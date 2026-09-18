"""
tests/test_network_generators.py

Pruebas de los tres generadores de red (src/network/), especificados en
NETWORK_SPECIFICATION.md.

Filosofía igual que en test_population_matching.py: población SINTÉTICA
construida a mano, con proporciones por localidad plausibles pero
inventadas, para poder verificar por inspección que cada generador hace
lo que dice hacer (Regla 2 del prompt maestro: nunca asumir que algo
funciona, verificarlo).

Lo que se verifica no es solo que el código corra, sino las tres
propiedades de las que depende el Experimento 2:

  1. Los tres generadores producen el grado promedio pedido. Si no,
     cualquier diferencia entre ellos podría deberse simplemente a que
     una red es más densa que otra, y la comparación no diría nada sobre
     la ESTRUCTURA.
  2. Cada generador induce efectivamente la estructura que afirma
     inducir (homofilia demográfica / segregación territorial), medida
     contra la línea base del azar.
  3. Misma semilla => misma red, exactamente (sección 26 del prompt
     maestro).

Ejecutar con:  python3 tests/test_network_generators.py
(Diseñado para correr también con pytest: pytest tests/)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.network import crear_generador, diagnosticos_red
from src.network.base import RedInvalidaError, normalizar_pesos
from src.network.homophilic_network import HomophilicNetworkGenerator, calibrar_beta, grado_esperado
from src.network.random_network import RandomNetworkGenerator
from src.network.territorial_network import TerritorialNetworkGenerator, resolver_probabilidades

# Participación de cada localidad, del orden de magnitud de Bogotá pero
# INVENTADA para el test — no es un dato: las proporciones reales vienen
# de las proyecciones DANE-SDP de DATA_SPECIFICATION.md.
PESOS_LOCALIDAD = {
    "Suba": 0.164, "Kennedy": 0.148, "Engativá": 0.105, "Ciudad Bolívar": 0.095,
    "Bosa": 0.094, "Usaquén": 0.062, "San Cristóbal": 0.050, "Fontibón": 0.048,
    "Rafael Uribe Uribe": 0.045, "Usme": 0.044, "Puente Aranda": 0.030,
    "Barrios Unidos": 0.026, "Chapinero": 0.020, "Teusaquillo": 0.019,
    "Tunjuelito": 0.018, "Santa Fe": 0.013, "Los Mártires": 0.012,
    "Antonio Nariño": 0.0055, "La Candelaria": 0.0014, "Sumapaz": 0.0011,
}


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def poblacion_sintetica(n=1000, seed=7):
    """Población de prueba con la estructura de D12."""
    rng = np.random.default_rng(seed)
    nombres = list(PESOS_LOCALIDAD)
    pesos = np.array([PESOS_LOCALIDAD[k] for k in nombres], dtype=float)
    pesos = pesos / pesos.sum()

    localidad = rng.choice(nombres, size=n, p=pesos)
    # estrato correlacionado con localidad (como en Bogotá), para que la
    # homofilia demográfica y la territorial no sean trivialmente iguales
    offset = {k: i % 3 for i, k in enumerate(nombres)}
    estrato = np.clip(
        np.array([offset[l] for l in localidad]) + rng.integers(1, 4, n), 1, 6
    )
    return pd.DataFrame({
        "agent_id": np.arange(n),
        "edad": rng.integers(18, 85, n),
        "sexo": rng.choice(["F", "M"], n),
        "localidad": localidad,
        "estrato": estrato,
        "nivel_educativo": rng.integers(0, 6, n),
        "opinion_t0": rng.uniform(0, 1, n),
    })


AGENTES = poblacion_sintetica()

CASOS = [
    ("aleatoria", {}),
    ("homofilica", {}),
    ("territorial", {"h": 10}),
]


# ----------------------------------------------------------------------


def test_estructura_de_salida():
    """Los tres generadores devuelven el mismo objeto, bien formado:
    adyacencia simétrica sin autolazos, y W con filas que suman 1."""
    print("\n[test_estructura_de_salida]")

    for tipo, params in CASOS:
        red = crear_generador(tipo).generar(AGENTES, k_promedio=10, seed=42, **params)
        A, W = red.adjacency, red.W

        _assert(A.dtype == bool and A.shape == (len(AGENTES), len(AGENTES)),
                f"{tipo}: adjacency booleana de N×N")
        _assert((A == A.T).all(), f"{tipo}: adjacency simétrica (red no dirigida, DI-N4)")
        _assert(not np.diag(A).any(), f"{tipo}: sin autolazos en la adyacencia")
        _assert(np.allclose(W.sum(axis=1), 1.0),
                f"{tipo}: todas las filas de W suman 1 (pesos de influencia válidos)")
        _assert((W >= 0).all(), f"{tipo}: todos los pesos son no negativos")


def test_grado_promedio_objetivo():
    """La condición que hace comparables los tres generadores: el grado
    promedio efectivo debe aproximarse al k̄ pedido, para todo el rango
    del barrido del Experimento 2."""
    print("\n[test_grado_promedio_objetivo]")

    for k in (5, 10, 15, 20):
        for tipo, params in CASOS:
            red = crear_generador(tipo).generar(AGENTES, k_promedio=k, seed=123, **params)
            efectivo = red.grado_promedio
            error_rel = abs(efectivo - k) / k
            _assert(error_rel < 0.10,
                    f"{tipo} k̄={k}: grado efectivo {efectivo:.2f} dentro del 10% del objetivo")


def test_reproducibilidad():
    """Misma semilla => exactamente la misma red. Distinta semilla =>
    red distinta (si no, la semilla no estaría haciendo nada)."""
    print("\n[test_reproducibilidad]")

    for tipo, params in CASOS:
        r1 = crear_generador(tipo).generar(AGENTES, k_promedio=10, seed=99, **params)
        r2 = crear_generador(tipo).generar(AGENTES, k_promedio=10, seed=99, **params)
        r3 = crear_generador(tipo).generar(AGENTES, k_promedio=10, seed=100, **params)

        _assert((r1.adjacency == r2.adjacency).all(),
                f"{tipo}: misma semilla produce exactamente la misma red")
        _assert(not (r1.adjacency == r3.adjacency).all(),
                f"{tipo}: semillas distintas producen redes distintas")


def test_aislados_conservan_su_opinion():
    """DI-N3: con k̄ bajo aparecen agentes de grado 0. Su fila de W debe
    ser w_ii = 1 (conservan su opinión), no una fila de ceros que haría
    colapsar su opinión a 0 por un artefacto de implementación."""
    print("\n[test_aislados_conservan_su_opinion]")

    red = RandomNetworkGenerator().generar(AGENTES, k_promedio=2, seed=5)
    aislados = np.where(red.grados == 0)[0]

    _assert(len(aislados) > 0,
            f"con k̄=2 aparecen agentes aislados ({len(aislados)} de {len(AGENTES)}) — "
            "el caso que DI-N3 tiene que manejar")
    _assert(all(red.W[i, i] == 1.0 for i in aislados),
            "cada agente aislado tiene w_ii = 1")
    _assert(np.allclose(red.W.sum(axis=1), 1.0),
            "las filas de los aislados siguen sumando 1 (W bien normalizada)")
    _assert(red.metadata()["n_aislados"] == len(aislados),
            "el número de aislados queda registrado en la metadata, no oculto")

    # y en el resto de la matriz la diagonal sigue siendo 0
    conectados = np.where(red.grados > 0)[0]
    _assert((red.W[conectados, conectados] == 0).all(),
            "los agentes con vecinos no tienen peso propio (diagonal 0)")


def test_homofilia_efectiva():
    """El generador homofílico debe conectar gente MÁS parecida que el
    azar; el aleatorio, no. Se mide contra la línea base de todos los
    pares posibles (diagnosticos_red)."""
    print("\n[test_homofilia_efectiva]")

    homo = HomophilicNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1)
    azar = RandomNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1)

    d_homo = diagnosticos_red(homo, AGENTES)
    d_azar = diagnosticos_red(azar, AGENTES)

    for var in ("edad", "estrato", "nivel_educativo"):
        h = d_homo[f"homofilia_{var}"]
        a = d_azar[f"homofilia_{var}"]
        _assert(h < 0.9,
                f"homofílica: las aristas conectan agentes más parecidos en {var} "
                f"que el azar (razón {h:.2f} < 0.9)")
        _assert(abs(a - 1.0) < 0.05,
                f"aleatoria: no induce homofilia en {var} (razón {a:.2f} ≈ 1) — "
                "es el control experimental")


def test_segregacion_territorial():
    """El generador territorial debe concentrar aristas dentro de la
    localidad, y hacerlo más cuanto mayor sea h. El aleatorio, no."""
    print("\n[test_segregacion_territorial]")

    azar = RandomNetworkGenerator().generar(AGENTES, k_promedio=10, seed=3)
    _assert(abs(diagnosticos_red(azar, AGENTES)["segregacion_territorial"] - 1.0) < 0.15,
            "aleatoria: fracción de aristas intra-localidad ≈ la del azar (razón ≈ 1)")

    anteriores = 0.0
    for h in (5, 10, 20):
        red = TerritorialNetworkGenerator().generar(AGENTES, k_promedio=10, seed=3, h=h)
        seg = diagnosticos_red(red, AGENTES)["segregacion_territorial"]
        _assert(seg > anteriores,
                f"territorial h={h}: segregación {seg:.2f} mayor que con el h anterior "
                f"({anteriores:.2f}) — más h, más concentración intra-localidad")
        anteriores = seg
    _assert(anteriores > 2.0,
            f"territorial h=20: segregación {anteriores:.2f} claramente por encima del azar")


def test_territorial_h_igual_1_equivale_a_aleatoria():
    """Caso límite útil como verificación cruzada: con h=1 no hay
    preferencia territorial, así que p_intra debe igualar a p_inter y la
    red debe comportarse como Erdős–Rényi."""
    print("\n[test_territorial_h_igual_1_equivale_a_aleatoria]")

    red = TerritorialNetworkGenerator().generar(AGENTES, k_promedio=10, seed=11, h=1)
    p_intra = red.parametros["p_intra"]
    p_inter = red.parametros["p_inter"]

    _assert(abs(p_intra - p_inter) < 1e-9, "con h=1, p_intra == p_inter")
    _assert(abs(p_intra - 10 / (len(AGENTES) - 1)) < 1e-6,
            "con h=1 la probabilidad coincide con la de Erdős–Rényi, k̄/(N-1)")
    seg = diagnosticos_red(red, AGENTES)["segregacion_territorial"]
    _assert(abs(seg - 1.0) < 0.15, f"con h=1 no hay segregación territorial (razón {seg:.2f} ≈ 1)")


def test_calibracion_de_beta():
    """β no se fija a mano: se calibra para que el grado promedio
    esperado iguale a k̄ (NETWORK_SPECIFICATION.md sección 4). Se verifica
    que la función objetivo sea monótona decreciente, que es lo que
    justifica usar bisección."""
    print("\n[test_calibracion_de_beta]")

    gen = HomophilicNetworkGenerator()
    i_idx, j_idx = np.triu_indices(len(AGENTES), k=1)
    d = gen._distancias(AGENTES, (1.0, 1.0, 1.0), i_idx, j_idx)

    grados = [grado_esperado(d, len(AGENTES), b) for b in (0.0, 0.5, 1.0, 2.0, 5.0, 20.0)]
    _assert(all(a > b for a, b in zip(grados, grados[1:])),
            "el grado esperado decrece monótonamente con beta (bisección válida)")
    _assert(abs(grados[0] - (len(AGENTES) - 1)) < 1e-6,
            "con beta=0 la red es completa (grado N-1), como debe ser")

    for k in (5, 10, 20):
        beta, g, convergio = calibrar_beta(d, len(AGENTES), k)
        _assert(convergio and abs(g - k) < 0.01 * k,
                f"beta calibrado para k̄={k}: grado esperado {g:.4f} (beta={beta:.4f})")


def test_pesos_cambian_la_red():
    """Los pesos w_e, w_s, w_v son un supuesto explícito, no un hecho
    (NETWORK_SPECIFICATION.md sección 8). El test verifica que cambiarlos
    cambia la red — es decir, que el supuesto por defecto (1,1,1)
    efectivamente importa y merece revisarse en el Experimento 3."""
    print("\n[test_pesos_cambian_la_red]")

    gen = HomophilicNetworkGenerator()
    d_edad = diagnosticos_red(
        gen.generar(AGENTES, k_promedio=10, seed=8, pesos=(1, 0.05, 0.05)), AGENTES)
    d_estrato = diagnosticos_red(
        gen.generar(AGENTES, k_promedio=10, seed=8, pesos=(0.05, 1, 0.05)), AGENTES)

    _assert(d_edad["homofilia_edad"] < d_estrato["homofilia_edad"],
            "cargando el peso en edad, la red es más homofílica por edad "
            f"({d_edad['homofilia_edad']:.2f} < {d_estrato['homofilia_edad']:.2f})")
    _assert(d_estrato["homofilia_estrato"] < d_edad["homofilia_estrato"],
            "cargando el peso en estrato, la red es más homofílica por estrato "
            f"({d_estrato['homofilia_estrato']:.2f} < {d_edad['homofilia_estrato']:.2f})")
    print("  -> el supuesto w=(1,1,1) no es neutro: la elección de pesos cambia "
          "materialmente la red (revisar en el Experimento 3).")


def test_estricto_false_permite_explorar_el_caso_degenerado():
    """DI-N6: el caso degenerado falla por defecto, pero se puede forzar a
    propósito con estricto=False — con la red resultante etiquetada como
    no convergida en la metadata, para que nunca pase por una red de k̄=10."""
    print("\n[test_estricto_false_permite_explorar_el_caso_degenerado]")

    red = HomophilicNetworkGenerator().generar(
        AGENTES, k_promedio=10, seed=1, pesos=(0, 1, 0), estricto=False)

    _assert(red.parametros["calibracion_convergio"] is False,
            "la metadata registra que la calibración NO convergió")
    _assert(red.grado_promedio > 50,
            f"y la red efectivamente quedó mucho más densa de lo pedido "
            f"(k̄ efectivo {red.grado_promedio:.1f} vs. 10 pedido) — por eso falla por defecto")


def test_cache_no_cambia_resultados():
    """El generador homofílico memoiza distancias y beta para no
    recalcularlos en cada run del Experimento 2. La caché es una
    optimización: reutilizar la instancia debe dar EXACTAMENTE la misma
    red que usar una instancia nueva. Y si la población cambia, la caché
    debe invalidarse."""
    print("\n[test_cache_no_cambia_resultados]")

    reutilizada = HomophilicNetworkGenerator()
    reutilizada.generar(AGENTES, k_promedio=10, seed=0)          # llena la caché
    r_cache = reutilizada.generar(AGENTES, k_promedio=10, seed=77)
    r_fresca = HomophilicNetworkGenerator().generar(AGENTES, k_promedio=10, seed=77)

    _assert((r_cache.adjacency == r_fresca.adjacency).all(),
            "la instancia reutilizada produce exactamente la misma red que una nueva")
    _assert(r_cache.parametros["beta_calibrado"] == r_fresca.parametros["beta_calibrado"],
            "y el mismo beta calibrado")

    otros = AGENTES.copy()
    otros["edad"] = otros["edad"].to_numpy()[::-1]  # misma distribución, otra asignación
    entradas_antes = len(reutilizada._cache_d)
    r_otros = reutilizada.generar(otros, k_promedio=10, seed=77)

    _assert(len(reutilizada._cache_d) == entradas_antes + 1,
            "una población distinta genera una entrada de caché nueva, no reusa la vieja")
    _assert(not (r_otros.adjacency == r_cache.adjacency).all(),
            "y la red resultante es distinta, como debe ser con otra población")


def test_errores_explicitos():
    """Los parámetros imposibles deben fallar con un mensaje claro, no
    devolver una red silenciosamente distinta de la pedida."""
    print("\n[test_errores_explicitos]")

    casos = [
        ("k̄ >= N-1 (red más que completa)",
         lambda: RandomNetworkGenerator().generar(AGENTES.head(10), k_promedio=20, seed=1),
         RedInvalidaError),
        ("k̄ <= 0",
         lambda: RandomNetworkGenerator().generar(AGENTES, k_promedio=0, seed=1),
         RedInvalidaError),
        ("falta la columna 'localidad' para el generador territorial",
         lambda: TerritorialNetworkGenerator().generar(
             AGENTES.drop(columns=["localidad"]), k_promedio=10, seed=1),
         RedInvalidaError),
        ("h < 1 (preferir conectarse fuera de la propia localidad)",
         lambda: TerritorialNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1, h=0.5),
         RedInvalidaError),
        # N=4, dos localidades de 2, k̄=1.5, h=10 -> p_inter=0.125, p_intra=1.25 > 1
        ("h y k̄ incompatibles: exigirían p_intra > 1",
         lambda: resolver_probabilidades(k_promedio=1.5, h=10.0, conteos=np.array([2, 2]), n=4),
         RedInvalidaError),
        ("k̄ por debajo del mínimo alcanzable por empates de distancia (DI-N6)",
         lambda: HomophilicNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1, pesos=(0, 1, 0)),
         RedInvalidaError),
        ("pesos todos en 0 en el generador homofílico",
         lambda: HomophilicNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1, pesos=(0, 0, 0)),
         RedInvalidaError),
        ("parámetro inexistente pasado al generador aleatorio",
         lambda: RandomNetworkGenerator().generar(AGENTES, k_promedio=10, seed=1, h=10),
         TypeError),
        ("tipo de generador desconocido",
         lambda: crear_generador("small_world"),
         ValueError),
    ]

    for descripcion, fn, excepcion in casos:
        try:
            fn()
            raise AssertionError(f"debería haber fallado: {descripcion}")
        except excepcion as e:
            print(f"  OK: falló como se esperaba — {descripcion}\n       ({type(e).__name__}: {str(e)[:110]})")


def test_normalizacion_caso_a_mano():
    """Verificación por inspección de la normalización de pesos, sobre una
    red diminuta escrita a mano: 0-1, 0-2, y el agente 3 aislado."""
    print("\n[test_normalizacion_caso_a_mano]")

    A = np.zeros((4, 4), dtype=bool)
    A[0, 1] = A[1, 0] = True
    A[0, 2] = A[2, 0] = True
    W = normalizar_pesos(A)

    esperado = np.array([
        [0.0, 0.5, 0.5, 0.0],   # agente 0: dos vecinos, 1/2 cada uno
        [1.0, 0.0, 0.0, 0.0],   # agente 1: un vecino, peso 1
        [1.0, 0.0, 0.0, 0.0],   # agente 2: un vecino, peso 1
        [0.0, 0.0, 0.0, 1.0],   # agente 3: aislado, conserva su opinión
    ])
    _assert(np.allclose(W, esperado), "la matriz de pesos coincide con la calculada a mano")


def test_ecuacion_territorial_a_mano():
    """Verificación por inspección del despeje lineal de p_intra/p_inter,
    con dos localidades de 2 agentes cada una."""
    print("\n[test_ecuacion_territorial_a_mano]")

    # N=4, dos localidades de tamaño 2, h=1 -> debe dar ER: p = k̄/(N-1)
    p_intra, p_inter = resolver_probabilidades(k_promedio=1.5, h=1.0, conteos=np.array([2, 2]), n=4)
    _assert(abs(p_intra - 0.5) < 1e-12 and abs(p_inter - 0.5) < 1e-12,
            f"h=1, k̄=1.5, N=4 -> p = 1.5/3 = 0.5 (obtenido {p_intra}, {p_inter})")

    # h=3: denominador = Σ n_l [h(n_l-1) + (N-n_l)] = 2*(3*1+2)*2 = 20
    # p_inter = 1.5*4/20 = 0.3 ; p_intra = 0.9
    p_intra, p_inter = resolver_probabilidades(k_promedio=1.5, h=3.0, conteos=np.array([2, 2]), n=4)
    _assert(abs(p_inter - 0.3) < 1e-12 and abs(p_intra - 0.9) < 1e-12,
            f"h=3, k̄=1.5, N=4 -> p_inter=0.3, p_intra=0.9 (obtenido {p_inter}, {p_intra})")

    # y el grado promedio implícito vuelve a ser k̄
    k_implicito = (2 * (p_intra * 1 + p_inter * 2) + 2 * (p_intra * 1 + p_inter * 2)) / 4
    _assert(abs(k_implicito - 1.5) < 1e-12,
            f"el grado promedio que implican esas probabilidades es k̄=1.5 (obtenido {k_implicito})")


if __name__ == "__main__":
    test_estructura_de_salida()
    test_grado_promedio_objetivo()
    test_reproducibilidad()
    test_aislados_conservan_su_opinion()
    test_homofilia_efectiva()
    test_segregacion_territorial()
    test_territorial_h_igual_1_equivale_a_aleatoria()
    test_calibracion_de_beta()
    test_pesos_cambian_la_red()
    test_estricto_false_permite_explorar_el_caso_degenerado()
    test_cache_no_cambia_resultados()
    test_errores_explicitos()
    test_normalizacion_caso_a_mano()
    test_ecuacion_territorial_a_mano()
    print("\nTodos los tests pasaron.")
