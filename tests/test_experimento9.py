"""
tests/test_experimento9.py

Pruebas del Experimento 9 con modelos simulados, **sin red**: la red queda
bloqueada al importar este archivo, y una prueba que intente usarla falla.
Se ejecuta directo:  python tests/test_experimento9.py
"""

import json
import re
import shutil
import socket
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np


# --- la red queda cortada antes de importar nada del proyecto ---------------

class RedBloqueada(RuntimeError):
    pass


INTENTOS_DE_RED = []


def _sin_red(*a, **k):
    INTENTOS_DE_RED.append(a[:1])
    raise RedBloqueada("Las pruebas del Experimento 9 no pueden usar la red.")


urllib.request.urlopen = _sin_red
socket.socket.connect = _sin_red
socket.create_connection = _sin_red

from src.experiments import experimento9 as e9                        # noqa: E402
from src.experiments.metrics import wasserstein1                      # noqa: E402

FALLOS = []
DATOS_REALES = (Path(e9.RAIZ) / "data" / "raw" / "ecp").exists()


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# --- estados sintéticos -----------------------------------------------------

def _normal_en(grilla, media, sd):
    p = np.exp(-0.5 * ((grilla - media) / sd) ** 2)
    return p / p.sum()


#: Medias inventadas, con cambios de varios tamaños y los dos signos.
MEDIAS = {("ECP", 2013): 2.91, ("ECP", 2017): 2.63, ("ECP", 2019): 2.47,
          ("ECP", 2021): 2.28, ("ECP", 2023): 2.52,
          ("EPC", 2014): 3.05, ("EPC", 2015): 2.64, ("EPC", 2017): 2.83,
          ("EPC", 2018): 3.12, ("EPC", 2019): 3.27, ("EPC", 2022): 2.71,
          ("EPC", 2023): 2.69, ("EPC", 2024): 3.02, ("EPC", 2025): 3.38}


def estados_sinteticos():
    salida = {}
    for (serie, anio), m in MEDIAS.items():
        g = e9.SERIES[serie]["grilla"]
        sd = 0.55 + 0.02 * (anio % 7) if serie == "ECP" else 1.0 + 0.03 * (anio % 5)
        salida[(serie, anio)] = e9.Estado(serie, anio, g, _normal_en(g, m, sd), 1000)
    return salida


ESTADOS = estados_sinteticos()
#: Pisos fijos: las pruebas de la lógica no necesitan sortear 200 réplicas.
PISOS = {t.clave: 0.05 for t in e9.TRANSICIONES}


# --- modelos simulados ------------------------------------------------------

def _transicion_de(usuario):
    anios = re.search(r"Periodo: de (\d{4}) a (\d{4})", usuario)
    serie = "ECP" if "Cultura Política" in usuario else "EPC"
    return next(t for t in e9.TRANSICIONES if t.serie == serie
                and (t.inicio, t.fin) == (int(anios[1]), int(anios[2])))


def _sonda_de(usuario):
    anio = int(re.search(r"(\d{4})", usuario)[1])
    serie = "ECP" if "Cultura Política" in usuario else "EPC"
    return next(t for t in e9.TRANSICIONES if t.serie == serie and t.fin == anio)


def modelo_que(propone, ancho=1.0, sonda_error=0.5, llamadas=None):
    """Un modelo que propone `propone(t)` y en la sonda se equivoca por `sonda_error`."""
    def llamar(modelo, sistema, usuario, temp):
        if llamadas is not None:
            llamadas.append(usuario)
        if sistema == e9.SISTEMA_SONDA:
            t = _sonda_de(usuario)
            if "porcentaje" in usuario:
                return json.dumps({"porcentaje": 100 * ESTADOS[("EPC", t.fin)].proporcion_4_5() + 50})
            return json.dumps({"media": ESTADOS[(t.serie, t.fin)].media + sonda_error})
        t = _transicion_de(usuario)
        dn, dsd = propone(t)
        return json.dumps({"delta_nivel": dn, "intervalo_nivel": [dn - ancho, dn + ancho],
                           "delta_dispersion": dsd,
                           "intervalo_dispersion": [dsd - ancho, dsd + ancho],
                           "justificacion": "prueba"})
    return llamar


ORACULO = lambda t: e9.cambio_observado(t, ESTADOS)                  # noqa: E731
CERO = lambda t: (0.0, 0.0)                                          # noqa: E731


def _tendencia(t):
    return e9.baselines(ESTADOS)["tendencia"].get(t.clave, (0.0, 0.0))


def correr(llamar, brazos=("A", "B"), carpeta=None):
    """Sonda + brazos + evaluación completos, sobre los estados sintéticos."""
    carpeta = Path(carpeta or tempfile.mkdtemp())
    cache = e9.Cache(carpeta / "cache.json")
    sonda = {t.clave: e9.sondear(t, ESTADOS, llamar, cache, "m") for t in e9.TRANSICIONES}
    hechos = {t.clave: e9.hechos_del_dossier(t.clave) for t in e9.TRANSICIONES}
    agregados = {b: {t.clave: e9.agregar(e9.recolectar_brazo(
                    t, b, ESTADOS, llamar, cache, "m", hechos[t.clave])["propuestas"])
                     for t in e9.TRANSICIONES} for b in brazos}
    return e9.evaluar(ESTADOS, agregados, sonda, PISOS), sonda


def _por(filas, fuente):
    return {f["clave"]: f for f in filas if f["fuente"] == fuente}


# --- dossiers (DI-E3) -------------------------------------------------------

def test_los_doce_dossiers_pasan_la_huella_y_traen_15_hechos():
    for t in e9.TRANSICIONES:
        h = e9.hechos_del_dossier(t.clave)
        n = len(re.findall(r"^\d+\. \*\*", h, re.M))
        assert n == 15, f"{t.clave}: {n} hechos"
        assert "Fuente:" not in h and "Selección" not in h, "se coló el encabezado"


def test_un_dossier_alterado_detiene_todo():
    tmp = Path(tempfile.mkdtemp())
    try:
        shutil.copy(e9.DOSSIERS / "HUELLAS.txt", tmp)
        texto = (e9.DOSSIERS / "EPC_2018_2019.md").read_text(encoding="utf-8")
        (tmp / "EPC_2018_2019.md").write_text(texto.replace("Radiohead", "Radiohed"),
                                              encoding="utf-8")
        try:
            e9.hechos_del_dossier("EPC_2018_2019", tmp)
        except e9.DossierAlterado:
            return
        raise AssertionError("un dossier editado pasó la verificación")
    finally:
        shutil.rmtree(tmp)


def test_la_huella_no_depende_del_final_de_linea():
    assert e9.huella("a\nb\n") == e9.huella("a\r\nb\r\n")


# --- mensajes (DI-E4) -------------------------------------------------------

def test_el_mensaje_no_depende_del_anio_final():
    """Si el estado final cambia, el mensaje tiene que ser idéntico."""
    for t in e9.TRANSICIONES:
        h = e9.hechos_del_dossier(t.clave)
        otros = dict(ESTADOS)
        g = ESTADOS[(t.serie, t.fin)].grilla
        otros[(t.serie, t.fin)] = e9.Estado(t.serie, t.fin, g, _normal_en(g, 4.4, 0.3))
        for b in ("A", "B"):
            assert e9.mensaje_brazo(t, ESTADOS, b, h) == e9.mensaje_brazo(t, otros, b, h), \
                f"{t.clave} brazo {b} depende del año final"


def test_el_mensaje_no_trae_las_cifras_finales():
    for t in e9.TRANSICIONES:
        fin = ESTADOS[(t.serie, t.fin)]
        _, u = e9.mensaje_brazo(t, ESTADOS, "B", e9.hechos_del_dossier(t.clave))
        assert f"Media: {fin.media:.2f}" not in u
        assert f"Desviación estándar: {fin.sd:.2f}" not in u


def test_el_brazo_a_no_lleva_dossier_y_el_b_si():
    t = e9.TRANSICIONES[7]
    h = e9.hechos_del_dossier(t.clave)
    _, a = e9.mensaje_brazo(t, ESTADOS, "A")
    _, b = e9.mensaje_brazo(t, ESTADOS, "B", h)
    primer_hecho = h.splitlines()[0]
    assert primer_hecho not in a and "Hechos del periodo" not in a
    assert primer_hecho in b
    assert b.replace("\nHechos del periodo (cronologías de Wikipedia en español):\n" + h + "\n", "") == a


def test_el_mensaje_trae_lo_que_pide_el_31():
    t = e9.Transicion("EPC", 2018, 2019)
    _, u = e9.mensaje_brazo(t, ESTADOS, "A")
    for pedazo in (f"Media: {ESTADOS[('EPC', 2018)].media:.2f}", "Distribución por categoría", "Enrique Peñalosa",
                   "Juan Manuel Santos", "Iván Duque", "de 2018 a 2019", "delta_nivel"):
        assert pedazo in u, pedazo
    _, u = e9.mensaje_brazo(e9.TRANSICIONES[0], ESTADOS, "A")
    assert "Quintiles del índice" in u and "Presidencia de la República" in u


def test_el_brazo_b_sin_hechos_no_se_arma():
    try:
        e9.mensaje_brazo(e9.TRANSICIONES[0], ESTADOS, "B")
    except e9.Experimento9Error:
        return
    raise AssertionError("se armó un brazo B sin dossier")


# --- lectura de respuestas (DI-E5) ------------------------------------------

BUENA = ('{"delta_nivel": -0.2, "intervalo_nivel": [-0.4, 0.0], "delta_dispersion": 0.05,'
         ' "intervalo_dispersion": [-0.05, 0.15], "justificacion": "x"}')


def test_lee_json_limpio_y_con_ruido_alrededor():
    for texto in (BUENA, "Claro:\n```json\n" + BUENA + "\n```\nListo.",):
        p = e9.parsear_propuesta(texto)
        assert p and p["delta_nivel"] == -0.2 and p["intervalo_nivel"] == [-0.4, 0.0]


def test_acepta_decimales_con_coma_y_ordena_intervalos_al_reves():
    p = e9.parsear_propuesta('{"delta_nivel": "-0,2", "intervalo_nivel": [0.0, -0.4],'
                             ' "delta_dispersion": 0, "intervalo_dispersion": [0.1, -0.1]}')
    assert p["delta_nivel"] == -0.2 and p["intervalo_nivel"] == [-0.4, 0.0]
    assert p["intervalo_dispersion"] == [-0.1, 0.1]


def test_rechaza_lo_que_no_sirve():
    for malo in (None, "", "no sé", "{roto", '{"delta_nivel": 0.1}',
                 BUENA.replace("[-0.4, 0.0]", "[-0.4]"),
                 BUENA.replace("-0.2", '"mucho"'),
                 BUENA.replace("-0.2", "true"),
                 BUENA.replace("-0.2", "NaN")):
        assert e9.parsear_propuesta(malo) is None, f"aceptó {malo!r}"


def test_lee_la_sonda():
    assert e9.parsear_sonda('{"media": 2.45}', "media") == 2.45
    assert e9.parsear_sonda("La media fue {\"media\": \"2,5\"}", "media") == 2.5
    assert e9.parsear_sonda('{"otra": 1}', "media") is None


# --- caché y recolección (DI-E2) --------------------------------------------

def test_la_segunda_corrida_no_llama_nada():
    tmp = Path(tempfile.mkdtemp())
    try:
        llamadas = []
        m = modelo_que(ORACULO, llamadas=llamadas)
        t = e9.TRANSICIONES[4]
        r1 = e9.recolectar_brazo(t, "A", ESTADOS, m, e9.Cache(tmp / "c.json"), "m")
        n = len(llamadas)
        assert n == e9.REPETICIONES and r1["llamadas_nuevas"] == n
        r2 = e9.recolectar_brazo(t, "A", ESTADOS, m, e9.Cache(tmp / "c.json"), "m")
        assert len(llamadas) == n and r2["llamadas_nuevas"] == 0
        assert r1["propuestas"] == r2["propuestas"]
    finally:
        shutil.rmtree(tmp)


def test_la_clave_distingue_repeticion_modelo_y_mensaje():
    base = e9.Cache.clave("m", 0.7, "s", "u", 0)
    assert len({base, e9.Cache.clave("m", 0.7, "s", "u", 1), e9.Cache.clave("n", 0.7, "s", "u", 0),
                e9.Cache.clave("m", 0.0, "s", "u", 0), e9.Cache.clave("m", 0.7, "s", "v", 0)}) == 5


def test_respuestas_malas_se_reintentan_sin_tumbar_la_corrida():
    n = {"i": 0}

    def a_veces(modelo, sistema, usuario, temp):
        n["i"] += 1
        if n["i"] % 3 == 0:
            raise ConnectionResetError("corte")
        if n["i"] % 3 == 1:
            return "no tengo idea"
        return BUENA
    r = e9.recolectar_brazo(e9.TRANSICIONES[0], "A", ESTADOS, a_veces,
                            e9.Cache(Path(tempfile.mkdtemp()) / "c.json"), "m")
    # una de cada tres sirve: 7 válidas y 13 fallos, y se detiene en el tope de 20
    assert len(r["propuestas"]) == 7 and len(r["fallos"]) == 13
    assert any("ConnectionResetError" in f["motivo"] for f in r["fallos"])


def test_un_error_de_red_no_se_guarda_en_la_cache():
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")

    def cae(*a):
        raise TimeoutError("lento")
    e9.recolectar_brazo(e9.TRANSICIONES[0], "A", ESTADOS, cae, cache, "m")
    assert cache.datos == {}


def test_la_mediana_y_el_intervalo_del_brazo():
    props = [{"delta_nivel": d, "delta_dispersion": d / 10,
              "intervalo_nivel": [d - 1, d + 2], "intervalo_dispersion": [0, 1]}
             for d in (0.1, 0.5, 0.2, 0.9, 0.3)]
    a = e9.agregar(props)
    assert a["delta_nivel"] == 0.3 and abs(a["delta_dispersion"] - 0.03) < 1e-12
    assert a["intervalo_nivel"] == [-0.7, 2.3] and a["n_validas"] == 5
    assert e9.agregar([]) is None


# --- ladeo y métricas -------------------------------------------------------

def test_sin_cambio_devuelve_la_distribucion_inicial():
    for serie, anio in (("EPC", 2014), ("ECP", 2013)):
        e = ESTADOS[(serie, anio)]
        q, proy = e9.predecir(e, 0.0, 0.0)
        assert e9.w1_grilla(q, e.p, e.grilla) < 1e-6 and not proy


def test_el_ladeo_acierta_los_momentos_propuestos():
    e = ESTADOS[("ECP", 2017)]
    q, _ = e9.predecir(e, -0.2, 0.05)
    m, s = e9.momentos(q, e.grilla)
    assert abs(m - (e.media - 0.2)) < 1e-6 and abs(s - (e.sd + 0.05)) < 1e-6


def test_lo_imposible_se_proyecta_y_se_cuenta():
    e = ESTADOS[("EPC", 2014)]
    for dn, dsd in ((3.0, 0.0), (-3.0, 0.0), (0.0, 5.0), (0.0, -2.0)):
        q, proy = e9.predecir(e, dn, dsd)
        assert proy, f"({dn}, {dsd}) no quedó marcada"
        assert abs(q.sum() - 1) < 1e-9 and (q >= 0).all()


def test_w1_exacto_coincide_con_el_de_muestras():
    rng = np.random.default_rng(1)
    a, b = ESTADOS[("EPC", 2014)], ESTADOS[("EPC", 2015)]
    exacto = e9.w1_grilla(a.p, b.p, a.grilla)
    muestral = wasserstein1(rng.choice(a.grilla, 200_000, p=a.p), rng.choice(b.grilla, 200_000, p=b.p))
    assert abs(exacto - muestral) < 0.01, (exacto, muestral)
    assert e9.w1_grilla(a.p, a.p, a.grilla) == 0.0
    assert abs(exacto - e9.w1_grilla(b.p, a.p, a.grilla)) < 1e-12


def test_el_piso_es_reproducible_y_crece_con_menos_muestra():
    e = ESTADOS[("EPC", 2019)]
    assert e9.piso_de_ruido(e, reps=30) == e9.piso_de_ruido(e, reps=30)
    assert e9.piso_de_ruido(e, n=200, reps=30) > e9.piso_de_ruido(e, n=5000, reps=30)


def test_la_grilla_de_la_ecp():
    assert len(e9.GRILLA_ECP) == 233 and e9.GRILLA_ECP[0] == 1 and e9.GRILLA_ECP[-1] == 5


# --- los baselines salen de su definición -----------------------------------

def test_un_modelo_oraculo_empata_con_el_oraculo():
    filas, _ = correr(modelo_que(ORACULO))
    b, o = _por(filas, "brazo_B"), _por(filas, "oraculo")
    assert len(b) == 12
    for c in b:
        assert abs(b[c]["w1_piso"] - o[c]["w1_piso"]) < 1e-9, c


def test_un_modelo_que_no_cambia_nada_empata_con_sin_cambio():
    filas, _ = correr(modelo_que(CERO), brazos=("A",))
    a, s = _por(filas, "brazo_A"), _por(filas, "sin_cambio")
    for c in a:
        assert abs(a[c]["w1_piso"] - s[c]["w1_piso"]) < 1e-9, c


def test_tendencia_es_el_cambio_anterior_de_la_misma_serie():
    t = e9.baselines(ESTADOS)["tendencia"]
    assert "ECP_2013_2017" not in t and "EPC_2014_2015" not in t and len(t) == 10
    assert t["EPC_2015_2017"] == e9.cambio_observado(e9.TRANSICIONES[4], ESTADOS)
    filas, _ = correr(modelo_que(_tendencia), brazos=("B",))
    b, tt = _por(filas, "brazo_B"), _por(filas, "tendencia")
    for c in tt:
        assert abs(b[c]["w1_piso"] - tt[c]["w1_piso"]) < 1e-9, c


# --- sonda de memoria -------------------------------------------------------

def test_la_sonda_marca_memoria_a_menos_de_010():
    for error, esperado in ((0.0, True), (0.099, True), (0.10, False), (-0.3, False)):
        cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
        s = e9.sondear(e9.TRANSICIONES[0], ESTADOS, modelo_que(CERO, sonda_error=error), cache, "m")
        assert s["en_memoria"] is esperado, (error, s)


def test_la_sonda_complementaria_solo_en_la_epc():
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    m = modelo_que(CERO)
    assert "respuesta_pct_4_5" not in e9.sondear(e9.TRANSICIONES[0], ESTADOS, m, cache, "m")
    s = e9.sondear(e9.TRANSICIONES[4], ESTADOS, m, cache, "m")
    assert s["en_memoria_complementaria"] is False and s["respuesta_pct_4_5"] is not None


def test_una_sonda_sin_respuesta_no_marca_memoria():
    llamadas = []

    def mudo(modelo, sistema, usuario, temp):
        llamadas.append(1)
        return "prefiero no decirlo"
    s = e9.sondear(e9.TRANSICIONES[0], ESTADOS, mudo, e9.Cache(Path(tempfile.mkdtemp()) / "c.json"), "m")
    assert s["en_memoria"] is False and s["sin_respuesta"] and len(llamadas) == e9.INTENTOS_SONDA


def test_la_sonda_va_a_temperatura_cero():
    temps = []

    def m(modelo, sistema, usuario, temp):
        temps.append(temp)
        return '{"media": 3}'
    e9.sondear(e9.TRANSICIONES[0], ESTADOS, m, e9.Cache(Path(tempfile.mkdtemp()) / "c.json"), "m")
    assert temps == [0.0]


# --- predicciones y regla de decisión ---------------------------------------

def test_oraculo_honesto_fuera_de_memoria_se_adopta():
    filas, sonda = correr(modelo_que(ORACULO, ancho=0.5, sonda_error=0.5))
    r = e9.resumen(filas)
    p = r["predicciones"]
    assert p["P1"]["valor"] == 11 and p["P1"]["se_cumple"]
    assert p["P2"]["se_cumple"]                         # le gana a «sin cambio»
    assert not p["P3"]["se_cumple"]                     # y a «tendencia» por mucho
    assert not p["P5"]["se_cumple"]                     # cobertura 100 %
    assert p["P6"]["se_cumple"] is False                # gana fuera de memoria
    assert r["regla"]["c1"] and r["regla"]["c2"] and r["regla"]["c3"]
    assert r["regla"]["veredicto"].startswith("Pasa las tres")


def test_modelo_que_no_cambia_nada_falla_el_criterio_1():
    filas, _ = correr(modelo_que(CERO))
    r = e9.resumen(filas)
    assert not r["regla"]["c1"] and r["regla"]["veredicto"].startswith("Falla 1")
    assert r["predicciones"]["P1"]["valor"] == 0          # Δ = 0 cuenta como signo fallado
    assert not r["predicciones"]["P2"]["se_cumple"]


def test_oraculo_sobreconfiado_falla_el_criterio_2():
    corrido = lambda t: tuple(x + 0.02 for x in ORACULO(t))          # noqa: E731
    filas, _ = correr(modelo_que(corrido, ancho=0.001))
    r = e9.resumen(filas)
    assert r["regla"]["c1"] and not r["regla"]["c2"]
    assert r["predicciones"]["P5"]["se_cumple"] and r["secundarias"]["cobertura_por_repeticion"] == 0
    assert r["regla"]["veredicto"].startswith("Pasa 1, falla 2")


def test_si_todo_esta_en_memoria_no_se_adopta():
    filas, sonda = correr(modelo_que(ORACULO, ancho=0.5, sonda_error=0.0))
    r = e9.resumen(filas)
    assert all(s["en_memoria"] for s in sonda.values())
    assert r["regla"]["c3"] is None and r["predicciones"]["P6"]["se_cumple"] is None
    assert "fuera de memoria" in r["regla"]["veredicto"]


def test_la_sensibilidad_de_memoria_usa_la_union_de_las_sondas():
    filas, sonda = correr(modelo_que(ORACULO, sonda_error=0.5), brazos=("B",))
    for f in filas:
        if f["serie"] == "EPC":
            f["en_memoria_sens"] = True                 # como si la sonda de BCV acertara
    r = e9.resumen(filas)
    assert r["sensibilidad_memoria_no_preregistrada"]["n_fuera"] == 4
    assert r["predicciones"]["P6"]["valor"]["n_fuera"] == 12


def test_el_veredicto_completo_se_puede_guardar_en_json():
    filas, sonda = correr(modelo_que(ORACULO))
    v = e9.veredicto_completo(filas, sonda, {"modelo": "m", "simulado": True})
    json.dumps(v, ensure_ascii=False)
    assert v["w1_piso"]["oraculo"]["total"]["n"] == 12 and v["brazo_A"] and v["brazo_B"]


# --- control por permutación (enmienda 5) ----------------------------------

def _agregados(propone, ancho=0.5):
    llamar = modelo_que(propone, ancho=ancho)
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    return {t.clave: e9.agregar(e9.recolectar_brazo(t, "A", ESTADOS, llamar, cache, "m")["propuestas"])
            for t in e9.TRANSICIONES}


def test_un_modelo_que_ignora_el_periodo_no_pasa_la_permutacion():
    """Misma propuesta en todos los periodos de una serie: permutar no cambia nada."""
    fijo = lambda t: (-0.15, 0.02) if t.serie == "ECP" else (0.10, -0.03)      # noqa: E731
    c = e9.control_permutacion(ESTADOS, _agregados(fijo), {}, PISOS, "A", n=200)
    assert c["p"] == 1.0 and c["lectura"].startswith("La ventaja del brazo no se distingue")


def test_el_oraculo_pasa_la_permutacion():
    c = e9.control_permutacion(ESTADOS, _agregados(ORACULO), {}, PISOS, "A", n=200)
    assert c["p"] <= 0.05, c
    assert c["fraccion_que_pasa_c1"] < 1


def test_la_permutacion_es_reproducible_y_no_mezcla_series():
    ag = _agregados(ORACULO)
    a = e9.control_permutacion(ESTADOS, ag, {}, PISOS, "A", n=100)
    b = e9.control_permutacion(ESTADOS, ag, {}, PISOS, "A", n=100)
    assert a == b
    # una propuesta de la EPC puesta en la ECP se notaría: aquí basta con que
    # el observado sea el de la asignación identidad
    filas = e9.evaluar(ESTADOS, {"A": ag}, {}, PISOS)
    assert abs(a["mediana_w1_piso_brazo"] - round(e9._mediana(e9._de(filas, "brazo_A")), 4)) < 1e-9


def test_el_veredicto_trae_el_control():
    filas, sonda = correr(modelo_que(ORACULO), brazos=("B",))
    v = e9.veredicto_completo(filas, sonda, {}, {"brazo_B": {"p": 0.01}})
    assert v["control_permutacion_enmienda_5"]["brazo_B"]["p"] == 0.01


# --- la línea de comandos no gasta nada -------------------------------------

def test_real_sin_clave_no_llama():
    import os
    viejo = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        assert e9.main(["sonda", "--real", "--salida", tempfile.mkdtemp()]) == 1
    finally:
        if viejo is not None:
            os.environ["OPENROUTER_API_KEY"] = viejo


def test_sin_confirmacion_no_se_gasta_nada():
    n = len(INTENTOS_DE_RED)
    llamadas = []
    m = modelo_que(ORACULO, llamadas=llamadas)
    tmp = Path(tempfile.mkdtemp())
    r = e9.correr_sonda(ESTADOS, m, e9.Cache(tmp / "c.json"), e9.MODELO, tmp, entrada=lambda _: "no")
    assert r is None and llamadas == [] and len(INTENTOS_DE_RED) == n


def test_los_brazos_reales_exigen_la_sonda_antes():
    tmp = Path(tempfile.mkdtemp())
    try:
        e9.correr_brazos(ESTADOS, modelo_que(ORACULO), e9.Cache(tmp / "c.json"), e9.MODELO, tmp,
                         entrada=lambda _: "si")
    except e9.Experimento9Error:
        return
    raise AssertionError("los brazos corrieron sin sonda")


def test_el_costo_se_estima():
    tokens, usd, base = e9.estimar_costo([("s" * 350, "u" * 3150, 350)] * 240)
    assert tokens == 240 * 1350 and 0 < usd < 1 and "Exp. 8" in base


def test_con_costo_medido_la_estimacion_usa_lo_medido():
    medido = {"llamadas": 2, "llamadas_con_costo": 2, "costo_usd": 0.004,
              "prompt_tokens": 1000, "completion_tokens": 3000}     # 1e-6 USD por token
    tokens, usd, base = e9.estimar_costo([("s" * 350, "u" * 3150, 350)] * 10, medido)
    # 1000 de entrada estimados + 1500 de salida medidos (razonamiento incluido)
    assert tokens == 10 * 2500 and abs(usd - 0.025) < 1e-12 and "medido" in base


# --- DI-E9 y DI-E10: quién respondió, cuánto costó, y el piloto --------------

def _con_meta(llamar, modelo_servido="xiaomi/mimo-v2.6-pro", costo=0.001):
    def envuelto(modelo, sistema, usuario, temp):
        return {"texto": llamar(modelo, sistema, usuario, temp), "modelo_servido": modelo_servido,
                "proveedor": "Xiaomi", "uso": {"prompt_tokens": 800, "completion_tokens": 1200,
                                               "reasoning_tokens": 900, "costo_usd": costo}}
    return envuelto


def test_la_cache_guarda_el_modelo_que_respondio_y_el_costo():
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    r = e9.recolectar_brazo(e9.TRANSICIONES[0], "A", ESTADOS, _con_meta(modelo_que(ORACULO)), cache, "m")
    assert len(r["propuestas"]) == 10
    g = e9.gasto_registrado(e9.Cache(cache.ruta))               # releído del disco
    assert g["llamadas"] == 10 and abs(g["costo_usd"] - 0.01) < 1e-12
    assert g["reasoning_tokens"] == 9000 and g["modelos_servidos"] == {"xiaomi/mimo-v2.6-pro": 10}


def test_una_cache_vieja_sin_metadatos_sigue_sirviendo():
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    e9.recolectar_brazo(e9.TRANSICIONES[0], "A", ESTADOS, modelo_que(ORACULO), cache, "m")
    g = e9.gasto_registrado(cache)
    assert g["llamadas"] == 0 and g["costo_usd"] == 0.0


def test_el_limite_corta_y_no_se_cuenta_como_fallo():
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    llamar = e9.con_limite(modelo_que(ORACULO), 3)
    try:
        e9.recolectar_brazo(e9.TRANSICIONES[0], "A", ESTADOS, llamar, cache, "m")
    except e9.LimiteDeLlamadas:
        assert len(cache.datos) == 3
        return
    raise AssertionError("el límite se tragó como un fallo más")


def test_el_piloto_se_reutiliza_y_evaluar_rechaza_brazos_incompletos():
    tmp = Path(tempfile.mkdtemp())
    try:
        e9._escribir(tmp / "sonda.json", {})
        llamadas = []
        m = _con_meta(modelo_que(ORACULO, llamadas=llamadas))
        cache = e9.Cache(tmp / "cache.json")
        e9.correr_brazos(ESTADOS, m, cache, e9.MODELO, tmp, entrada=lambda _: "si", maximo=2)
        assert len(llamadas) == 2
        try:
            e9.correr_evaluacion(ESTADOS, tmp, {})
            raise AssertionError("evaluó brazos incompletos")
        except e9.Experimento9Error as err:
            assert "incompleto" in str(err)
        e9.correr_brazos(ESTADOS, m, e9.Cache(tmp / "cache.json"), e9.MODELO, tmp,
                         entrada=lambda _: "si")
        assert len(llamadas) == 240                   # las 2 del piloto no se repiten
    finally:
        shutil.rmtree(tmp)


def test_el_cliente_real_pide_el_costo_y_lee_el_modelo_servido():
    import os
    from src.experiments import donante_llm
    enviado = {}

    def falso_post(url, cuerpo, cabeceras, timeout=90):
        enviado.update(url=url, cuerpo=cuerpo, cabeceras=cabeceras)
        return {"id": "gen-1", "model": "xiaomi/mimo-v2.6-pro", "provider": "Xiaomi",
                "choices": [{"message": {"content": '{"media": 2.4}'}}],
                "usage": {"prompt_tokens": 120, "completion_tokens": 800, "cost": 0.0021,
                          "completion_tokens_details": {"reasoning_tokens": 780}}}
    viejo_post, vieja_clave = donante_llm._post, os.environ.get("OPENROUTER_API_KEY")
    donante_llm._post = falso_post
    os.environ["OPENROUTER_API_KEY"] = "clave-de-prueba"
    try:
        r = e9.cliente_real()(e9.MODELO, "s", "u", 0.0)
    finally:
        donante_llm._post = viejo_post
        if vieja_clave is None:
            os.environ.pop("OPENROUTER_API_KEY")
        else:
            os.environ["OPENROUTER_API_KEY"] = vieja_clave
    assert enviado["cuerpo"]["usage"] == {"include": True}
    assert enviado["cuerpo"]["model"] == e9.MODELO and enviado["url"].startswith("https://openrouter.ai")
    assert r["texto"] == '{"media": 2.4}' and r["modelo_servido"] == "xiaomi/mimo-v2.6-pro"
    assert r["uso"] == {"prompt_tokens": 120, "completion_tokens": 800,
                        "reasoning_tokens": 780, "costo_usd": 0.0021}


def test_todo_simulado_sobre_los_datos_reales():
    """De punta a punta con los cargadores reales, el modelo simulado y sin red."""
    if not DATOS_REALES:
        print("         (sin data/raw/ecp en esta máquina: se omite)")
        return
    tmp = Path(tempfile.mkdtemp())
    try:
        assert e9.main(["todo", "--salida", str(tmp)]) == 0
        v = json.loads((tmp / "veredicto.json").read_text(encoding="utf-8"))
        assert v["simulado"] is True and v["w1_piso"]["brazo_B"]["total"]["n"] == 12
        # un modelo que propone al azar no depende del periodo
        assert v["control_permutacion_enmienda_5"]["brazo_B"]["n_permutaciones"] == e9.N_PERMUTACIONES
        # el oráculo no puede ser peor que «sin cambio» en ninguna serie
        assert v["w1_piso"]["oraculo"]["total"]["mediana"] <= v["w1_piso"]["sin_cambio"]["total"]["mediana"]
    finally:
        shutil.rmtree(tmp)


def test_ninguna_prueba_toco_la_red():
    assert INTENTOS_DE_RED == [], INTENTOS_DE_RED


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in globals().items() if k.startswith("test_")]
    print(f"Experimento 9 — {len(pruebas)} pruebas, sin red\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
