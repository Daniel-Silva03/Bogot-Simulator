"""
tests/test_population_matching.py

Pruebas del hot-deck nearest-neighbour matching (src/population/matching.py).

Usa datos SINTÉTICOS pequeños y controlados a mano — no datos reales de
Multipropósito/BCV — precisamente para poder verificar por inspección que
el resultado es el esperado (Regla 2 del prompt maestro: nunca asumir que
algo funciona, verificarlo).

Ejecutar con:  python3 tests/test_population_matching.py
(Diseñado para correr también con pytest si está disponible: pytest tests/)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.population.matching import (
    hot_deck_match,
    NIVELES_RELAJACION,
    construir_escalera_relajacion,
)


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def test_caso_basico_match_exacto():
    """Caso donde cada bloque localidad+sexo del receptor tiene donante
    directo — todo debería resolverse en nivel 0."""
    print("\n[test_caso_basico_match_exacto]")

    receptor = pd.DataFrame({
        "agent_id": [1, 2, 3],
        "localidad": ["Suba", "Suba", "Kennedy"],
        "sexo": ["F", "M", "F"],
        "edad": [30, 45, 25],
        "estrato": [3, 2, 4],
        "nivel_educativo": [3, 2, 4],
    })

    donante = pd.DataFrame({
        "localidad": ["Suba", "Suba", "Suba", "Kennedy", "Kennedy"],
        "sexo": ["F", "F", "M", "F", "F"],
        "edad": [31, 60, 44, 26, 50],
        "estrato": [3, 3, 2, 4, 1],
        "nivel_educativo": [3, 1, 2, 4, 2],
        "confianza_institucional": [3.5, 1.0, 4.0, 4.5, 2.0],
    })

    resultado = hot_deck_match(receptor, donante, opinion_col="confianza_institucional")

    print(resultado.reporte())

    _assert((resultado.nivel_relajacion_usado == 0).all(),
            "todos los registros deberían resolverse en nivel 0 (match exacto disponible)")

    # agente 1: Suba+F, más cercano en (edad,estrato,educ) estandarizado
    # entre las dos donantes Suba+F (edad 31 vs 60) -> debería preferir la de edad 31
    fila1 = resultado.agentes.loc[resultado.agentes["agent_id"] == 1, "confianza_institucional"].iloc[0]
    _assert(fila1 == 3.5, f"agente 1 debería matchear con donante de edad más cercana (esperado 3.5, obtuvo {fila1})")

    # agente 2: Suba+M, solo hay un donante Suba+M -> debe ser ese
    fila2 = resultado.agentes.loc[resultado.agentes["agent_id"] == 2, "confianza_institucional"].iloc[0]
    _assert(fila2 == 4.0, f"agente 2 debería matchear con el único donante Suba+M (esperado 4.0, obtuvo {fila2})")


def test_relajacion_por_falta_de_sexo():
    """Caso donde el bloque localidad+sexo exacto no existe en el donante,
    pero sí existe la localidad con otro sexo -> debe caer a nivel 1."""
    print("\n[test_relajacion_por_falta_de_sexo]")

    receptor = pd.DataFrame({
        "agent_id": [1],
        "localidad": ["Chapinero"],
        "sexo": ["F"],
        "edad": [40],
        "estrato": [5],
        "nivel_educativo": [4],
    })

    donante = pd.DataFrame({
        "localidad": ["Chapinero", "Suba"],
        "sexo": ["M", "F"],  # no hay Chapinero+F en el donante
        "edad": [41, 40],
        "estrato": [5, 5],
        "nivel_educativo": [4, 4],
        "confianza_institucional": [2.5, 4.5],
    })

    resultado = hot_deck_match(receptor, donante, opinion_col="confianza_institucional")
    print(resultado.reporte())

    _assert(resultado.nivel_relajacion_usado[0] == 1,
            "debería caer a nivel 1 (relaja sexo, mantiene localidad)")
    fila = resultado.agentes["confianza_institucional"].iloc[0]
    _assert(fila == 2.5, f"debería matchear con el donante de Chapinero aunque sea sexo M (esperado 2.5, obtuvo {fila})")


def test_relajacion_total_nivel_2():
    """Caso extremo: ni siquiera la localidad existe en el donante ->
    debe caer a nivel 2 (solo distancia, sin restricción exacta) y quedar
    reportado en el resumen de relajación, no oculto."""
    print("\n[test_relajacion_total_nivel_2]")

    receptor = pd.DataFrame({
        "agent_id": [1],
        "localidad": ["Sumapaz"],
        "sexo": ["F"],
        "edad": [50],
        "estrato": [2],
        "nivel_educativo": [1],
    })

    donante = pd.DataFrame({
        "localidad": ["Suba", "Kennedy"],
        "sexo": ["M", "M"],
        "edad": [50, 20],
        "estrato": [2, 6],
        "nivel_educativo": [1, 5],
        "confianza_institucional": [3.0, 1.0],
    })

    resultado = hot_deck_match(receptor, donante, opinion_col="confianza_institucional")
    print(resultado.reporte())

    _assert(resultado.nivel_relajacion_usado[0] == 2,
            "debería caer a nivel 2 (sin match exacto de localidad ni sexo disponible)")
    _assert(resultado.resumen_relajacion[2] == 1,
            "el resumen de relajación debe reportar explícitamente el caso de nivel 2")
    fila = resultado.agentes["confianza_institucional"].iloc[0]
    _assert(fila == 3.0, f"debería matchear por distancia pura al más parecido (esperado 3.0, obtuvo {fila})")


def test_reproducibilidad():
    """Mismo input, misma semilla -> mismo resultado (sección 26 del prompt maestro)."""
    print("\n[test_reproducibilidad]")

    receptor = pd.DataFrame({
        "agent_id": range(20),
        "localidad": ["Suba"] * 20,
        "sexo": ["F"] * 20,
        "edad": np.random.default_rng(1).integers(18, 80, 20),
        "estrato": np.random.default_rng(2).integers(1, 6, 20),
        "nivel_educativo": np.random.default_rng(3).integers(0, 5, 20),
    })
    donante = pd.DataFrame({
        "localidad": ["Suba"] * 15,
        "sexo": ["F"] * 15,
        "edad": np.random.default_rng(4).integers(18, 80, 15),
        "estrato": np.random.default_rng(5).integers(1, 6, 15),
        "nivel_educativo": np.random.default_rng(6).integers(0, 5, 15),
        "confianza_institucional": np.random.default_rng(7).uniform(1, 5, 15),
    })

    r1 = hot_deck_match(receptor, donante, "confianza_institucional", random_state=42)
    r2 = hot_deck_match(receptor, donante, "confianza_institucional", random_state=42)

    _assert(
        np.allclose(r1.agentes["confianza_institucional"], r2.agentes["confianza_institucional"]),
        "misma semilla debe producir el mismo resultado exacto"
    )


def test_falta_columna_lanza_error():
    """Si falta una variable puente, debe fallar explícitamente (Regla 2:
    no inventar datos ni seguir silenciosamente con datos incompletos)."""
    print("\n[test_falta_columna_lanza_error]")

    receptor = pd.DataFrame({
        "agent_id": [1], "localidad": ["Suba"], "sexo": ["F"], "edad": [30],
        # falta "estrato" y "nivel_educativo" a propósito
    })
    donante = pd.DataFrame({
        "localidad": ["Suba"], "sexo": ["F"], "edad": [30], "estrato": [3],
        "nivel_educativo": [3], "confianza_institucional": [3.0],
    })

    try:
        hot_deck_match(receptor, donante, "confianza_institucional")
        raise AssertionError("debería haber lanzado ValueError por columnas faltantes")
    except ValueError as e:
        print(f"  OK: lanzó ValueError como se esperaba ({e})")


def test_receptor_con_indice_no_trivial():
    """REGRESIÓN — el bug más grave encontrado en la revisión de Sept. 2026.

    El emparejamiento trabajaba con etiquetas de índice donde debía usar
    posiciones de fila. Con un receptor cuyo índice no fuera 0..N-1 (lo que
    produce cualquier `.sample()` sin `reset_index`), el resultado era:
      - IndexError, si el índice se salía de rango; o, peor,
      - opiniones asignadas a la persona equivocada, VIOLANDO el bloque
        exacto localidad+sexo, mientras `resumen_relajacion` seguía
        reportando 100% en nivel 0.

    Este test fija la garantía central del método: la opinión que recibe
    cada agente viene de un donante de su MISMA localidad y MISMO sexo,
    sea cual sea el índice del DataFrame que se pase.
    """
    print("\n[test_receptor_con_indice_no_trivial]")

    receptor = pd.DataFrame({
        "agent_id": [1, 2, 3],
        "localidad": ["Suba", "Suba", "Kennedy"],
        "sexo": ["F", "M", "F"],
        "edad": [30, 45, 25],
        "estrato": [3, 2, 4],
        "nivel_educativo": [3, 2, 4],
    })
    donante = pd.DataFrame({
        "localidad": ["Suba", "Suba", "Kennedy"],
        "sexo": ["F", "M", "F"],
        "edad": [31, 44, 26],
        "estrato": [3, 2, 4],
        "nivel_educativo": [3, 2, 4],
        "confianza_institucional": [3.5, 4.0, 4.5],
    })
    esperado = {1: 3.5, 2: 4.0, 3: 4.5}

    for descripcion, indice in [
        ("RangeIndex normal", [0, 1, 2]),
        ("índice permutado dentro de rango (corrupción silenciosa)", [2, 0, 1]),
        ("índice fuera de rango, como tras .sample()", [100, 101, 102]),
        ("índice de etiquetas de texto", ["a", "b", "c"]),
    ]:
        rec = receptor.copy()
        rec.index = indice
        resultado = hot_deck_match(rec, donante, opinion_col="confianza_institucional")

        obtenido = dict(zip(resultado.agentes["agent_id"], resultado.agentes["confianza_institucional"]))
        _assert(obtenido == esperado,
                f"{descripcion}: cada agente recibe la opinión de su propio bloque "
                f"(esperado {esperado}, obtuvo {obtenido})")
        _assert((resultado.nivel_relajacion_usado == 0).all(),
                f"{descripcion}: y todos se resuelven en nivel 0, como corresponde")


def test_exact_match_vars_tiene_efecto():
    """REGRESIÓN — `exact_match_vars` se validaba pero no se usaba: el bucle
    iteraba sobre una escalera fija localidad -> sexo, así que pedir otro
    conjunto de variables de bloque no cambiaba nada."""
    print("\n[test_exact_match_vars_tiene_efecto]")

    _assert(construir_escalera_relajacion(["localidad", "sexo"]) ==
            [["localidad", "sexo"], ["localidad"], []],
            "la escalera por defecto reproduce exactamente la que estaba escrita a mano")
    _assert(NIVELES_RELAJACION == [["localidad", "sexo"], ["localidad"], []],
            "la constante pública NIVELES_RELAJACION no cambió de valor")
    _assert(construir_escalera_relajacion(["sexo"]) == [["sexo"], []],
            "con una sola variable de bloque la escalera tiene dos niveles")

    # Receptor de Chapinero/F. El donante NO tiene Chapinero/F, pero sí
    # tiene una mujer (en Suba) y un hombre de Chapinero.
    receptor = pd.DataFrame({
        "agent_id": [1], "localidad": ["Chapinero"], "sexo": ["F"],
        "edad": [40], "estrato": [5], "nivel_educativo": [4],
    })
    donante = pd.DataFrame({
        "localidad": ["Chapinero", "Suba", "Bosa"],
        "sexo": ["M", "F", "M"],
        "edad": [41, 40, 60],
        "estrato": [5, 5, 2],
        "nivel_educativo": [4, 4, 1],
        "confianza_institucional": [2.5, 4.5, 1.0],
    })

    # Pidiendo bloque exacto SOLO por sexo, debe ganar la mujer de Suba (4.5),
    # no el hombre de Chapinero (2.5) que ganaría con la escalera fija.
    r = hot_deck_match(receptor, donante, "confianza_institucional", exact_match_vars=["sexo"])
    valor = r.agentes["confianza_institucional"].iloc[0]
    _assert(valor == 4.5,
            f"exact_match_vars=['sexo'] respeta el sexo aunque cambie la localidad "
            f"(esperado 4.5, obtuvo {valor})")
    _assert(r.nivel_relajacion_usado[0] == 0,
            "y lo resuelve en nivel 0 de SU escalera, no relajando")
    _assert(r.escalera_relajacion == [["sexo"], []],
            "el resultado guarda la escalera realmente usada, para que el "
            "metadata de la corrida sea interpretable")

    # El default sigue comportándose como antes (prioriza localidad).
    r_default = hot_deck_match(receptor, donante, "confianza_institucional")
    _assert(r_default.agentes["confianza_institucional"].iloc[0] == 2.5,
            "el comportamiento por defecto no cambió: prioriza localidad sobre sexo")


def test_empates_se_sortean_y_no_se_aplanan():
    """DI-M1 — el regresor del defecto que detuvo el Experimento 7.

    Con variables de distancia discretas, todos los receptores de una celda
    empatan contra los mismos donantes. Antes se tomaba siempre el primero y
    los 300 agentes recibían UN valor; ahora se sortea entre los empatados.
    """
    import numpy as np

    # Una sola celda: mismo sexo, misma edad, mismo estrato. Empate perfecto.
    receptor = pd.DataFrame({
        "agent_id": range(300),
        "localidad": ["Suba"] * 300,
        "sexo": ["F"] * 300,
        "edad": [30] * 300,
        "estrato": [3] * 300,
        "nivel_educativo": [3] * 300,
    })
    donante = pd.DataFrame({
        "localidad": ["Suba"] * 5,
        "sexo": ["F"] * 5,
        "edad": [30] * 5,
        "estrato": [3] * 5,
        "nivel_educativo": [3] * 5,
        "confianza_institucional": [1.0, 2.0, 3.0, 4.0, 5.0],
        "factor_expansion": [1.0, 1.0, 1.0, 1.0, 1.0],
    })

    r = hot_deck_match(receptor, donante, "confianza_institucional",
                       exact_match_vars=["sexo"], distance_vars=["edad", "estrato"],
                       random_state=7, peso_col="factor_expansion")
    distintos = r.agentes["confianza_institucional"].nunique()
    _assert(distintos == 5,
            f"con cinco donantes empatados deben aparecer los cinco valores "
            f"(obtuvo {distintos}); si sale 1, volvió el desempate determinista")

    # Y con pesos desiguales, la distribución donada debe seguir los pesos.
    donante_pesado = donante.copy()
    donante_pesado["factor_expansion"] = [90.0, 2.5, 2.5, 2.5, 2.5]
    r2 = hot_deck_match(receptor, donante_pesado, "confianza_institucional",
                        exact_match_vars=["sexo"], distance_vars=["edad", "estrato"],
                        random_state=7, peso_col="factor_expansion")
    prop_1 = float((r2.agentes["confianza_institucional"] == 1.0).mean())
    _assert(0.80 <= prop_1 <= 0.99,
            f"el donante con 90 % del peso debe llevarse ~90 % de las donaciones "
            f"(obtuvo {prop_1:.2f})")

    # Reproducible: misma semilla, mismo resultado.
    r3 = hot_deck_match(receptor, donante, "confianza_institucional",
                        exact_match_vars=["sexo"], distance_vars=["edad", "estrato"],
                        random_state=7, peso_col="factor_expansion")
    _assert(np.array_equal(r.agentes["confianza_institucional"].to_numpy(),
                           r3.agentes["confianza_institucional"].to_numpy()),
            "el sorteo de empates es reproducible con la misma semilla")


if __name__ == "__main__":
    test_caso_basico_match_exacto()
    test_relajacion_por_falta_de_sexo()
    test_relajacion_total_nivel_2()
    test_reproducibilidad()
    test_falta_columna_lanza_error()
    test_receptor_con_indice_no_trivial()
    test_exact_match_vars_tiene_efecto()
    test_empates_se_sortean_y_no_se_aplanan()
    print("\nTodos los tests pasaron.")
