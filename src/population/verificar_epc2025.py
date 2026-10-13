"""
src/population/verificar_epc2025.py

Paso 1 para juntar la EPC 2025 (DATA_INVENTORY §13.9): el archivo de 2025 no trae etiquetas de valor, así que cada
pregunta del catálogo se verifica contra el formulario de 2025 en PDF. Para cada una: su código en 2025 (inventario), el
texto y las opciones del formulario, si las etiquetas y los códigos son los del catálogo, y si los datos traen códigos que
el formulario no nombra.

Uso:
    python src/population/verificar_epc2025.py

Escribe `data/processed/epc_armonizado/verificacion_2025.csv` (solo metadatos: códigos, textos del formulario público y
conteos; ningún microdato) y su resumen.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-V25-1. **Cómo se leen las opciones.** El formulario las trae de dos formas: una por línea («o 1: Buen camino») o una fila
    de etiquetas y debajo una fila de números («Nada orgulloso … Muy orgulloso» / «1 2 3 4 5»). En las baterías, la fila de
    etiquetas va una sola vez en la cabecera (`ECO_*`); se toma la última cabecera antes del ítem, y se marca para revisar.
DI-V25-2. **Cuándo coincide.** Si las opciones vienen una por línea, se compara cada código con su etiqueta, normalizada
    como en `armonizar_epc` (DI-AR1). Si vienen en fila, se compara la fila entera con las etiquetas del catálogo unidas en
    orden: así no hace falta adivinar dónde termina cada etiqueta. Los números de la fila deben ser los de la escala.
DI-V25-3. **Los códigos de «no sabe» o «no aplica»** (90, 98, 99…) no cuentan para la escala, como en el catálogo.
DI-V25-4. **El resultado es una propuesta, no la decisión.** Lo que no coincide exacto, o viene de una cabecera de
    batería, queda «a revisar»; la decisión final por pregunta la toma una persona leyendo el formulario y se anota en
    `REVISION_MANUAL`, con su razón.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population import armonizar_epc as ae             # noqa: E402
from src.population import epc_bcv as eb                   # noqa: E402
from src.population import poblacion_epc as pe            # noqa: E402

FORMULARIO = "Encuesta de Percepción Ciudadana/Formularios 2014 - 2025/EPC2025_Formulario.pdf"
SALIDA = ae.SALIDA / "verificacion_2025.csv"
NO_ESCALA = {88, 89, 90, 97, 98, 99}                                            # DI-V25-3
#: DI-V25-4: decisiones de la revisión manual, por variable del catálogo: (¿entra?, razón).
_SAT = "misma escala de satisfacción 1-5; 2025 rotula también los puntos intermedios"
_GOB = "misma escala, pero evalúa al gobierno de turno: se junta solo 2024-2025 (Galán, DI-AR5)"
REVISION_MANUAL: dict[str, tuple[bool, str]] = {
    **{f"SP{i}": (True, _SAT + "; 90 = no recibe el servicio") for i in range(1, 7)},
    **{v: (True, _SAT) for v in ("MA3_1", "MA3_2", "MA3_3")},
    "CR2": (True, _SAT + "; «la oferta cultural que hay» pasa a «actividades culturales»"),
    "CR4": (True, _SAT + "; «la oferta recreativa y deportiva» pasa a «actividades recreativas o deportivas»"),
    "MV13_10": (True, _SAT + "; «los bicicarriles» pasa a «estado de bicicarriles»"),
    "MV13_11": (True, _SAT + "; «los andenes» pasa a «estado de andenes»"),
    **{v: (True, "mismas puntas, 1 Nada y 5 Totalmente; 2025 rotula los puntos intermedios") for v in ("CO1_1", "CO1_2", "CO1_3")},
    "RC3_1": (True, "mismas puntas, 1 Muy mal y 5 Muy bien; «cuidado y respeto» pasa a «cuidado y uso» de los espacios públicos"),
    "RC3_2": (True, "mismas puntas, 1 Muy mal y 5 Muy bien; «respeto a» pasa a «cumplimiento por» las normas de tránsito"),
    "RC3_3": (True, "mismas puntas, 1 Muy mal y 5 Muy bien; mismo texto"),
    "VS15": (True, "mismo sí/no; el formulario dice «víctima de algún DMC_1», un marcador que se rellena con «delito»"),
    "CC9": (True, "mismo sí/no"),
    **{v: (True, _GOB) for v in ("GG3", "CC5A")},
    **{v: (True, _GOB + "; 1 Nada y 5 Totalmente, como en 2023") for v in ("MICE1", "MICE2", "MICE3")},
    **{v: (False, "cambiaron las puntas: de «Baja / Alta» a «Nada probable / Totalmente probable»")
       for v in ("RC5_6", "RC5_16", "RC5_17")},
    "CV5": (False, "cambió la etiqueta del punto 4: «Satisfecho» pasa a «Algo satisfecho»"),
}


def texto_formulario() -> str:
    from pypdf import PdfReader
    r = PdfReader(str(eb.resolver_dir_bcv().parent / FORMULARIO))
    return "\n".join(pg.extract_text() or "" for pg in r.pages)


def bloques(t: str) -> dict[str, str]:
    """Cada código «XXX_n:» con el texto hasta el siguiente código o encabezado de pregunta."""
    marcas = list(re.finditer(r"(?m)^\s*([A-Z]{2,4}_\d+[A-Z]?(?:_\d+)?):", t))
    out = {}
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(t)
        cuerpo = t[m.end():fin]
        corte = re.search(r"\n\s*\|\s*(PRIORITARIA|OPCIONAL|COMPLEMENTARIA)|\n\s*\|\|", cuerpo)
        out.setdefault(m.group(1), cuerpo[:corte.start()] if corte else cuerpo)
    return out


def opciones_por_linea(b: str) -> dict[int, str]:
    return {int(c): e.strip() for c, e in re.findall(r"(?m)^\s*o?\s*(\d{1,2})\s*:\s*(.+?)\s*$", b)}


def fila_de_numeros(b: str) -> tuple[str, list[int]] | None:
    """(texto de etiquetas antes de la fila de números, los números). None si no hay fila."""
    lineas = b.split("\n")
    for i, l in enumerate(lineas):
        if re.fullmatch(r"\s*(\d{1,2}\s+){1,9}\d{1,2}\s*", l):
            nums = [int(x) for x in l.split()]
            antes = "\n".join(lineas[:i])
            etq = re.split(r"\[[^\]]*\]", antes)[-1]                            # lo que sigue a la última [instrucción]
            return etq, nums
    return None


def cabecera_bateria(t: str, codigo: str) -> str:
    """DI-V25-1: la última línea de etiquetas de una batería antes del ítem."""
    i = t.find(codigo + ":")
    previo = t[:i]
    cands = re.findall(r"(?m)^\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ()]+){2,})\s*$", previo[-2500:])
    return cands[-1] if cands else ""


def comparar(ficha: dict, b: str, t: str, codigo: str) -> dict:
    esc = list(ficha["escala"])
    etq_cat = {int(k): v for k, v in ficha["etiquetas"].items() if int(k) in esc}
    por_linea = {c: e for c, e in opciones_por_linea(b).items() if c not in NO_ESCALA}
    if por_linea and set(por_linea) >= set(esc):
        iguales = all(ae._norm(por_linea[c]) == ae._norm(etq_cat[c]) for c in esc)
        return {"forma": "una por línea", "opciones_2025": json.dumps({c: por_linea[c] for c in sorted(por_linea)},
                                                                     ensure_ascii=False),
                "coincide": iguales and set(por_linea) == set(esc), "a_revisar": not iguales or set(por_linea) != set(esc)}
    fila = fila_de_numeros(b)
    if fila:
        texto, nums = fila
        nums = [n for n in nums if n not in NO_ESCALA]
        bateria = not ae._norm(texto)
        if bateria:
            texto = cabecera_bateria(t, codigo)
        unidas = ae._norm(" ".join(etq_cat[c] for c in esc))
        lo_que_dice = ae._norm(texto)
        lo_que_dice = re.sub(r"\b(NO SABE NO RESPONDE|NO SABE|NO RESPONDE|NO APLICA|NO RECIBIO|NO LO CONOCE|NO TIENE OPINION)\b",
                             "", lo_que_dice).strip()
        lo_que_dice = " ".join(lo_que_dice.split())
        return {"forma": "batería" if bateria else "fila", "opciones_2025": f"{texto.strip()} | {nums}",
                "coincide": nums == esc and lo_que_dice == unidas, "a_revisar": bateria or not (nums == esc and lo_que_dice == unidas)}
    return {"forma": "no encontrada", "opciones_2025": "", "coincide": False, "a_revisar": True}


def verificar() -> pd.DataFrame:
    inv = pd.read_csv(ae.INVENTARIO)
    cat, _ = pe.catalogo()
    t = texto_formulario()
    bl = bloques(t)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = pd.read_stata(eb.archivo_del_anio(2025), convert_categoricals=False)
    col = {c.upper(): c for c in d.columns}
    filas = []
    for f in cat:
        v = f["variable"]
        fila = inv[(inv.variable == v) & (inv.anio == 2025) & (inv.estado == "ok")]
        cod = str(fila.codigo.iloc[0]) if len(fila) else None
        base = {"variable": v, "pregunta_catalogo": f["pregunta"], "codigo_2025": cod}
        if cod is None or cod.upper() not in col:
            filas.append({**base, "resultado": "sin código en 2025"})
            continue
        b = bl.get(cod) or bl.get(cod.upper())
        if b is None:
            filas.append({**base, "resultado": "código no está en el formulario"})
            continue
        c = comparar(f, b, t, cod)
        presentes = set(pd.to_numeric(d[col[cod.upper()]], errors="coerce").dropna().astype(int))
        sobran = sorted(presentes - set(f["escala"]) - NO_ESCALA)
        preg25 = " ".join(re.split(r"\[", b)[0].split())
        sim = difflib.SequenceMatcher(None, ae._norm(f["pregunta"]), ae._norm(preg25)).ratio()
        res = "coincide" if c["coincide"] and not sobran else "a revisar"
        if v in REVISION_MANUAL:
            res = "entra (revisión manual)" if REVISION_MANUAL[v][0] else "no entra (revisión manual)"
        filas.append({**base, "pregunta_2025": preg25[:300], "similitud_texto": round(sim, 2), **c,
                      "codigos_datos_fuera_de_escala": " ".join(map(str, sobran)), "resultado": res,
                      "razon_manual": REVISION_MANUAL.get(v, (None, ""))[1]})
    return pd.DataFrame(filas)


def main() -> int:
    r = verificar()
    ae.SALIDA.mkdir(parents=True, exist_ok=True)
    r.to_csv(SALIDA, index=False, encoding="utf-8")
    print(r.resultado.value_counts().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
