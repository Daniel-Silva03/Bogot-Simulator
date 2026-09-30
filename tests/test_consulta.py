"""
tests/test_consulta.py

Pruebas de la consulta de punta a punta (src/consulta/motor.py y servidor.py), con
el modelo simulado: ninguna llama a la API. Usan la población EPC 2022-2024 si está en
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
        print(f"  --     {nombre} (sin la población EPC 2022-2024 en esta máquina)")
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
    """GG3 tiene no respuesta: la media de cada localidad tiene que caer en la escala."""
    r = M.responder_catalogo("GG3")
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
    """DI-CO6: VS8 junta tres años; GG3 solo 2022-2023 (DI-AR5)."""
    tres, dos = M.responder_catalogo("VS8"), M.responder_catalogo("GG3")
    assert tres["anios"] == [2022, 2023, 2024] and dos["anios"] == [2022, 2023]
    assert tres["encuestados_mediana_localidad"] > 200 > dos["encuestados_mediana_localidad"] > 100
    assert "2022, 2023 y 2024" in tres["fuente"]
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


def test_sin_grupo_de_educacion():
    """DI-CO5: la población 2022-2024 no empareja por educación."""
    assert "educacion" not in mo.GRUPOS and "educacion" not in M.responder_catalogo("VS8")["grupos"]


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
