"""
src/consulta/agentes.py

D22: estimar una pregunta nueva política o institucional con agentes. 200 encuestados reales de la EPC 2025, cada uno con sus
40 respuestas del catálogo y sus datos demográficos, responden la pregunta con la probabilidad de cada opción. La cifra de
Bogotá y la de cada grupo salen de esas probabilidades, ponderadas con `Factor1`.

Método probado en `PERSONAS_POLITICA_RESULTS.md` y `AGENTES_2026_RESULTS.md`. Las dos validaciones fuera de muestra de D22 no
pasaron (`VALIDACION_AGENTES_D22_RESULTS.md`, `ACTUALIDAD_EPC_RESULTS.md`); desde el 19/10/2026 se usa con el modelo real como
experimento declarado, por decisión de Daniel (D22, enmienda; DI-AG-P6).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-AG-P1. **El panel es fijo:** 200 encuestados de la EPC 2025 sorteados con la semilla 20261018 entre los de las localidades
    1-19. Es una muestra, como las de las pruebas; el mismo panel para toda pregunta, para que dos preguntas se puedan comparar.
DI-AG-P2. **Las llamadas van en paralelo** (`PARALELO` hilos) con `experimento9.pedir`. La caché tiene candado (1/10/2026) y
    reintenta el reemplazo del archivo en Windows (14/10/2026).
DI-AG-P3. **El rango es ±12,6:** el cuantil 80 % del error de los agentes en las 17 preguntas políticas probadas (las 10 de
    `PERSONAS_POLITICA`, perfil B, y las 7 del CNC de `AGENTES_2026`, Luna; error medio 8,2). Se midió en las mismas pruebas que
    justifican D22, así que no es una validación fuera de muestra: esa es la condición 1 de D22.
DI-AG-P4. **Lo favorable** son las opciones 4 y 5 de la escala de la reformulación, como en la estimación de hoy (DI-CO22).
DI-AG-P5. **Los grupos** son los de la página (estrato 1-2 / 3-4 / 5-6, los cinco tramos de edad y sexo), con los datos del
    encuestado de 2025. Con 200 agentes, un grupo puede tener 20 o 30 personas: se muestra cuántos hay en cada uno.
DI-AG-P6. **El error, a la vista** (19/10/2026). Hecho: en las dos pruebas con preguntas que no se habían usado, el error medio
    fue de 12,2 (`VALIDACION_AGENTES_D22`) y de 10,1 a 10,9 (`ACTUALIDAD_EPC`), y repetir el último dato medido acertó más
    (7,7 en la segunda; también en `GALAN_ACTUAL`). Decisión: `ERROR_MEDIDO` va junto a la cifra, con esas palabras. El rango
    de ±12,6 queda: es parecido a ese error.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]

SEMILLA = 20261018
N = 200
PARALELO = 16
H = 12.6                                                        # DI-AG-P3
MODELO = "openai/gpt-6-luna"
TEMPERATURA = 1.0
CACHE = RAIZ / "data" / "processed" / "consulta" / "cache_agentes.json"
TEXTO = ("Estimado con {n} bogotanos reales que respondieron la Encuesta de Percepción Ciudadana 2025: un modelo de lenguaje "
         "responde como cada uno, según sus otras respuestas. Es una suposición, no una medición; el rango es de ±{h:.0f}.")
#: DI-AG-P6
ERROR_MEDIDO = ("En las pruebas con preguntas políticas que no se habían usado, este método se equivocó en promedio entre 10 y "
                "12 puntos, y repetir el último dato medido acertó más. Está a prueba: no lo leas como un pronóstico.")


class Agentes:
    """El panel de 200 (DI-AG-P1), con sus perfiles listos."""

    def __init__(self, datos=None):
        from src.experiments import personas_con_encuesta as pc
        from src.experiments import personas_politica as pq
        self.datos = datos if datos is not None else pc.datos_2025()
        base, d, _ = self.datos
        elegibles = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy())
        self.personas = np.sort(np.random.default_rng(SEMILLA).choice(elegibles, min(N, len(elegibles)), replace=False))
        self.perfiles = [pq.perfil(i, self.datos, [], {}, con_vida=False) for i in self.personas]
        self.peso = base.peso.to_numpy(float)[self.personas]
        self.grupos = self._grupos(d.iloc[self.personas])

    @staticmethod
    def _grupos(d: pd.DataFrame) -> dict[str, np.ndarray]:
        """DI-AG-P5."""
        from src.consulta import motor as mo
        from src.population import poblacion_epc as pe
        num = lambda c: pd.to_numeric(d[c], errors="coerce")                       # noqa: E731
        falso = pd.DataFrame({"estrato": num("DMO_4_1").fillna(99).to_numpy(),
                              "edad_tramo": pe.tramo_edad(num("DMO_3_1")).to_numpy(),
                              "sexo": num("DMO_1").map({1: "M", 2: "F"}).to_numpy()})
        g = mo._grupos(falso)
        return {k: v.to_numpy() for k, v in g.items()}

    def _usuario(self, perfil: str, pregunta: str, escala: list[str]) -> str:
        ops = "; ".join(f"{i}={e}" for i, e in enumerate(escala, 1)) + "; 9=No sabe"
        return f"QUIÉN ES:\n{perfil}\n\nPREGUNTAS NUEVAS:\nE1. {pregunta.strip()} Opciones: {ops}"

    def estimar(self, pregunta: str, escala: list[str], llamar, cache, modelo: str = MODELO) -> dict:
        """La cifra de Bogotá, su rango, la distribución y los grupos."""
        from src.experiments import experimento9 as e9
        from src.experiments import personas_pulidas as pp
        from src.consulta import motor as mo
        if len(escala) != 5:
            raise ValueError("La estimación con agentes necesita una escala de cinco opciones.")
        sistema = pp.BASE + pp.SALIDA_PROB
        esc = [{"clave": "E1", "validos": [1, 2, 3, 4, 5]}]
        t0 = time.time()

        def uno(perfil):
            texto, _ = e9.pedir(llamar, cache, modelo, TEMPERATURA, sistema, self._usuario(perfil, pregunta, escala), 0)
            return pp.leer_prob(texto, esc)["E1"]
        with ThreadPoolExecutor(max_workers=PARALELO) as ex:                       # DI-AG-P2
            probs = list(ex.map(uno, self.perfiles))
        ok = np.array([q is not None for q in probs])
        if not ok.any():
            return {"tipo": "invalida", "mensaje": "Los agentes no pudieron responder esta pregunta. Prueba a reformularla."}
        w = self.peso
        pfav = np.array([(q.get(4, 0) + q.get(5, 0)) if q else np.nan for q in probs])        # DI-AG-P4
        dist = [float(sum(w[j] * probs[j].get(c, 0) for j in np.flatnonzero(ok)) / w[ok].sum()) for c in range(1, 6)]

        def media(m):
            m = m & ok
            return round(float(np.sum(w[m] * pfav[m]) / np.sum(w[m])), 4) if m.any() else None
        pct = 100 * media(np.ones(len(w), bool))
        lo, hi = max(0.0, pct - H), min(100.0, pct + H)
        llamada = "sí" if lo > 50 else ("no" if hi < 50 else "dividida")
        grupos = {g: [{"grupo": o, "alto": media(etq == o), "n": int(((etq == o) & ok).sum())}
                      for o in mo.GRUPOS[g]["orden"] if ((etq == o) & ok).any()]
                  for g, etq in self.grupos.items()}
        return {"tipo": "agentes", "suposicion": True, "pregunta": pregunta.strip(), "escala": escala,
                "porcentaje": round(pct, 1), "rango": [round(lo, 1), round(hi, 1)], "llamada": llamada,
                "titulo": mo.LLAMADA_TITULO[llamada], "distribucion": [round(x, 4) for x in dist], "grupos": grupos,
                "respondieron": int(ok.sum()), "agentes": len(self.perfiles), "segundos": round(time.time() - t0, 1),
                "texto": TEXTO.format(n=int(ok.sum()), h=H), "error_medido": ERROR_MEDIDO,
                "sin_mapa": ("Con 200 agentes quedan unos 11 por localidad: no alcanza para un mapa."),
                "experimental": True}


def cliente_simulado():
    """Probabilidades al azar, sin gasto: para mirar la página."""
    rng = np.random.default_rng(0)

    def llamar(modelo, sistema, usuario, temp):
        return json.dumps({"E1": {str(c): float(x) for c, x in zip(range(1, 6), rng.dirichlet(np.ones(5)))}})
    return llamar
