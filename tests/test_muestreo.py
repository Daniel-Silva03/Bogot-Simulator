"""
tests/test_muestreo.py

Pruebas del muestreo de agentes (src/population/muestreo.py), que cierra
A16: cómo se eligen los N agentes del prototipo a partir del receptor
completo.

Lo que hay que verificar no es que el código corra, sino que efectivamente
CORRIJA el sesgo que motivó todo esto. El test central construye un
receptor deliberadamente sesgado —localidades pequeñas sobre-muestreadas,
como en Multipropósito— con factores de expansión que codifican la
realidad, y exige que la muestra recupere las proporciones reales.

Ejecutar con:  python3 tests/test_muestreo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.population.muestreo import (
    MuestreoError,
    diagnostico_territorial,
    muestrear,
    _pps_sistematico,
)

# Poblaciones reales aproximadas (18+), en miles: dos localidades grandes,
# dos chicas. El receptor de prueba invierte las proporciones, como hace la
# encuesta real.
POBLACION_REAL = {"Suba": 1_074_193, "Bosa": 557_654, "Santa Fe": 81_201, "Sumapaz": 2_834}
MARGINAL = pd.DataFrame({
    "localidad": list(POBLACION_REAL),
    "poblacion": list(POBLACION_REAL.values()),
})


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def receptor_sesgado(n_por_localidad=2000, seed=0):
    """Receptor con el MISMO número de personas por localidad —el sesgo
    máximo posible— y factores de expansión que restauran la realidad:
    cada persona 'representa' a poblacion_real / n_por_localidad."""
    rng = np.random.default_rng(seed)
    filas = []
    for loc, pob in POBLACION_REAL.items():
        peso = pob / n_por_localidad
        for _ in range(n_por_localidad):
            filas.append((loc, peso))
    df = pd.DataFrame(filas, columns=["localidad", "factor_expansion"])
    df["agent_id"] = np.arange(len(df))
    df["edad"] = rng.integers(18, 85, len(df))
    df["sexo"] = rng.choice(["F", "M"], len(df))
    df["estrato"] = rng.integers(1, 7, len(df))
    df["nivel_educativo"] = rng.integers(0, 6, len(df))
    return df


RECEPTOR = receptor_sesgado()


def test_ponderado_corrige_el_sesgo():
    """El test que justifica el módulo entero."""
    print("\n[test_ponderado_corrige_el_sesgo]")

    def distancia_total(diag):
        """Suma de |share observado - share real| / 2: 0 = perfecto,
        1 = no se solapan. Resume el sesgo en un número, sin que lo
        domine una localidad diminuta."""
        n = diag["observado"].sum()
        return float((diag["observado"] / n - diag["esperado"] / n).abs().sum() / 2)

    crudo = diagnostico_territorial(RECEPTOR.sample(1000, random_state=1), MARGINAL)
    print(crudo.to_string(index=False))
    d_crudo = distancia_total(crudo)
    _assert(d_crudo > 0.3,
            f"el receptor de prueba está fuertemente sesgado sin corregir "
            f"(distancia al marginal real: {d_crudo:.3f}) — es el problema a resolver")

    r = muestrear(RECEPTOR, 1000, seed=42, marginal=MARGINAL)
    _assert(r.metodo == "ponderado", "con factor_expansion presente elige muestreo ponderado")

    diag = diagnostico_territorial(r.agentes, MARGINAL)
    print(diag.to_string(index=False))
    d_pond = distancia_total(diag)
    _assert(d_pond < 0.02,
            f"tras ponderar, la muestra reproduce el marginal real "
            f"(distancia {d_pond:.3f} contra {d_crudo:.3f} sin corregir)")

    # El criterio por localidad solo tiene sentido donde el valor esperado
    # da para juzgarlo: con 1,7 agentes esperados en Sumapaz, obtener 0 o 3
    # es ruido de muestreo, no sesgo del método.
    grandes = diag[diag["esperado"] >= 10]
    peor = max(abs(grandes["sesgo"] - 1))
    _assert(peor < 0.2,
            f"y ninguna localidad con cuota apreciable se desvía más de 20% "
            f"(desvío máximo {peor:.2f} sobre {len(grandes)} localidades)")

    _assert(len(r.agentes) == 1000, "devuelve exactamente los 1.000 agentes pedidos")
    _assert(r.agentes["agent_id"].is_unique, "sin agentes repetidos")


def test_pps_es_proporcional_al_peso():
    """La propiedad que define al método: la probabilidad de inclusión de
    cada unidad es proporcional a su peso. Se verifica empíricamente sobre
    muchas repeticiones, que es la única forma honesta de comprobarlo."""
    print("\n[test_pps_es_proporcional_al_peso]")

    # Pesos elegidos para que ninguna unidad supere π=1 con este n: la
    # proporcionalidad solo puede cumplirse donde es alcanzable. Una unidad
    # con n·w/W > 1 es de certeza por definición, y ese caso lo cubre el
    # test siguiente.
    pesos = np.array([1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0])
    n, reps = 3, 4000
    conteo = np.zeros(len(pesos))
    for s in range(reps):
        idx, _ = _pps_sistematico(pesos, n, np.random.default_rng(s))
        conteo[idx] += 1

    observado = conteo / reps
    esperado = n * pesos / pesos.sum()
    error = np.abs(observado - esperado).max()
    for w, o, e in zip(pesos, observado, esperado):
        print(f"    peso {w:5.1f}: inclusión observada {o:.3f}  esperada {e:.3f}")
    _assert(error < 0.03,
            f"las probabilidades de inclusión siguen a los pesos (error máx {error:.3f})")


def test_unidades_de_certeza():
    """Una unidad cuyo peso supera W/n debe entrar siempre, y una sola vez.
    Sin tratarla aparte, el barrido sistemático la seleccionaría dos veces
    y la muestra saldría más chica de lo pedido."""
    print("\n[test_unidades_de_certeza]")

    pesos = np.array([1000.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    for s in range(20):
        idx, meta = _pps_sistematico(pesos, 3, np.random.default_rng(s))
        _assert_silencioso = (0 in idx) and len(idx) == 3 and len(set(idx)) == 3
        if not _assert_silencioso:
            raise AssertionError(f"semilla {s}: idx={idx}")
    _assert(True, "la unidad dominante entra siempre, una sola vez, y la muestra tiene el tamaño pedido")
    _assert(meta["unidades_certeza"] >= 1, "y queda registrada como unidad de certeza en la metadata")


def test_estratificado_cumple_cuotas():
    """Sin ponderador, la caída es estratificar por localidad contra el
    marginal. Las cuotas deben cumplirse exactamente y sumar n."""
    print("\n[test_estratificado_cumple_cuotas]")

    sin_peso = RECEPTOR.drop(columns=["factor_expansion"])
    r = muestrear(sin_peso, 1000, seed=7, marginal=MARGINAL)
    _assert(r.metodo == "estratificado",
            "sin factor_expansion pero con marginal, cae a estratificado (no a aleatorio)")

    diag = diagnostico_territorial(r.agentes, MARGINAL)
    print(diag.to_string(index=False))
    _assert(len(r.agentes) == 1000, "la muestra tiene exactamente 1.000 agentes")
    desvio = (diag["observado"] - diag["esperado"]).abs().max()
    _assert(desvio <= 1.0,
            f"cada localidad queda a menos de un agente de su cuota (desvío máx {desvio})")


def test_reproducibilidad():
    print("\n[test_reproducibilidad]")
    a = muestrear(RECEPTOR, 500, seed=3, marginal=MARGINAL).agentes
    b = muestrear(RECEPTOR, 500, seed=3, marginal=MARGINAL).agentes
    c = muestrear(RECEPTOR, 500, seed=4, marginal=MARGINAL).agentes
    _assert(a["agent_id"].tolist() == b["agent_id"].tolist(),
            "misma semilla produce exactamente la misma muestra")
    _assert(a["agent_id"].tolist() != c["agent_id"].tolist(),
            "semillas distintas producen muestras distintas")


def test_errores_explicitos():
    print("\n[test_errores_explicitos]")
    casos = [
        ("pedir más agentes de los que hay",
         lambda: muestrear(RECEPTOR.head(10), 100, seed=1, marginal=MARGINAL)),
        ("forzar 'ponderado' sin la columna de peso",
         lambda: muestrear(RECEPTOR.drop(columns=["factor_expansion"]), 10,
                           seed=1, metodo="ponderado", marginal=MARGINAL)),
        ("pesos nulos en el receptor",
         lambda: muestrear(RECEPTOR.assign(factor_expansion=np.nan), 10,
                           seed=1, marginal=MARGINAL)),
        ("pesos <= 0",
         lambda: muestrear(RECEPTOR.assign(factor_expansion=0.0), 10,
                           seed=1, marginal=MARGINAL)),
        ("n inválido",
         lambda: muestrear(RECEPTOR, 0, seed=1, marginal=MARGINAL)),
        ("método inexistente",
         lambda: muestrear(RECEPTOR, 10, seed=1, metodo="magia", marginal=MARGINAL)),
    ]
    for descripcion, fn in casos:
        try:
            fn()
            raise AssertionError(f"debería haber fallado: {descripcion}")
        except MuestreoError as e:
            print(f"  OK: falló como se esperaba — {descripcion}\n       ({str(e)[:95]})")


def test_metadata_para_reproducibilidad():
    """La sección 26 del prompt maestro: toda corrida debe quedar trazada."""
    print("\n[test_metadata_para_reproducibilidad]")
    r = muestrear(RECEPTOR, 300, seed=11, marginal=MARGINAL)
    print(r.reporte())
    for clave in ("n_receptor", "n_muestra", "seed_muestreo", "razon_metodo"):
        _assert(clave in r.metadata, f"la metadata registra '{clave}'")


if __name__ == "__main__":
    test_ponderado_corrige_el_sesgo()
    test_pps_es_proporcional_al_peso()
    test_unidades_de_certeza()
    test_estratificado_cumple_cuotas()
    test_reproducibilidad()
    test_errores_explicitos()
    test_metadata_para_reproducibilidad()
    print("\nTodos los tests pasaron.")
