"""
tests/test_electoral.py

Pruebas de src/population/electoral.py (D16). Las de lógica usan archivos
inventados; la última usa los reales si la carpeta existe en esta máquina.
Se ejecuta directo:  python tests/test_electoral.py
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.population import electoral as el

FALLOS = []
LOC = el.localidades()


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def falla_con(error, f, *a, texto=None):
    try:
        f(*a)
    except error as e:
        assert texto is None or texto in str(e), str(e)
        return
    raise AssertionError(f"no levantó {error.__name__}")


def mesas_2022():
    """Dos mesas en Usaquén, una en Corferias; con blancos y nulos."""
    filas = [(1, "01", "001", "GUSTAVO PETRO", 100), (1, "01", "001", "RODOLFO HERNANDEZ", 50),
             (1, "01", "001", "VOTOS EN BLANCO", 5), (1, "01", "002", "GUSTAVO PETRO", 80),
             (1, "01", "002", "VOTOS NULOS", 3), (90, "00", "001", "FEDERICO GUTIERREZ", 40)]
    return pd.DataFrame(filas, columns=["zona", "puesto", "mesa", "nombre", "votos"])


# --- utilidades --------------------------------------------------------------

def test_normalizar():
    assert el.normalizar("Rodolfo Hernández") == "RODOLFO HERNANDEZ"
    assert el.normalizar("VOTOS EN BLANCO .") == "VOTOS EN BLANCO"
    assert el.normalizar("  enrique   GÓMEZ  martínez ") == "ENRIQUE GOMEZ MARTINEZ"
    assert el.normalizar("ENRIQUE PEÑALOSA") == "ENRIQUE PENALOSA"


def test_la_carpeta_se_exige_y_no_puede_estar_en_el_repo():
    viejo = os.environ.pop("BSS_ELECTORAL_DIR", None)
    try:
        falla_con(el.ElectoralError, el.resolver_dir, None, texto="BSS_ELECTORAL_DIR")
        falla_con(el.ElectoralError, el.resolver_dir, str(el.RAIZ / "data"), texto="dentro del repositorio")
        tmp = tempfile.mkdtemp()
        assert el.resolver_dir(tmp) == Path(tmp).resolve()
    finally:
        if viejo is not None:
            os.environ["BSS_ELECTORAL_DIR"] = viejo


def test_todas_las_opciones_tienen_clave_estable_entre_anios():
    petro = {a: [v for v in op.values() if v[0] == "petro"] for a, op in el.OPCIONES.items()}
    assert petro[2014] == [] and len(petro[2018]) == len(petro[2022]) == 1
    for anio, op in el.OPCIONES.items():
        assert all(k == el.normalizar(k) for k in op), f"{anio}: clave sin normalizar"
        assert all(t in {"candidato", "blanco", "nulo", "no_marcado", "promotores_blanco"}
                   for _, _, t, _ in op.values())


# --- agregación --------------------------------------------------------------

def test_agregar_conserva_los_votos_y_separa_las_zonas_especiales():
    v, z = el.agregar(mesas_2022(), 2022, LOC)
    assert v.votos.sum() == mesas_2022().votos.sum() == z.votos_total.sum()
    usaquen = z[z.zona == 1].iloc[0]
    assert usaquen.localidad == "Usaquén" and usaquen.cod_loc == 1
    assert usaquen.mesas == 2 and usaquen.puestos == 1
    assert usaquen.votos_total == 238 and usaquen.votos_candidatos == 230      # sin blanco ni nulos
    corferias = z[z.zona == 90].iloc[0]
    assert pd.isna(corferias.cod_loc) and corferias.localidad == "Puesto censo (Corferias)"
    petro = v[(v.zona == 1) & (v.clave == "petro")].iloc[0]
    assert petro.votos == 180 and petro.opcion == "Gustavo Petro" and petro.tipo == "candidato"
    assert set(v[v.zona == 1].tipo) == {"candidato", "blanco", "nulo"}


def test_un_nombre_desconocido_detiene_todo():
    m = mesas_2022()
    m.loc[0, "nombre"] = "CANDIDATO INVENTADO"
    falla_con(el.ElectoralError, el.agregar, m, 2022, LOC, texto="CANDIDATO INVENTADO")


def test_una_zona_que_no_es_localidad_detiene_todo():
    m = mesas_2022()
    m.loc[0, "zona"] = 45
    falla_con(el.ElectoralError, el.agregar, m, 2022, LOC, texto="45")


def test_votos_negativos_detienen_todo():
    m = mesas_2022()
    m.loc[0, "votos"] = -1
    falla_con(el.ElectoralError, el.agregar, m, 2022, LOC)


def test_mesas_con_el_mismo_numero_en_puestos_distintos_se_cuentan_aparte():
    m = mesas_2022()
    m.loc[3:4, "puesto"] = "02"        # la mesa 002 pasa a otro puesto...
    m.loc[3:4, "mesa"] = "001"         # ...con el mismo número que la 001 del puesto 01
    _, z = el.agregar(m, 2022, LOC)
    assert z[z.zona == 1].iloc[0].mesas == 2 and z[z.zona == 1].iloc[0].puestos == 2


# --- lectores ----------------------------------------------------------------

def test_el_lector_2022_filtra_bogota_y_limpia_nombres():
    tmp = Path(tempfile.mkdtemp())
    try:
        filas = ["DEP;ZONA;PUESTO;MESA;CANNOMBRE;VOTOS",
                 "16;01;01;001;GUSTAVO PETRO;10", "16;90;00;001;VOTOS EN BLANCO .;2",
                 "01;01;01;001;GUSTAVO PETRO;999"]                      # Antioquia: fuera
        (tmp / el.FUENTES[2022]["archivo"]).write_bytes("\n".join(filas).encode("latin-1"))
        m = el.leer_2022(tmp)
        assert len(m) == 2 and m.votos.sum() == 12
        assert list(m.nombre) == ["GUSTAVO PETRO", "VOTOS EN BLANCO"]
        assert list(m.zona) == [1, 90]
    finally:
        shutil.rmtree(tmp)


def test_sin_filas_de_bogota_es_un_error():
    df = pd.DataFrame({"DEP": [1], "Z": [1], "P": [1], "M": [1], "N": ["X"], "V": [1]})
    falla_con(el.ElectoralError, el._estandar, df, "DEP", "Z", "P", "M", "N", "V", texto="Bogotá")


# --- verificación (DI-EL7) ---------------------------------------------------

def _dta_2018(tmp):
    x = pd.DataFrame({
        "codmpio": [11001] * 6 + [5001],
        "nombres": ["GUSTAVO FRANCISCO", "IVAN", "PROMOTORES VOTO EN BLANCO", "", "", "", "IVAN"],
        "primer_apellido": ["PETRO", "DUQUE", "", "TARJETAS NO MARCADAS", "VOTOS NULOS",
                            "VOTOS EN BLANCO", "DUQUE"],
        "votos": [100.0, 90.0, 4.0, 2.0, 3.0, 6.0, 999.0]})
    x.to_stata(tmp / el.MUNICIPALES[2018], write_index=False)


def test_los_totales_municipales_se_leen_por_opcion():
    tmp = Path(tempfile.mkdtemp())
    try:
        _dta_2018(tmp)
        t = el.totales_municipales(tmp, 2018)
        assert t == {"petro": 100, "duque": 90, "promotores_blanco": 4, "no_marcado": 2,
                     "nulo": 3, "blanco": 6}, t
    finally:
        shutil.rmtree(tmp)


def test_la_verificacion_acepta_solo_las_diferencias_conocidas():
    v = pd.DataFrame({"clave": ["petro", "duque", "blanco"], "votos": [73, 117, 6]})
    r = el.verificar(v, {"petro": 100, "duque": 90, "blanco": 6}, 2018)       # −27 y +27
    assert r["coincide"] and len(r["diferencias_conocidas"]) == 2
    falla_con(el.ElectoralError, el.verificar, v, {"petro": 100, "duque": 90, "blanco": 6}, 2022,
              texto="no explicadas")
    falla_con(el.ElectoralError, el.verificar, v.assign(votos=[73, 117, 7]),
              {"petro": 100, "duque": 90, "blanco": 6}, 2018, texto="blanco")


# --- Congreso 2018 (DI-EL8, DI-EL9) -------------------------------------------

def _csv_congreso(tmp, filas, corp="camara"):
    cab = "NCircunscripcion,NDepto,NMpio,ZZ,PP,Npuesto,mesa,partido,candidato,votos"
    (tmp / el.CONGRESO[corp]).write_text("\n".join([cab] + filas), encoding="utf-8")


def test_el_congreso_filtra_bogota_y_tipifica_los_especiales():
    tmp = Path(tempfile.mkdtemp())
    try:
        _csv_congreso(tmp, [
            "TERRITORIAL DEPARTAMENTAL,BOGOTA D.C.,BOGOTA. D.C.,1,01,USAQUEN,1,PARTIDO ALIANZA VERDE,ANA PEREZ,10",
            "TERRITORIAL DEPARTAMENTAL,BOGOTA D.C.,BOGOTA. D.C.,1,01,USAQUEN,1,PARTIDO ALIANZA VERDE,,4",
            "TERRITORIAL DEPARTAMENTAL,BOGOTA D.C.,BOGOTA. D.C.,1,01,USAQUEN,1,,VOTOS EN BLANCO,3",
            "TERRITORIAL DEPARTAMENTAL,ANTIOQUIA,MEDELLIN,1,01,X,1,PARTIDO ALIANZA VERDE,ANA,999",
        ])
        m = el.leer_congreso(tmp, "camara")
        assert len(m) == 3 and m.votos.sum() == 17
        assert set(m.tipo) == {"partido", "blanco"} and set(m.circunscripcion) == {"territorial"}
        v, z = el.agregar_congreso(m, "camara", LOC)
        verde = v[v.partido == "PARTIDO ALIANZA VERDE"].votos.iloc[0]
        assert verde == 14, verde                        # lista y candidato juntos
        assert z.votos_partidos.iloc[0] == 14 and z.votos_total.iloc[0] == 17
    finally:
        shutil.rmtree(tmp)


def test_las_filas_identicas_se_suman_no_se_descartan():
    """DI-EL8: dos candidatos sin nombre con 1 voto en la misma mesa son dos votos."""
    tmp = Path(tempfile.mkdtemp())
    try:
        fila = "INDIGENAS,BOGOTA D.C.,BOGOTA. D.C.,1,01,USAQUEN,56,MOVIMIENTO ALTERNATIVO INDIGENA Y SOCIAL MAIS,,1"
        _csv_congreso(tmp, [fila, fila])
        v, _ = el.agregar_congreso(el.leer_congreso(tmp, "camara"), "camara", LOC)
        assert v.votos.sum() == 2
    finally:
        shutil.rmtree(tmp)


def test_una_circunscripcion_o_un_especial_desconocido_detiene_todo():
    tmp = Path(tempfile.mkdtemp())
    try:
        _csv_congreso(tmp, ["INVENTADA,BOGOTA D.C.,BOGOTA. D.C.,1,01,X,1,PARTIDO X,A,1"])
        falla_con(el.ElectoralError, el.leer_congreso, tmp, "camara", texto="INVENTADA")
        _csv_congreso(tmp, ["NACIONAL,BOGOTA D.C.,BOGOTA. D.C.,1,01,X,1,,VOTOS RAROS,1"], corp="senado")
        falla_con(el.ElectoralError, el.leer_congreso, tmp, "senado", texto="VOTOS RAROS")
    finally:
        shutil.rmtree(tmp)


def test_un_nombre_truncado_se_empareja_con_el_completo():
    a = {"PARTIDO FUERZA ALTERNATIVA REVOLUCIONARIA DEL COMU": 10, "PARTIDO X": 5}
    b = {"PARTIDO FUERZA ALTERNATIVA REVOLUCIONARIA DEL COMUN": 10, "PARTIDO X": 5}
    pares = el._cruzar_nombres(a, b)
    assert pares["PARTIDO FUERZA ALTERNATIVA REVOLUCIONARIA DEL COMU"] == (10, 10) and len(pares) == 2
    # un prefijo corto NO cuenta como el mismo partido
    assert el._cruzar_nombres({"PARTIDO": 1}, {"PARTIDO LIBERAL": 1})["PARTIDO"] == (1, None)


def test_congreso_real_verificado():
    carpeta = os.environ.get("BSS_ELECTORAL_DIR") or r"C:\Users\User\Desktop\CNC_datos"
    if not (Path(carpeta) / el.CONGRESO["camara"]).exists():
        print("         (sin los archivos del Congreso en esta máquina: se omite)")
        return
    v, z, meta = el.construir_congreso(Path(carpeta))
    ver = meta["verificacion"]
    assert ver["camara"]["territorial"]["coincide"] is True and ver["camara"]["indigena"]["coincide"] is True
    assert ver["camara"]["afro"]["coincide"] == "diferencia conocida"
    assert ver["senado"]["nacional"]["coincide"] == "aproximado" and ver["senado"]["indigena"]["coincide"] is None
    tot = z.groupby(["corporacion", "circunscripcion"]).votos_total.sum()
    assert tot[("camara", "territorial")] == 2_653_552 and tot[("camara", "indigena")] == 74_176
    assert z[z.cod_loc.notna()].groupby("corporacion").cod_loc.nunique().eq(20).all()


# --- datos reales ------------------------------------------------------------

def test_2022_real_cuadra_con_el_archivo_municipal():
    carpeta = os.environ.get("BSS_ELECTORAL_DIR") or r"C:\Users\User\Desktop\CNC_datos"
    if not (Path(carpeta) / el.FUENTES[2022]["archivo"]).exists():
        print("         (sin los archivos electorales en esta máquina: se omite)")
        return
    v, z, meta = el.construir(Path(carpeta), anios=(2022,))
    assert meta["verificacion"][2022]["coincide"]
    assert z.votos_total.sum() == 3_801_013 and z.zona.nunique() == 22
    assert v.votos.sum() == z.votos_total.sum()
    assert z[z.cod_loc.notna()].cod_loc.nunique() == 20


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in globals().items() if k.startswith("test_")]
    print(f"Resultados electorales — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
