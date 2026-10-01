"""
tests/test_banco.py

Pruebas de src/experiments/banco.py. Con un modelo simulado: ninguna llama a la API. Las que
leen las fuentes reales solo leen metadatos (textos y categorías), y se omiten si no están.
Se ejecuta directo:  python tests/test_banco.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import banco as ba
from src.experiments import experimento9 as e9

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


CATS = "1=Totalmente en desacuerdo; 2=En desacuerdo; 3=Ni lo uno ni lo otro; 4=De acuerdo; 5=Totalmente de acuerdo; 99=No sabe"


def j(**d):
    return json.dumps(d)


def test_parsear_acepta_una_util_y_una_descartada():
    r = ba.parsear(j(opinion=True, electoral=False, pregunta_pagina="¿Qué tan de acuerdo está con X?",
                     codigos_favorables=[4, 5], tema="x"), CATS)
    assert r["util"] and r["codigos_favorables"] == [4, 5]
    r = ba.parsear(j(opinion=False, electoral=False, pregunta_pagina="", codigos_favorables=[], tema="conducta"), CATS)
    assert r is not None and not r["util"]
    r = ba.parsear(j(opinion=True, electoral=True, pregunta_pagina="", codigos_favorables=[]), CATS)
    assert r is not None and not r["util"]


def test_parsear_rechaza_codigos_que_no_existen_o_faltantes():
    malos = [
        j(opinion=True, electoral=False, pregunta_pagina="¿X?", codigos_favorables=[6]),       # no existe
        j(opinion=True, electoral=False, pregunta_pagina="¿X?", codigos_favorables=[]),        # útil sin favorables
        j(opinion=True, electoral=False, pregunta_pagina="", codigos_favorables=[4]),          # útil sin pregunta
        j(opinion="sí", electoral=False, pregunta_pagina="¿X?", codigos_favorables=[4]),
        "no es json",
    ]
    assert all(ba.parsear(m, CATS) is None for m in malos)


def test_el_prompt_no_lleva_resultados_solo_texto_y_categorias():
    """DI-BA2."""
    p = ba.prompt({"texto": "¿X?", "categorias": CATS, "modulo": "Democracia", "texto_incompleto": True})
    assert "¿X?" in p and CATS in p and "cortado" in p
    assert not any(w in p.lower() for w in ("porcentaje", "media", "%"))


def test_la_clasificacion_con_el_simulado_y_la_cache():
    df = pd.DataFrame([{"id": "A", "texto": "¿A?", "categorias": CATS, "modulo": "", "texto_incompleto": False,
                        "fuente": "x", "independiente": True},
                       {"id": "B", "texto": "¿B?", "categorias": "1=Sí; 2=No", "modulo": "", "texto_incompleto": False,
                        "fuente": "x", "independiente": True}])
    llamadas = {"n": 0}
    sim = ba.modelo_simulado()

    def contar(*a):
        llamadas["n"] += 1
        return sim(*a)
    with tempfile.TemporaryDirectory() as tmp:
        cache = e9.Cache(Path(tmp) / "c.json")
        cl = ba.clasificar(df, contar, cache, "simulado")
        ba.clasificar(df, contar, cache, "simulado")
    assert llamadas["n"] == 2 and cl.util.all() and json.loads(cl.codigos_favorables[0]) == [5]


def test_las_candidatas_reales_salen_y_metro_y_corredor_quedan_marcados_como_vistos():
    if not ba.DDI_ECP.exists() or not ba.INVENTARIO.exists():
        print("         (sin las fuentes en esta máquina: se omite)")
        return
    df = ba.candidatas()
    assert df.id.is_unique and set(df.fuente) == {"ECP DANE", "EPC armonizada", "EPC coyuntura", "Biblioteca CNC"}
    vistos = set(df[df.visto].id)
    assert vistos == {"CNC_METRO", "CNC_CORREDOR"}
    assert not df[df.fuente == "ECP DANE"].modulo.str.startswith("Elecciones").any()          # DI-BA4
    assert (df.anio != 2025).all()                                                           # DI-BA1


def test_el_sorteo_cumple_las_tres_reglas_y_es_reproducible():
    """DI-BA5."""
    ruta = ba.SALIDA / "clasificadas.csv"
    if not ruta.exists():
        print("         (sin la clasificación en esta máquina: se omite)")
        return
    cl = pd.read_csv(ruta)
    s = ba.sortear(cl)
    assert s.equals(ba.sortear(cl))                                                  # misma semilla, mismo sorteo
    assert not s.id.isin(ba.EXCLUIDAS).any()                                         # regla 1
    assert set(s.ambito) == {"Bogotá", "general"} and (s[s.fuente == "ECP DANE"].ambito == "general").all()   # regla 2
    assert (s.groupby("familia").conjunto.nunique() == 1).all()                      # regla 3: la familia no se parte
    g = s[s.conjunto == "guardado"]
    assert g.independiente.all() and not g.id.isin(["CNC_METRO", "CNC_CORREDOR"]).any()
    with tempfile.TemporaryDirectory() as tmp:
        s.to_csv(Path(tmp) / "s.csv", index=False)
        assert not ba.practica(Path(tmp) / "s.csv").id.isin(g.id).any()            # la puerta de la práctica


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Banco — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
