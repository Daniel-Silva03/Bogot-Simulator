"""
src/consulta/motor.py

La consulta de punta a punta (D17): de la pregunta que alguien escribe a la
respuesta que ve en la página. Une las tres piezas validadas:

    reformulación (`reformular.py`, 24 de 24)
        ├─ catálogo → el dato medido: población EPC 2023, por ciudad, grupo y localidad
        ├─ nueva    → el puente (`puente.py`, lectura B): diferencias entre grupos
        │             y un nivel propuesto, editable; SIN mapa por localidad
        └─ fuera    → por qué no, y una alternativa que vuelve a pasar por aquí

Todo lo que devuelve lleva `suposicion: True` y el texto que la página muestra.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-CO1. **Una pregunta del catálogo se responde con los agentes, y su margen sale de
    los encuestados.** La media de una localidad es la de sus 1.000 agentes (que
    pesan a los encuestados según la composición del receptor); el margen del 95 %
    se obtiene remuestreando manzanas de la EPC dentro de la localidad (DI-PE5) y
    recalculando esa misma media de agentes. Así el margen es el de la encuesta, no
    el de los 20.000 agentes, que son copias.

DI-CO2. **Una pregunta nueva no tiene mapa** (`PUENTE_RESULTS.md`, lectura B: el
    puente ordena personas, no localidades). Se devuelven diferencias entre grupos
    en desviaciones estándar del puntaje del puente («más / menos de acuerdo que el
    promedio»), no porcentajes: el puente ordena, no fija cuántos están de acuerdo.
    El nivel de la ciudad es el que propone el modelo, y la página lo deja editar.

DI-CO3. **En la página el puente usa el catálogo completo (102 preguntas)**, no el de
    la validación (91): ya no hay preguntas escondidas. Se valida y se puntúa igual.

DI-CO4. **Una alternativa sugerida para una pregunta fuera de alcance no se responde
    directamente** (`REFORMULACION_RESULTS.md` §3): la página la manda otra vez a
    `reformular`, como pregunta nueva.

DI-CO5. **Grupos:** estrato en tres niveles (1-2, 3-4, 5-6; el 0 va con 1-2), los
    cinco tramos de edad, sexo y los cuatro niveles de educación de DI-PE1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import reformular as rf                  # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                  # noqa: E402

POBLACION = RAIZ / "data" / "processed" / "poblacion_epc2023"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"
CACHE = RAIZ / "data" / "processed" / "consulta" / "cache.json"
N_BOOT = 200
SEMILLA = 20260930
SUMAPAZ = 20

GRUPOS = {
    "estrato": {"titulo": "Estrato", "orden": ["1 y 2", "3 y 4", "5 y 6"]},
    "edad": {"titulo": "Edad", "orden": ["18 a 25", "26 a 35", "36 a 45", "46 a 55", "56 o más"]},
    "sexo": {"titulo": "Sexo", "orden": ["Mujeres", "Hombres"]},
    "educacion": {"titulo": "Educación", "orden": ["Primaria o menos", "Secundaria o media",
                                                   "Técnica o tecnológica", "Universitaria o posgrado"]},
}
AVISO = ("Esto es una suposición, no una medición: muestra cómo respondería una población sintética "
         "construida con la Encuesta de Percepción Ciudadana 2023 de Bogotá Cómo Vamos.")


class ConsultaError(RuntimeError):
    """La consulta no se puede responder como está especificada."""


def _wmean(x, w):
    s = np.sum(w)
    return float(np.sum(x * w) / s) if s > 0 else float("nan")


def _grupos(ag: pd.DataFrame) -> dict[str, pd.Series]:
    """DI-CO5: la etiqueta de grupo de cada agente."""
    est = ag.estrato.map(lambda e: "1 y 2" if e <= 2 else ("3 y 4" if e <= 4 else "5 y 6"))
    edad = ag.edad_tramo.map(dict(enumerate(GRUPOS["edad"]["orden"])))
    sexo = ag.sexo.map({"F": "Mujeres", "M": "Hombres"})
    edu = ag.educ_h.map(dict(enumerate(GRUPOS["educacion"]["orden"])))
    return {"estrato": est, "edad": edad, "sexo": sexo, "educacion": edu}


class Motor:
    """Carga una sola vez la población y el catálogo; cada consulta es independiente."""

    def __init__(self, llamar: rf.Llamar, modelo: str, donante: Optional[pd.DataFrame] = None,
                 agentes: Optional[pd.DataFrame] = None, catalogo: Optional[dict] = None,
                 cache: Optional[e9.Cache] = None):
        from src.population import poblacion_epc as pe
        self.llamar, self.modelo = llamar, modelo
        self.catalogo = catalogo if catalogo is not None else rf.cargar_catalogo()
        self.donante = donante if donante is not None else pe.cargar_donante()
        ag = agentes if agentes is not None else pd.read_parquet(POBLACION / "agentes.parquet")
        self.agentes = ag[ag.donante_id.notna()].reset_index(drop=True)
        self.idx = self.agentes.donante_id.astype(int).to_numpy()
        self.peso = self.agentes.peso.to_numpy(float)
        self.loc = self.agentes.cod_loc.to_numpy()
        self.grupos = _grupos(self.agentes)
        self.cache = cache if cache is not None else e9.Cache(CACHE)
        col = {c.upper(): c for c in self.donante.columns}
        self._x = {v: pd.to_numeric(self.donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
                   for v, f in self.catalogo.items()}
        self.datos_puente = pu.Datos(self.donante, self.catalogo, {})
        self._conglo = {}
        loc_d = self.donante.cod_loc.to_numpy()
        for l in sorted(set(self.loc)):
            m = loc_d == l
            self._conglo[int(l)] = (np.flatnonzero(m), pd.factorize(self.donante.conglomerado.to_numpy()[m])[0])

    # ---------------------------------------------------------------- paso 1
    def reformular(self, pregunta: str) -> dict:
        if not pregunta or not pregunta.strip():
            raise ConsultaError("La pregunta está vacía.")
        r, _ = rf.reformular(pregunta[:500], self.catalogo, self.llamar, self.cache, self.modelo)
        if r is None:
            return {"alcance": "invalida", "mensaje": "No pude reformular esta pregunta. Prueba a escribirla de otra forma."}
        if r["alcance"] == "catalogo":
            f = self.catalogo[r["codigo"]]
            r["pregunta_catalogo"] = f["pregunta"].strip()
            r["escala"] = [f["etiquetas"][str(k)] for k in f["escala"]]
        return r

    # ---------------------------------------------------------------- paso 2a
    def responder_catalogo(self, codigo: str) -> dict:
        if codigo not in self.catalogo:
            raise ConsultaError(f"{codigo} no está en el catálogo.")
        f = self.catalogo[codigo]
        esc = list(f["escala"])
        k = len(esc)
        x = self._x[codigo][self.idx]
        ok = np.isin(x, esc)
        w = self.peso * ok
        dist = [_wmean((x == c).astype(float), w) for c in esc]
        alto = [c for c in esc if c > (k + 1) / 2]           # la mitad superior de la escala
        bajo = [c for c in esc if c < (k + 1) / 2]
        rng = np.random.default_rng(SEMILLA)
        por_loc = {}
        xd = self._x[codigo]
        for l, (filas, g) in self._conglo.items():
            m = (self.loc == l) & ok
            if not m.any():
                continue
            # DI-CO1: cuántos agentes heredan a cada encuestado de la localidad
            cuenta = np.bincount(np.searchsorted(filas, self.idx[m]), minlength=len(filas)).astype(float)
            cuenta *= np.isin(xd[filas], esc)                   # «no sabe» no entra a la media
            vals = np.nan_to_num(xd[filas])
            media = float(np.sum(cuenta * vals) / cuenta.sum())
            nc = g.max() + 1
            boot = []
            for _ in range(N_BOOT):
                mult = np.bincount(rng.integers(0, nc, nc), minlength=nc)[g]
                c = cuenta * mult
                if c.sum() > 0:
                    boot.append(np.sum(c * vals) / c.sum())
            validos_d = np.isin(xd[filas], esc)
            por_loc[str(int(l))] = {
                "media": round(media, 3),
                "margen": [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)],
                "alto": round(_wmean(np.isin(x[m], alto).astype(float), self.peso[m]), 3),
                "encuestados": int(validos_d.sum())}
        grupos = {}
        for gname, etq in self.grupos.items():
            e = etq.to_numpy()
            grupos[gname] = [{"grupo": o, "media": round(_wmean(x[(e == o) & ok], self.peso[(e == o) & ok]), 3),
                              "alto": round(_wmean(np.isin(x[(e == o) & ok], alto).astype(float), self.peso[(e == o) & ok]), 3)}
                             for o in GRUPOS[gname]["orden"] if ((e == o) & ok).any()]
        return {"tipo": "catalogo", "suposicion": True, "aviso": AVISO, "codigo": codigo,
                "pregunta": f["pregunta"].strip(), "escala": [f["etiquetas"][str(c)] for c in esc],
                "ciudad": {"media": round(_wmean(x[ok], self.peso[ok]), 3), "distribucion": [round(d, 4) for d in dist],
                           "alto": round(sum(d for c, d in zip(esc, dist) if c in alto), 4),
                           "bajo": round(sum(d for c, d in zip(esc, dist) if c in bajo), 4),
                           "etiqueta_alto": f"{f['etiquetas'][str(esc[-2])]} o {f['etiquetas'][str(esc[-1])].lower()}" if k >= 4 else f["etiquetas"][str(esc[-1])],
                           "respondieron": round(float(ok.mean()), 4)},
                "localidades": por_loc, "grupos": grupos,
                "fuente": "Dato medido en la EPC 2023, reponderado por la población sintética (DI-CO1)."}

    # ---------------------------------------------------------------- paso 2b
    def responder_nueva(self, pregunta: str, escala: list[str]) -> dict:
        if not pregunta or len(escala) != 5:
            raise ConsultaError("Una pregunta nueva necesita su texto y cinco etiquetas.")
        f_esc = {"variable": "NUEVA", "codigo": "NUEVA", "pregunta": pregunta.strip(), "escala": [1, 2, 3, 4, 5],
                 "etiquetas": {str(i + 1): e for i, e in enumerate(escala)}}
        texto, _ = e9.pedir(self.llamar, self.cache, self.modelo, pu.TEMPERATURA, pu.SISTEMA,
                            pu.prompt(f_esc, self.catalogo), 0)
        r = pu.parsear(texto, f_esc, self.catalogo)                              # DI-CO3
        if r is None:
            return {"tipo": "invalida", "mensaje": "No pude construir el puente para esta pregunta. Prueba a reformularla."}
        s = self.datos_puente.puntaje(r["preguntas"])[self.idx]
        m, sd = _wmean(s, self.peso), np.sqrt(_wmean((s - _wmean(s, self.peso)) ** 2, self.peso)) or 1.0
        z = (s - m) / sd
        grupos = {}
        for gname, etq in self.grupos.items():
            e = etq.to_numpy()
            grupos[gname] = [{"grupo": o, "indice": round(_wmean(z[e == o], self.peso[e == o]), 3)}
                             for o in GRUPOS[gname]["orden"] if (e == o).any()]
        puente = [{**p, "pregunta": self.catalogo[p["codigo"]]["pregunta"].strip()} for p in r["preguntas"]]
        return {"tipo": "nueva", "suposicion": True, "aviso": AVISO, "pregunta": pregunta.strip(), "escala": escala,
                "nivel_propuesto": round(r["nivel"], 2), "grupos": grupos, "puente": puente,
                "justificacion": r["justificacion"],
                "sin_mapa": ("Para preguntas nuevas el simulador no dibuja localidades: en la prueba con preguntas "
                             "conocidas ordenó bien a las personas, pero no a las localidades (PUENTE_RESULTS.md)."),
                "fuente": ("Puente: el modelo eligió preguntas medidas relacionadas; cada persona responde con sus "
                           "propias respuestas. El nivel lo propone el modelo y se puede cambiar.")}


# --------------------------------------------------------------------------
# Información general para el mapa (sin opinión)

def informacion_general(agentes: Optional[pd.DataFrame] = None, donante: Optional[pd.DataFrame] = None) -> dict:
    """Por localidad: nombre, adultos (proyección oficial), estrato medio de la población y
    cuántas personas de la EPC 2023 viven ahí. Nada de opinión."""
    from src.population import poblacion_epc as pe
    ag = agentes if agentes is not None else pd.read_parquet(POBLACION / "agentes.parquet")
    don = donante if donante is not None else pe.cargar_donante()
    m = pd.read_csv(MARGINAL).set_index("COD_LOC")
    enc = don.cod_loc.value_counts()
    out = {}
    for c, fila in m.iterrows():
        a = ag[ag.cod_loc == c]
        out[str(int(c))] = {"nombre": fila.localidad, "adultos": int(fila.poblacion),
                            "estrato_medio": round(float(a.estrato.mean()), 2) if len(a) else None,
                            "encuestados": int(enc.get(c, 0))}
    return out


def cliente(simulado: bool = False):
    """(llamar, modelo). El simulado contesta la reformulación y el puente sin gasto."""
    if not simulado:
        return e9.cliente_real(), rf.MODELO
    cat = rf.cargar_catalogo()
    ref = rf.modelo_simulado(cat)
    cods = list(cat)

    def llamar(modelo, sistema, usuario, temp):
        if sistema == rf.SISTEMA:
            return ref(modelo, sistema, usuario, temp)
        return json.dumps({"preguntas": [{"codigo": cods[0], "sentido": "+", "peso": 2},
                                         {"codigo": cods[1], "sentido": "-", "peso": 1}],
                           "nivel": 3.2, "justificacion": "simulado"})
    return llamar, e9.MODELO_SIMULADO
