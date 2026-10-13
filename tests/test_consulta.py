"""
tests/test_consulta.py

Pruebas de la consulta de punta a punta (src/consulta/motor.py y servidor.py), con
el modelo simulado: ninguna llama a la API. Usan la población EPC 2022-2025 si está en
esta máquina.
Se ejecuta directo:  python tests/test_consulta.py
"""

import json
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.simplefilter("ignore")

import numpy as np

from src.consulta import motor as mo
from src.consulta import servidor as sv
from src.experiments import experimento9 as e9

FALLOS = []
HAY = (mo.POBLACION / "agentes.parquet").exists()
_tmp = tempfile.TemporaryDirectory()
if HAY:
    LLAMAR, MODELO = mo.cliente(simulado=True)
    M = mo.Motor(LLAMAR, MODELO, cache=e9.Cache(Path(_tmp.name) / "c.json"))


def check(nombre, cuerpo):
    if not HAY:
        print(f"  --     {nombre} (sin la población EPC 2022-2025 en esta máquina)")
        return
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# --- motor ----------------------------------------------------------------------

def test_una_pregunta_del_catalogo_trae_ciudad_grupos_y_19_localidades():
    r = M.responder_catalogo("VS8")
    assert r["suposicion"] and r["tipo"] == "catalogo"
    assert abs(sum(r["ciudad"]["distribucion"]) - 1) < 1e-3
    assert sorted(map(int, r["localidades"])) == list(range(1, 20))          # sin Sumapaz
    assert all(v["margen"][0] <= v["media"] <= v["margen"][1] for v in r["localidades"].values())
    assert [g["grupo"] for g in r["grupos"]["estrato"]] == mo.GRUPOS["estrato"]["orden"]


def test_el_margen_de_una_localidad_es_el_de_la_encuesta():
    """DI-CO1: con ~250 encuestados, el margen del 95 % no puede ser de centésimas."""
    r = M.responder_catalogo("VS8")
    anchos = [v["margen"][1] - v["margen"][0] for v in r["localidades"].values()]
    assert np.median(anchos) > 0.1, np.median(anchos)


def test_no_sabe_no_entra_a_la_media():
    """GG3_GALAN tiene no respuesta: la media de cada localidad tiene que caer en la escala."""
    r = M.responder_catalogo("GG3_GALAN")
    assert all(1 <= v["media"] <= 5 for v in r["localidades"].values())
    assert r["ciudad"]["respondieron"] < 1


def test_una_pregunta_nueva_no_trae_mapa_y_sus_grupos_promedian_cero():
    """DI-CO2."""
    r = M.responder_nueva("¿Qué tan de acuerdo está con X?", ["a", "b", "c", "d", "e"])
    assert r["tipo"] == "nueva" and "localidades" not in r and r["sin_mapa"]
    ag = M.agentes
    for g, filas in r["grupos"].items():
        etq = M.grupos[g].to_numpy()
        pesos = [M.peso[etq == f["grupo"]].sum() for f in filas]
        assert abs(np.average([f["indice"] for f in filas], weights=pesos)) < 0.01, g
    assert len(ag) == 19_000


def test_una_pregunta_nueva_no_trae_nivel_ni_fuerza_y_su_tono_es_el_mismo_siempre():
    """D18: DI-CO14 (el tono general no depende de la pregunta) y DI-CO16 (sin nivel)."""
    a = M.responder_nueva("¿Qué tan de acuerdo está con Y?", ["a", "b", "c", "d", "e"])
    b = M.responder_nueva("¿Qué tan de acuerdo está con otra cosa?", ["a", "b", "c", "d", "e"])
    for r in (a, b):
        assert not {"nivel_propuesto", "fuerza", "fuerza_texto", "aviso_grupos", "aviso_anios", "justificacion"} & set(r)
    assert a["grupos"] == b["grupos"] == M.tono
    assert a["respuesta"]["titulo"] == "No podemos decir si Bogotá estaría de acuerdo."      # DI-CO20
    html = sv.construir_pagina(mo.informacion_general(M.agentes, M.donante), True)
    assert "sin-respuesta" in html and html.count("Para explorar ·") == 2 and "Contexto 1" not in html
    assert a["tono_titulo"] == "Así responden estos grupos en general"                  # DI-CO21
    assert "Es contexto" in a["tono_texto"] and "%" not in a["tono_texto"] and str(M.n_tono) in a["tono_texto"]
    assert 20 <= M.n_tono < len(M.catalogo)


def test_el_tono_es_el_mismo_que_se_midio_en_la_practica():
    """DI-CO14: el tono de la página es el mismo de `practica_puente.tono_general` (el que se midió en el banco)."""
    from src.experiments import practica_puente as pp
    t = pp.tono_general(M)
    m = np.average(t, weights=M.peso)
    t = (t - m) / np.sqrt(np.average((t - m) ** 2, weights=M.peso))
    for g, filas in M.tono.items():
        e = M.grupos[g].to_numpy()
        for f in filas:
            assert abs(np.average(t[e == f["grupo"]], weights=M.peso[e == f["grupo"]]) - f["indice"]) < 1e-3, (g, f)
    est = [f["indice"] for f in M.tono["estrato"]]
    print(f"         tono por estrato (1-2, 3-4, 5-6): {est}")


def test_si_el_v2_dice_sin_base_se_pide_el_puente_de_siempre():
    """DI-CO12, opción 1 de Daniel: no se usa «sin base»; se pide el puente de siempre."""
    from src.experiments import puente as pu
    from src.experiments import puente_sin_base as sb
    cods = list(M.catalogo)
    vistos = []

    def llamar(modelo, sistema, usuario, temp):
        vistos.append(sistema)
        if sistema == sb.SISTEMA_V2:
            return json.dumps({"preguntas": [], "sin_base": True, "nivel": None, "justificacion": "no hay"})
        return json.dumps({"preguntas": [{"codigo": cods[0], "sentido": "+", "peso": 2}], "nivel": 3, "justificacion": "x"})
    m = mo.Motor(llamar, "prueba", donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                 cache=e9.Cache(Path(_tmp.name) / "sinbase.json"))
    r = m.responder_nueva("¿Qué tan de acuerdo está con Z?", ["a", "b", "c", "d", "e"])
    from src.experiments import nivel_parecidas_b as nb
    assert vistos[:2] == [sb.SISTEMA_V2, pu.SISTEMA] and set(vistos[2:]) <= {nb.SISTEMA}     # DI-CO22: luego, la estimación
    assert r["tipo"] == "nueva" and r["reintento"] and [q["codigo"] for q in r["relacionadas"]] == [cods[0]]


def test_las_preguntas_relacionadas_traen_lo_que_la_gente_respondio():
    """DI-CO15: el dato de cada relacionada es el de la ciudad en esa pregunta del catálogo."""
    r = M.responder_nueva("¿Qué tan de acuerdo está con W?", ["a", "b", "c", "d", "e"])
    assert r["relacionadas"]
    for q in r["relacionadas"]:
        c = M.responder_catalogo(q["codigo"])
        assert q["ciudad"] == c["ciudad"] and q["anios"] == c["anios"] and q["escala"] == c["escala"]
        assert q["sentido"] in "+-"
    html = sv.construir_pagina(mo.informacion_general(M.agentes, M.donante), True)
    assert "ver de todos modos" not in html and 'type="range"' not in html and "Ver completa" in html


def test_una_pregunta_nueva_trae_la_estimacion_validada():
    """DI-CO22, DI-CO25, DI-CO29 y DI-CO33: Luna, las 139 candidatas y el rango según cuántas eligió."""
    vistos = []

    def llamar(modelo, sistema, usuario, temp):
        vistos.append(modelo)
        return LLAMAR(modelo, sistema, usuario, temp)
    # un motor que se presenta como real (DI-CO31), con las respuestas del simulado y su caché temporal
    m = mo.Motor(llamar, mo.MODELO_PAGINA, donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                 cache=e9.Cache(Path(_tmp.name) / "est.json"))
    r = m.responder_nueva("¿Qué tan de acuerdo está con V?", ["a", "b", "c", "d", "e"])
    e = r["estimacion"]
    from src.experiments import banco_lote6 as b6
    n = 139 if b6.REALES.exists() else 109                                                # DI-CO29: sin traslado, 109
    assert len(m._candidatas) == n and mo.MODELO_ESTIMACION in vistos
    assert m._candidatas.fuente_txt.notna().all() and m._candidatas.id.str.startswith('EDP25_').sum() == 17
    assert 0 <= e["rango"][0] <= e["porcentaje"] <= e["rango"][1] <= 100
    assert mo.MODELO_ESTIMACION == "openai/gpt-6-luna" and mo.H_ESTIMACION_K == {1: 23.9, 2: 22.9, 3: 21.7}   # DI-CO33
    assert mo.MODELO_PAGINA == "openai/gpt-6-luna"                                                 # DI-CO26
    h = mo.H_ESTIMACION_K[min(len(e["preguntas"]), 3)]
    assert abs(e["rango"][1] - min(100, e["porcentaje"] + h)) < 0.06 and e["preguntas"]
    assert "71 %" in e["texto"] and "acertó 12" in e["texto"] and "texto original" in e["texto"]    # DI-CO29
    lado = "sí" if e["rango"][0] > 50 else ("no" if e["rango"][1] < 50 else "dividida")
    assert e["llamada"] == lado and e["titulo"] == mo.LLAMADA_TITULO[lado] and "estimación, no una medición" in e["texto"]
    html = sv.construir_pagina(mo.informacion_general(M.agentes, M.donante), True)
    assert 'class="estimacion' in html and "En qué se apoya la estimación" in html


def test_la_estimacion_usa_lo_que_escribio_la_persona():
    """DI-CO28: con `original`, el modelo que estima ve lo escrito; lo mostrado sigue siendo la reformulada."""
    from src.experiments import nivel_parecidas_b as nb
    vistos = []

    def llamar(modelo, sistema, usuario, temp):
        if sistema == nb.SISTEMA:
            vistos.append(usuario.split("\n")[1])
        return LLAMAR(modelo, sistema, usuario, temp)
    m = mo.Motor(llamar, MODELO, donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                 cache=e9.Cache(Path(_tmp.name) / "original.json"))
    r = m.responder_nueva("¿Qué tan de acuerdo está con S?", ["a", "b", "c", "d", "e"], original="¿la gente quiere S?")
    assert vistos == ["¿la gente quiere S?"] and r["pregunta"] == "¿Qué tan de acuerdo está con S?"
    m.responder_nueva("¿Qué tan de acuerdo está con R?", ["a", "b", "c", "d", "e"])            # sin original, como antes
    assert vistos[-1] == "¿Qué tan de acuerdo está con R?"
    html = sv.construir_pagina(mo.informacion_general(M.agentes, M.donante), True)
    assert "original:q" in html and "original:v" in html


def test_si_la_estimacion_falla_queda_el_aviso_de_siempre():
    """DI-CO22: si el modelo no da candidatas válidas, `estimacion` es None y la página muestra DI-CO20."""
    from src.experiments import nivel_parecidas_b as nb

    def llamar(modelo, sistema, usuario, temp):
        return "no sé" if sistema == nb.SISTEMA else LLAMAR(modelo, sistema, usuario, temp)
    m = mo.Motor(llamar, MODELO, donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                 cache=e9.Cache(Path(_tmp.name) / "est_roto.json"))
    r = m.responder_nueva("¿Qué tan de acuerdo está con U?", ["a", "b", "c", "d", "e"])
    assert r["estimacion"] is None and r["respuesta"]["titulo"].startswith("No podemos decir")


def test_sin_saldo_o_sin_red_se_dice_que_el_servicio_no_respondio():
    """DI-CO24: un error de HTTP o de red no se confunde con «no se pudo estimar»."""
    import urllib.error
    from src.experiments import nivel_parecidas_b as nb

    def sin_saldo(modelo, sistema, usuario, temp):
        if sistema == nb.SISTEMA:
            raise urllib.error.HTTPError("https://openrouter.ai", 402, "Payment Required", {}, None)
        return LLAMAR(modelo, sistema, usuario, temp)
    m = mo.Motor(sin_saldo, MODELO, donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                 cache=e9.Cache(Path(_tmp.name) / "sin_saldo.json"))
    try:
        m.responder_nueva("¿Qué tan de acuerdo está con T?", ["a", "b", "c", "d", "e"])
    except mo.ServicioNoDisponible as e:
        assert "saldo" in str(e) and isinstance(e, mo.ConsultaError)
    else:
        raise AssertionError("un 402 no puede quedar como «no se pudo estimar»")

    def sin_red(*a):
        raise TimeoutError("sin red")
    m2 = mo.Motor(sin_red, MODELO, donante=M.donante, agentes=M.agentes, catalogo=M.catalogo,
                  cache=e9.Cache(Path(_tmp.name) / "sin_red.json"))
    try:
        m2.reformular("¿x?")
    except mo.ServicioNoDisponible as e:
        assert "conexión" in str(e)
    else:
        raise AssertionError("sin red, la reformulación debe decir que el servicio no respondió")


def test_un_puente_roto_se_dice_y_no_se_responde():
    roto = mo.Motor(lambda *a: "esto no es json", "roto", donante=M.donante, agentes=M.agentes,
                    catalogo=M.catalogo, cache=e9.Cache(Path(_tmp.name) / "roto.json"))
    assert roto.responder_nueva("¿x?", ["a", "b", "c", "d", "e"])["tipo"] == "invalida"
    assert roto.reformular("¿x?")["alcance"] == "invalida"


def test_una_pregunta_vacia_o_un_codigo_inexistente_son_error():
    for f in (lambda: M.reformular("   "), lambda: M.responder_catalogo("ZZ9")):
        try:
            f()
        except mo.ConsultaError:
            continue
        raise AssertionError("debió fallar")


def test_cada_pregunta_responde_con_los_donantes_de_sus_anios():
    """DI-CO6 y DI-CO38: VS8 junta cuatro años; GG3_GALAN solo 2024-2025 (DI-AR5, DI-PO6)."""
    cuatro, dos = M.responder_catalogo("VS8"), M.responder_catalogo("GG3_GALAN")
    assert cuatro["anios"] == [2022, 2023, 2024, 2025] and dos["anios"] == [2024, 2025]
    assert cuatro["encuestados_mediana_localidad"] > 280 > 200 > dos["encuestados_mediana_localidad"] > 100
    assert "2022, 2023, 2024 y 2025" in cuatro["fuente"]
    solo = [v for v, a in M.anios.items() if a == [2023]][0]
    r = M.responder_catalogo(solo)
    assert r["anios"] == [2023] and r["encuestados_mediana_localidad"] < 120 and r["ciudad"]["respondieron"] > 0.5


def test_el_puente_estandariza_cada_pregunta_dentro_de_su_anio():
    """DI-CO7: en cada año, cada pregunta del puente tiene media ponderada 0."""
    anio = M.donante.anio.to_numpy()
    w = M.donante.peso.to_numpy(float)
    z = M.datos_puente.z["VS8"]
    for a in (2022, 2023, 2024):
        m = anio == a
        assert abs(np.sum(z[m] * w[m]) / np.sum(w[m])) < 0.05


def test_dice_a_cuantos_consulto_y_sin_numeros_en_las_etiquetas():
    """DI-CO9 y DI-CO10: VS18 solo tiene 2023 y sus etiquetas traen «4. Alta»."""
    tres, solo = M.responder_catalogo("VS8"), M.responder_catalogo("VS18")
    assert tres["consultados"] == len(M.agentes) == 19_000
    assert 5_000 < solo["consultados"] < 8_000
    assert not any(e[0].isdigit() for e in solo["escala"]) and not solo["ciudad"]["etiqueta_alto"][0].isdigit()
    assert mo._etq("4. Alta") == "Alta" and mo._etq("Muy alta") == "Muy alta" and mo._etq("0. Sin estrato") == "Sin estrato"


def test_las_escalas_numericas_se_muestran_como_numeros_con_sus_extremos():
    """DI-CO17: MV13_7 solo nombra los extremos; CO1_1 viene en mayúsculas; SP1 trae «5 Muy satisfecho»."""
    r = M.responder_catalogo("MV13_7")
    assert r["escala"] == ["1 · Muy insatisfecho", "2", "3", "4", "5 · Muy satisfecho"]
    assert r["ciudad"]["etiqueta_alto"] == "4 o 5 (muy satisfecho)"
    assert mo.escala_visible(M.catalogo["CO1_1"])[0] == "1 · Nada"
    assert mo.escala_visible(M.catalogo["SP1"])[-1] == "Muy satisfecho"
    for f in M.catalogo.values():                 # nada empieza con un número suelto salvo «2», «3», «4» o «1 · …»
        for e in mo.escala_visible(f):
            assert not e[0].isdigit() or e.isdigit() or " · " in e, (f["variable"], e)


def test_el_porcentaje_cuenta_el_lado_favorable_si_se_sabe():
    """DI-CO18: AG1 tiene lo favorable abajo; CC2 trae categorías que no son opinión; VS18 no tiene lado favorable."""
    ag1, cc2, vs8 = M.responder_catalogo("AG1"), M.responder_catalogo("CC2"), M.responder_catalogo("VS8")
    assert ag1["ciudad"]["etiqueta_alto"] == "Buen camino"
    assert abs(ag1["ciudad"]["alto"] - ag1["ciudad"]["distribucion"][0]) < 1e-4
    assert cc2["ciudad"]["etiqueta_alto"] == "Favorable"
    assert abs(cc2["ciudad"]["alto"] - cc2["ciudad"]["distribucion"][0]) < 1e-4
    assert vs8["ciudad"]["etiqueta_alto"] == "Algo seguro o muy seguro"
    assert mo.lado(M.catalogo["VS18"]) == ([4, 5], "Alta o muy alta")
    loc = next(iter(ag1["localidades"].values()))
    assert 0 < loc["alto"] < 1 and all(0 < g["alto"] < 1 for g in ag1["grupos"]["estrato"])


def test_no_tiene_opinion_y_no_lo_conoce_cuentan_como_no_sabe():
    """DI-CO19: CC2 se muestra con Favorable / Desfavorable; el resto queda fuera y se dice cuánto."""
    r = M.responder_catalogo("CC2")
    assert r["escala"] == ["Favorable", "Desfavorable"] and len(r["ciudad"]["distribucion"]) == 2
    assert abs(sum(r["ciudad"]["distribucion"]) - 1) < 1e-3
    assert 1 <= r["ciudad"]["media"] <= 2 and all(1 <= v["media"] <= 2 for v in r["localidades"].values())
    assert 0.5 < r["ciudad"]["respondieron"] < 0.95                       # la página dice cuántos no cuentan
    assert M.catalogo["CC2"]["escala"] == [1, 2, 3, 4]                       # el catálogo del modelo no cambia
    html = sv.construir_pagina(mo.informacion_general(M.agentes, M.donante), True)
    assert "no sabía o no tenía opinión" in html


def test_sin_grupo_de_educacion():
    """DI-CO5: la población 2022-2024 no empareja por educación."""
    assert "educacion" not in mo.GRUPOS and "educacion" not in M.responder_catalogo("VS8")["grupos"]


# --- intención de voto (DI-CO30) -----------------------------------------------------

def _hay_voto():
    try:
        M._banco_voto()
    except mo.ConsultaError:
        print("         (sin los resultados del lote 7 en esta máquina: se omite)")
        return False
    return True


def test_la_reformulacion_de_la_pagina_es_la_version_5_y_reconoce_el_voto():
    """DI-CO30, DI-CO32 y DI-CO37."""
    vistos = []
    mensajes = []
    m = mo.Motor(lambda mod, s, u, t: vistos.append(s) or mensajes.append(u) or LLAMAR(mod, s, u, t), MODELO,
                 donante=M.donante, anios=M.anios, agentes=M.agentes, cache=e9.Cache(Path(_tmp.name) / "v5.json"))
    m.reformular("¿Qué tan orgullosos se sienten de Bogotá?")
    from src.consulta import reformular as rf
    assert vistos == [rf.SISTEMA_V5]
    lineas = mensajes[0].split("\n")
    gg3 = [l for l in lineas if l.startswith("GG3_GALAN |")][0]
    assert "[Se midió en 2024 y 2025, con el alcalde Carlos Fernando Galán" in gg3                    # DI-CO38
    assert not any(l.startswith(("GG3 |", "CV5 |", "GP1N_", "MICE1 |")) for l in lineas)              # sin López
    assert "Concejo de 2024-2027" in [l for l in lineas if l.startswith("CC5A_GALAN |")][0]
    assert "[" not in [l for l in mensajes[0].split("\n") if l.startswith("VS8 |")][0]
    r = M.reformular("¿Cuántos bogotanos votarían por Iván Cepeda?")
    assert r["alcance"] == "voto" and r["tipo"] == "primera" and r["candidatos"] == ["Iván Cepeda"] and r["escala"] is None
    assert M.reformular("¿La gente se siente segura caminando por su barrio?")["alcance"] == "catalogo"


def test_la_intencion_de_voto_trae_rango_encuestas_y_aviso_sin_mapa():
    if not _hay_voto():
        return
    r = M.responder_voto("primera", ["Iván Cepeda"], "¿Votaría por Iván Cepeda?")
    assert r["tipo"] == "voto" and r["suposicion"] and r["llamada"] is None and "localidad" in r["sin_mapa"]
    assert "suposición" in r["aviso"] and "mayo de 2026" in r["aviso"]
    (e,) = r["estimaciones"]
    assert 1 <= len(e["preguntas"]) <= 5 and e["candidato"] == "Iván Cepeda"
    assert abs(e["porcentaje"] - np.mean([q["porcentaje"] for q in e["preguntas"]])) < 0.1
    assert abs(e["rango"][1] - e["rango"][0] - 2 * mo.H_VOTO) < 0.2 or 0 in e["rango"] or 100 in e["rango"]
    assert all(q["pregunta"].startswith("En ") and q["fuente"].startswith("Encuesta del CNC") for q in e["preguntas"])
    assert "localidades" not in r and "grupos" not in r                         # solo el total de Bogotá
    assert set(e["edad"]) <= set(mo.VOTO_EDAD) and e["edad"] and mo.H_VOTO_EDAD == 9.5          # DI-CO34
    for g in e["edad"].values():
        assert abs(g["rango"][1] - min(100, g["porcentaje"] + 9.5)) < 0.06
    assert "estrato" in r["edad_texto"] and "sexo" in r["edad_texto"]                          # dice por qué no van


def test_la_segunda_vuelta_estima_a_los_dos_y_solo_llama_con_mas_de_16_puntos():
    if not _hay_voto():
        return
    r = M.responder_voto("segunda", ["Iván Cepeda", "Paloma Valencia"], "¿Quién ganaría?")
    a, b = r["estimaciones"]
    assert [a["candidato"], b["candidato"]] == ["Iván Cepeda", "Paloma Valencia"]
    d = a["porcentaje"] - b["porcentaje"]
    assert (r["llamada"] == "Reñida") == (abs(d) <= mo.H2_VOTO)


def test_el_simulado_nunca_guarda_con_el_nombre_de_un_modelo_real():
    """DI-CO31: una prueba en --simulado no puede quedar como respuesta de Luna en la caché."""
    with tempfile.TemporaryDirectory() as tmp:
        c = e9.Cache(Path(tmp) / "c.json")
        m = mo.Motor(LLAMAR, MODELO, donante=M.donante, anios=M.anios, agentes=M.agentes, cache=c)
        assert m.modelo_est == e9.MODELO_SIMULADO
        m.responder_nueva("¿Estaría de acuerdo con más ciclorrutas?", ["a", "b", "c", "d", "e"])
        if _hay_voto():
            m.responder_voto("primera", ["Iván Cepeda"], "¿x?")
        assert c.datos and all(v["modelo"] == e9.MODELO_SIMULADO for v in c.datos.values())

def test_las_respuestas_se_agrupan_y_el_gobierno_dice_quien_era():
    """DI-CO36."""
    r = M.responder_catalogo("GG3_GALAN")
    assert [g["nombre"] for g in r["agrupada"]] == ["Negativa", "Neutral", "Positiva"]
    assert sorted(i for g in r["agrupada"] for i in g["indices"]) == list(range(len(r["escala"])))
    assert "Galán" in r["nota"] and "Claudia López" not in r["nota"]                           # DI-CO38
    assert "Claudia López" in mo.nota_gobierno("GG3", [2022, 2023])            # la rama de la población 2022-2024
    assert [g["nombre"] for g in mo.agrupar(M.catalogo["GG7"])] == ["Lado bajo", "En el medio", "Lado alto"]   # sin lado conocido
    assert mo.agrupar(M.catalogo["AG1"]) is None and M.responder_catalogo("VS8")["nota"] is None
    assert "mezcla los dos gobiernos" in mo.nota_gobierno("MICE1", [2023, 2024])
    html = (Path(__file__).resolve().parents[1] / "src" / "consulta" / "pagina.html").read_text(encoding="utf-8")
    assert "function reparto" in html and "data-vista" in html and ".filtro[data-f]" in html


def test_una_segunda_vuelta_incompleta_dice_como_escribirla():
    """DI-CO35: no se reinterpreta, se explica."""
    m = mo.mensaje_voto_incompleto(json.dumps({"alcance": "voto", "tipo": "segunda", "candidatos": ["Iván Cepeda"],
                                               "reformulada": "¿x?"}))
    assert "nombra a los dos candidatos" in m and "entre Iván Cepeda y Abelardo de la Espriella" in m
    m = mo.mensaje_voto_incompleto(json.dumps({"alcance": "voto", "tipo": "primera",
                                               "candidatos": ["Iván Cepeda", "Abelardo de la Espriella"], "reformulada": "¿x?"}))
    assert "segunda vuelta entre Iván Cepeda y Abelardo de la Espriella" in m and "votarían por Iván Cepeda" in m
    assert mo.mensaje_voto_incompleto(json.dumps({"alcance": "nueva"})) is None and mo.mensaje_voto_incompleto("no es json") is None

    def uno_solo(modelo, sistema, usuario, temp):
        return json.dumps({"alcance": "voto", "tipo": "segunda", "candidatos": ["Iván Cepeda"], "reformulada": "¿x?"})
    m2 = mo.Motor(uno_solo, MODELO, donante=M.donante, anios=M.anios, agentes=M.agentes,
                  cache=e9.Cache(Path(_tmp.name) / "inc.json"))
    r = m2.reformular("¿En una segunda vuelta, votaría usted por Iván Cepeda?")
    assert r["alcance"] == "invalida" and "nombra a los dos candidatos" in r["mensaje"]


def test_un_voto_mal_formado_es_error():
    for t, c in [("consulta", ["X"]), ("segunda", ["X"]), ("primera", [])]:
        try:
            M.responder_voto(t, c, "¿x?")
        except mo.ConsultaError:
            continue
        raise AssertionError(t)


def test_la_pagina_muestra_el_voto_sin_mapa():
    html = (Path(__file__).resolve().parents[1] / "src" / "consulta" / "pagina.html").read_text(encoding="utf-8")
    assert "r.alcance === 'voto'" in html and "Intención de voto · estimación" in html and "function mostrarVoto" in html
    assert "estado.modo === 'nueva' || estado.modo === 'voto'" in html                # mapa apagado
    assert "encuestas del CNC y su resultado real en Bogotá" in html
    assert "function edadVoto" in html and "${edadVoto(r)}" in html                              # DI-CO34


# --- servidor y página -------------------------------------------------------------

def _servidor():
    general = mo.informacion_general(M.agentes, M.donante)
    srv = sv.crear_servidor(M, lambda: sv.construir_pagina(general, True), 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _post(url, cuerpo):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_el_servidor_responde_las_tres_rutas_y_solo_en_localhost():
    srv, base = _servidor()
    try:
        assert srv.server_address[0] == "127.0.0.1"                           # DI-SE1
        with urllib.request.urlopen(base + "/", timeout=30) as r:
            html = r.read().decode("utf-8")
        assert "/*__DATOS__*/" not in html and "/*__BASE__*/" not in html
        assert "es una suposición" in html and "#mapa .loc:focus" in html and "data-capa" not in html     # sin los botones de antes
        s, d = _post(base + "/api/reformular", {"pregunta": "¿La gente se siente segura caminando por su barrio?"})
        assert s == 200 and d["alcance"] == "catalogo" and d["codigo"] == "VS8"
        s, d = _post(base + "/api/responder", {"codigo": "VS8"})
        assert s == 200 and d["tipo"] == "catalogo"
        s, d = _post(base + "/api/responder", {"pregunta": "¿x?", "escala": ["a", "b", "c", "d", "e"]})
        assert s == 200 and d["tipo"] == "nueva"
        s, d = _post(base + "/api/reformular", {"pregunta": "¿Votaría por Paloma Valencia?"})
        assert s == 200 and d["alcance"] == "voto"
        s, d = _post(base + "/api/responder", {"voto": {"tipo": "consulta", "candidatos": ["X"], "reformulada": "¿x?"}})
        assert s == 400
        assert _post(base + "/api/responder", {"codigo": "ZZ9"})[0] == 400
        assert _post(base + "/api/otra", {})[0] == 404
    finally:
        srv.shutdown()


def test_la_informacion_general_no_trae_opinion():
    g = mo.informacion_general(M.agentes, M.donante)
    assert len(g) == 20 and set(next(iter(g.values()))) == {"nombre", "adultos", "estrato_medio", "encuestados"}
    assert g["20"]["encuestados"] == 0


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Consulta — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
