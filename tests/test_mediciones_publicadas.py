"""
tests/test_mediciones_publicadas.py

Pruebas del registro de encuestas públicas (`config/mediciones_publicadas.csv`, plan v3 Fase 2, `REGISTRO_ENCUESTAS_FASE2.md`).
Se ejecuta directo:  python tests/test_mediciones_publicadas.py
"""

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

FALLOS = []
T = pd.read_csv(RAIZ / "config" / "mediciones_publicadas.csv", dtype=str)
CAMPOS = ("id", "serie", "concepto", "encuestadora", "mes", "fecha_publicacion", "campo_inicio", "campo_fin", "poblacion",
          "muestra_total", "muestra_bogota", "metodo", "margen_error", "texto_pregunta", "opciones", "lo_que_se_cuenta", "valor",
          "fuente", "url", "verificacion", "comparabilidad", "fecha_verificacion")


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_tiene_los_campos_del_plan_y_ninguno_vacio():
    assert all(c in T.columns for c in CAMPOS)
    assert not T[list(CAMPOS)].isna().any().any(), "un dato que no está se marca «pendiente», no se deja vacío"


def test_una_fila_por_medicion():
    assert T.id.is_unique and not T.duplicated(["serie", "mes"]).any()


def test_cada_dato_dice_de_donde_salio():
    ok = ("nota de prensa", "nota de prensa (vía resumen del buscador)", "informe original", "microdato propio")
    assert all(v in ok or v.startswith("pendiente de verificación") for v in T.verificacion)


def test_una_serie_es_un_solo_concepto_y_una_encuestadora():
    for s, g in T.groupby("serie"):
        assert g.concepto.nunique() == 1 and g.encuestadora.nunique() == 1, s


def test_ninguna_fecha_de_campo_inventada():
    """Plan v3 §6.2: no inferir el campo de la fecha de publicación; si está, va antes de ella."""
    c = T[T.campo_fin != "pendiente"]
    assert (pd.to_datetime(c.campo_fin) <= pd.to_datetime(c.fecha_publicacion)).all()


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Registro de encuestas — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
