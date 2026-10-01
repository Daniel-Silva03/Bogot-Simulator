"""
src/consulta/motor.py

La consulta de punta a punta (D17): de la pregunta que alguien escribe a la
respuesta que ve en la página. Une las tres piezas validadas:

    reformulación (`reformular.py`, 24 de 24)
        ├─ catálogo → el dato medido: población EPC 2022-2024, por ciudad, grupo y localidad
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
    *Cambio (30/09, población 2022-2024): sin educación.* Esa población no empareja
    por educación (2024 no la pregunta), así que la educación del agente no dice
    nada de su donante: un grupo por educación solo repetiría estrato y edad.

DI-CO6. **La página usa la población 2022-2024** (`poblacion_epc_olas.py`, lectura B
    mantenida por Daniel el 30/09). Una pregunta del catálogo la responden los
    agentes cuyo donante es de un año que se puede juntar para esa pregunta (DI-PO2);
    los demás no cuentan, ni como «no sabe». La respuesta dice de qué años sale y
    cuántos encuestados hay por localidad. El margen remuestrea los conglomerados de
    DI-PO3.

DI-CO7. **En una pregunta nueva, cada pregunta del puente se estandariza dentro de su
    año** (como `puente_localidades.py`, DI-PL3), con los pesos de los donantes; si
    no existe ese año, vale 0. Así un cambio de nivel entre años no se vuelve una
    diferencia entre grupos.

DI-CO8. **El prompt de la reformulación no cambia** (sigue diciendo «EPC 2023»): es el
    que se validó 24 de 24, y el catálogo que ve el modelo es el mismo (102 preguntas).

DI-CO9. **La respuesta dice a cuántas personas sintéticas consultó**: las que tienen
    donante (Sumapaz no) y, en una pregunta del catálogo, cuyo donante es de un año de
    esa pregunta. Hecho, en la prueba con el modelo real (30/09): la página decía
    siempre «20.000», también en una pregunta solo de 2023, donde responden 6.492.

DI-CO10. **Las etiquetas se muestran sin el número del código** («4. Alta» → «Alta»).
    Algunas etiquetas de la EPC lo traen; en la página se leía «4. alta o 5. muy
    alta». Solo cambia lo que se muestra: el catálogo y lo que ve el modelo no cambian.

DI-CO11. **Si el puente usa preguntas que no se hicieron todos los años, la respuesta lo
    dice** (Daniel, 30/09: «déjalo así y dilo en la respuesta»). Hecho: en la prueba
    con el modelo real, el puente del metro usó dos preguntas que solo existen en
    2023; para los encuestados de 2022 y 2024 valen 0 (DI-CO7). No se restringe al
    modelo (eso cambiaría su prompt y habría que validarlo otra vez). Cada pregunta
    del puente lleva sus años, y la respuesta trae qué fracción del peso del puente
    queda en cada año y un texto que lo explica.

DI-CO12. **El puente de la página usa el prompt v2 y muestra su fuerza**
    (`PUENTE_SIN_BASE_RESULTS.md`: P3 se cumple; P1 no, así que no se usa «sin base»).
    Si el v2 responde «sin base» o una respuesta rota, se pide el puente otra vez con el
    prompt de siempre (`puente.SISTEMA`) y se muestra como **base débil** (opción 1 que
    eligió Daniel el 1/10; no contradice la regla escrita). Es una llamada más, solo en
    esos casos. Si tampoco hay puente con el prompt de siempre, la pregunta no se responde,
    como antes.
"""

from __future__ import annotations

import json
import re
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

POBLACION = RAIZ / "data" / "processed" / "poblacion_epc2022_2024"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"
CACHE = RAIZ / "data" / "processed" / "consulta" / "cache.json"
N_BOOT = 200
SEMILLA = 20260930
SUMAPAZ = 20

GRUPOS = {
    "estrato": {"titulo": "Estrato", "orden": ["1 y 2", "3 y 4", "5 y 6"]},
    "edad": {"titulo": "Edad", "orden": ["18 a 25", "26 a 35", "36 a 45", "46 a 55", "56 o más"]},
    "sexo": {"titulo": "Sexo", "orden": ["Mujeres", "Hombres"]},
}
AVISO = ("Esto es una suposición, no una medición: muestra cómo respondería una población sintética "
         "construida con la Encuesta de Percepción Ciudadana 2022, 2023 y 2024 de Bogotá Cómo Vamos.")


#: DI-CO12: qué le dice la página a quien lee, según la fuerza del puente.
FUERZA_TEXTO = {
    "fuerte": "La encuesta midió el mismo tema que la pregunta: la suposición tiene una base fuerte.",
    "media": "La encuesta midió algo muy cercano a la pregunta: la suposición tiene una base media.",
    "debil": ("La encuesta no midió este tema; solo algo del área general. La suposición tiene una base "
              "débil: tómala con mucha cautela."),
}


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
    return {"estrato": est, "edad": edad, "sexo": sexo}                          # DI-CO5


def _etq(texto: str) -> str:
    """DI-CO10."""
    return re.sub(r"^\s*\d+\s*[.)-]\s*", "", str(texto)).strip()


def cobertura_puente(puente: list[dict], anios: list[int]) -> tuple[dict, Optional[str]]:
    """DI-CO11: (fracción del peso del puente que existe en cada año, texto o None)."""
    total = sum(p["peso"] for p in puente)
    frac = {a: sum(p["peso"] for p in puente if a in p["anios"]) / total for a in anios}
    parciales = [p for p in puente if set(anios) - set(p["anios"])]
    if not parciales:
        return {str(a): 1.0 for a in anios}, None
    cortos = [a for a in anios if frac[a] < 1]
    completos = [a for a in anios if frac[a] == 1]
    n, k = len(puente), len(parciales)
    texto = (f"{k} de las {n} preguntas en que se apoya no se hicieron todos los años. Para quien respondió "
             f"la encuesta en un año sin esa pregunta, cuenta como neutra: "
             + ", ".join(f"en {a} queda el {round(100 * frac[a])} % del peso" for a in cortos) + ". ")
    if completos:
        texto += f"Las diferencias entre grupos se apoyan más en quienes respondieron en {_texto_anios(completos)}."
    return {str(a): round(frac[a], 3) for a in anios}, texto


def cargar_donantes() -> pd.DataFrame:
    return pd.read_parquet(POBLACION / "donantes.parquet")


def cargar_anios() -> dict[str, list[int]]:
    cat = json.loads((POBLACION / "catalogo.json").read_text(encoding="utf-8"))["dentro"]
    return {f["variable"]: f["anios"] for f in cat}


def _texto_anios(a: list[int]) -> str:
    a = sorted(a)
    return str(a[0]) if len(a) == 1 else ", ".join(map(str, a[:-1])) + f" y {a[-1]}"


class _PuenteOlas:
    """DI-CO7: la interfaz de `puente.Datos` con cada pregunta estandarizada por año."""

    def __init__(self, x: dict[str, np.ndarray], catalogo: dict, w: np.ndarray, anio: np.ndarray):
        self.w = w
        self.z = {}
        for v, f in catalogo.items():
            z = np.zeros(len(w))
            ok = np.isin(x[v], f["escala"])
            for a in np.unique(anio):
                m = ok & (anio == a)
                if m.any():
                    mu = _wmean(x[v][m], w[m])
                    sd = np.sqrt(_wmean((x[v][m] - mu) ** 2, w[m])) or 1.0
                    z[m] = (x[v][m] - mu) / sd
            self.z[v] = z

    def puntaje(self, puente: list[dict]) -> np.ndarray:
        return pu.Datos.puntaje(self, puente)


class Motor:
    """Carga una sola vez la población y el catálogo; cada consulta es independiente."""

    def __init__(self, llamar: rf.Llamar, modelo: str, donante: Optional[pd.DataFrame] = None,
                 agentes: Optional[pd.DataFrame] = None, catalogo: Optional[dict] = None,
                 cache: Optional[e9.Cache] = None, anios: Optional[dict] = None):
        self.llamar, self.modelo = llamar, modelo
        self.catalogo = catalogo if catalogo is not None else rf.cargar_catalogo()
        self.donante = donante if donante is not None else cargar_donantes()
        self.anios = anios if anios is not None else cargar_anios()
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
        anio_d = (self.donante.anio.to_numpy() if "anio" in self.donante.columns
                  else np.full(len(self.donante), 2023))
        self.anio_agente = anio_d[self.idx]
        self.datos_puente = _PuenteOlas(self._x, self.catalogo, self.donante.peso.to_numpy(float), anio_d)   # DI-CO7
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
            r["escala"] = [_etq(f["etiquetas"][str(k)]) for k in f["escala"]]
        return r

    # ---------------------------------------------------------------- paso 2a
    def responder_catalogo(self, codigo: str) -> dict:
        if codigo not in self.catalogo:
            raise ConsultaError(f"{codigo} no está en el catálogo.")
        f = self.catalogo[codigo]
        esc = list(f["escala"])
        k = len(esc)
        x = self._x[codigo][self.idx]
        anios = sorted(self.anios.get(codigo, [2023]))
        cubre = np.isin(self.anio_agente, anios)                                  # DI-CO6
        ok = np.isin(x, esc) & cubre
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
        n_loc = int(np.median([v["encuestados"] for v in por_loc.values()]))
        grupos = {}
        for gname, etq in self.grupos.items():
            e = etq.to_numpy()
            grupos[gname] = [{"grupo": o, "media": round(_wmean(x[(e == o) & ok], self.peso[(e == o) & ok]), 3),
                              "alto": round(_wmean(np.isin(x[(e == o) & ok], alto).astype(float), self.peso[(e == o) & ok]), 3)}
                             for o in GRUPOS[gname]["orden"] if ((e == o) & ok).any()]
        return {"tipo": "catalogo", "suposicion": True, "aviso": AVISO, "codigo": codigo,
                "pregunta": f["pregunta"].strip(), "escala": [_etq(f["etiquetas"][str(c)]) for c in esc],
                "consultados": int(cubre.sum()),                                    # DI-CO9
                "ciudad": {"media": round(_wmean(x[ok], self.peso[ok]), 3), "distribucion": [round(d, 4) for d in dist],
                           "alto": round(sum(d for c, d in zip(esc, dist) if c in alto), 4),
                           "bajo": round(sum(d for c, d in zip(esc, dist) if c in bajo), 4),
                           "etiqueta_alto": (f"{_etq(f['etiquetas'][str(esc[-2])])} o {_etq(f['etiquetas'][str(esc[-1])]).lower()}"
                                             if k >= 4 else _etq(f["etiquetas"][str(esc[-1])])),
                           "respondieron": round(float(ok.sum() / cubre.sum()), 4)},
                "localidades": por_loc, "grupos": grupos, "anios": anios,
                "encuestados_mediana_localidad": n_loc,
                "fuente": (f"Dato medido en la EPC {_texto_anios(anios)}, reponderado por la población sintética; "
                           f"unas {n_loc} personas encuestadas por localidad.")}

    # ---------------------------------------------------------------- paso 2b
    def responder_nueva(self, pregunta: str, escala: list[str]) -> dict:
        if not pregunta or len(escala) != 5:
            raise ConsultaError("Una pregunta nueva necesita su texto y cinco etiquetas.")
        f_esc = {"variable": "NUEVA", "codigo": "NUEVA", "pregunta": pregunta.strip(), "escala": [1, 2, 3, 4, 5],
                 "etiquetas": {str(i + 1): e for i, e in enumerate(escala)}}
        from src.experiments import puente_sin_base as sb
        u = pu.prompt(f_esc, self.catalogo)
        texto, _ = e9.pedir(self.llamar, self.cache, self.modelo, pu.TEMPERATURA, sb.SISTEMA_V2, u, 0)
        r = sb.parsear_v2(texto, f_esc, self.catalogo)                          # DI-CO12
        reintento = r is None or r["sin_base"]
        if reintento:
            texto, _ = e9.pedir(self.llamar, self.cache, self.modelo, pu.TEMPERATURA, pu.SISTEMA, u, 0)
            r = pu.parsear(texto, f_esc, self.catalogo)                          # DI-CO3
            if r is not None:
                r = {**r, "fuerza": "debil"}
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
        puente = [{**p, "pregunta": self.catalogo[p["codigo"]]["pregunta"].strip(),
                   "anios": sorted(self.anios.get(p["codigo"], [2023]))} for p in r["preguntas"]]
        peso_anio, aviso_anios = cobertura_puente(puente, sorted(set(int(a) for a in self.anio_agente)))   # DI-CO11
        return {"tipo": "nueva", "suposicion": True, "aviso": AVISO, "pregunta": pregunta.strip(), "escala": escala,
                "consultados": len(self.agentes),                                   # DI-CO9
                "nivel_propuesto": round(r["nivel"], 2), "grupos": grupos, "puente": puente,
                "justificacion": r["justificacion"], "peso_por_anio": peso_anio, "aviso_anios": aviso_anios,
                "fuerza": r["fuerza"], "fuerza_texto": FUERZA_TEXTO[r["fuerza"]], "reintento": reintento,
                "sin_mapa": ("Para preguntas nuevas el simulador no dibuja localidades: en las pruebas con preguntas "
                             "conocidas ordenó bien a las personas, pero no a las localidades "
                             "(PUENTE_RESULTS.md, PUENTE_LOCALIDADES_RESULTS.md)."),
                "fuente": ("Puente: el modelo eligió preguntas medidas relacionadas; cada persona responde con sus "
                           "propias respuestas. El nivel lo propone el modelo y se puede cambiar.")}


# --------------------------------------------------------------------------
# Información general para el mapa (sin opinión)

def informacion_general(agentes: Optional[pd.DataFrame] = None, donante: Optional[pd.DataFrame] = None) -> dict:
    """Por localidad: nombre, adultos (proyección oficial), estrato medio de la población y
    cuántas personas de la EPC 2022-2024 viven ahí. Nada de opinión."""
    ag = agentes if agentes is not None else pd.read_parquet(POBLACION / "agentes.parquet")
    don = donante if donante is not None else cargar_donantes()
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
                           "fuerza": "media", "sin_base": False, "nivel": 3.2, "justificacion": "simulado"})
    return llamar, e9.MODELO_SIMULADO
