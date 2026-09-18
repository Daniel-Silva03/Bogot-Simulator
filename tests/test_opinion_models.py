"""
tests/test_opinion_models.py

Pruebas de los modelos de dinámica de opinión (src/opinion/),
especificados en MODEL_SPECIFICATION.md.

Dos verificaciones sostienen todo lo demás:

  1. La forma matricial `paso()` calcula exactamente lo mismo que la
     ecuación escrita agente por agente como aparece en el documento. La
     versión vectorizada es una optimización (DI-O1); esto es lo que
     impide que sea además un cambio de modelo sin querer.

  2. La simulación converge al punto fijo ANALÍTICO de Friedkin-Johnsen,
     a* = (I − ΦW)^{-1}(I − Φ)a(0). Haber elegido un modelo lineal sirve
     justamente para esto: no hay que creerle al bucle, se puede comprobar
     contra la solución exacta.

Ejecutar con:  python3 tests/test_opinion_models.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.network import crear_generador
from src.network.base import normalizar_pesos
from src.opinion import ModeloOpinionError, crear_modelo
from src.opinion.degroot import DeGrootModel
from src.opinion.friedkin_johnsen import FriedkinJohnsenModel


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def poblacion(n=300, seed=5):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "agent_id": np.arange(n),
        "edad": rng.integers(18, 85, n),
        "sexo": rng.choice(["F", "M"], n),
        "localidad": rng.choice(["Suba", "Kennedy", "Bosa", "Chapinero"], n),
        "estrato": rng.integers(1, 7, n),
        "nivel_educativo": rng.integers(0, 6, n),
        "opinion_t0": rng.uniform(1, 5, n),
    })


AGENTES = poblacion()
RED = crear_generador("territorial").generar(AGENTES, k_promedio=8, seed=1, h=10)
W = RED.W
A0 = AGENTES["opinion_t0"].to_numpy(dtype=float)


# ----------------------------------------------------------------------


def test_matricial_coincide_con_la_ecuacion_del_documento():
    """DI-O1: `paso()` debe dar exactamente lo mismo que evaluar la
    ecuación del documento agente por agente."""
    print("\n[test_matricial_coincide_con_la_ecuacion_del_documento]")

    rng = np.random.default_rng(0)
    a = rng.uniform(1, 5, len(A0))

    for nombre, modelo in [("degroot", DeGrootModel(W)),
                           ("friedkin_johnsen", FriedkinJohnsenModel(W, phi=0.7))]:
        modelo.preparar(A0)
        vectorizado = modelo.paso(a)
        uno_a_uno = np.array([modelo.calcular_agente(i, a) for i in range(len(a))])
        error = float(np.abs(vectorizado - uno_a_uno).max())
        _assert(error < 1e-12,
                f"{nombre}: la forma matricial coincide con la ecuación escrita "
                f"agente por agente (error máx {error:.2e})")


def test_degroot_conserva_la_media_y_tiende_al_consenso():
    """Propiedades conocidas del modelo: DeGroot promedia, así que la
    opinión queda dentro del rango inicial y la dispersión baja. Con W
    doblemente estocástica además conserva la media exactamente."""
    print("\n[test_degroot_conserva_la_media_y_tiende_al_consenso]")

    tray = DeGrootModel(W).simular(A0, n_pasos=200)
    print("   ", tray.reporte().replace("\n", "\n    "))

    _assert(tray.desviacion[-1] < tray.desviacion[0],
            f"la dispersión baja ({tray.desviacion[0]:.3f} -> {tray.desviacion[-1]:.3f}): "
            "DeGroot empuja al consenso, su defecto conocido")
    _assert(tray.minimo[-1] >= A0.min() - 1e-9 and tray.maximo[-1] <= A0.max() + 1e-9,
            "ninguna opinión sale del rango inicial (es un promedio ponderado)")

    # Con una red regular W es doblemente estocástica y la media es invariante.
    # El anillo se toma con n IMPAR a propósito: ver el test siguiente.
    n = 61
    anillo = DeGrootModel(normalizar_pesos(_anillo(n)))
    a0 = np.random.default_rng(3).uniform(0, 10, n)
    t = anillo.simular(a0, n_pasos=20000)   # un anillo mezcla despacio: O(n²) pasos
    _assert(abs(t.media[-1] - a0.mean()) < 1e-9,
            f"en una red regular la media se conserva exactamente "
            f"({a0.mean():.6f} -> {t.media[-1]:.6f})")
    _assert(t.desviacion[-1] < 1e-6,
            f"y la red llega a consenso completo (desviación final {t.desviacion[-1]:.2e})")


def _anillo(n):
    """Anillo: cada agente conectado con sus dos vecinos, sin peso propio."""
    A = np.zeros((n, n), dtype=bool)
    for i in range(n):
        A[i, (i + 1) % n] = A[i, (i - 1) % n] = True
    return A


def test_degroot_oscila_en_redes_bipartitas():
    """Propiedad conocida del modelo, no un fallo de implementación:
    con diagonal cero (nadie conserva peso propio), en un grafo bipartito
    DeGroot alterna entre dos estados y nunca converge. Un anillo de
    tamaño PAR es el ejemplo mínimo.

    No afecta al proyecto —las tres redes de NETWORK_SPECIFICATION.md son
    aleatorias y tienen ciclos impares con probabilidad prácticamente 1—
    pero conviene que esté escrito: si alguna vez una corrida de DeGroot
    no converge, esta es la primera hipótesis a revisar, no un bug."""
    print("\n[test_degroot_oscila_en_redes_bipartitas]")

    n = 60  # par -> bipartito
    m = DeGrootModel(normalizar_pesos(_anillo(n)))
    a0 = np.random.default_rng(3).uniform(0, 10, n)
    t = m.simular(a0, n_pasos=2000)

    _assert(not t.convergio,
            f"en un anillo de {n} (par, bipartito) DeGroot no converge")
    _assert(t.desviacion[-1] > 0.1,
            f"la dispersión se estanca en vez de irse a cero ({t.desviacion[-1]:.3f})")

    # y lo que hace es alternar: dos pasos seguidos vuelven al mismo punto
    par = m.paso(m.paso(t.opinion_final))
    _assert(np.abs(par - t.opinion_final).max() < np.abs(m.paso(t.opinion_final) - t.opinion_final).max(),
            "el estado es periódico: dos pasos acercan más al punto de partida que uno")

    impar = DeGrootModel(normalizar_pesos(_anillo(61))).simular(np.append(a0, 1.0), n_pasos=20000)
    _assert(impar.convergio,
            "con un anillo de 61 (impar, no bipartito) sí converge — es la paridad, "
            "no el tamaño")


def test_fj_converge_al_punto_fijo_analitico():
    """La verificación más fuerte: la simulación tiene que llegar a la
    solución exacta del sistema lineal, no solo a 'algo estable'."""
    print("\n[test_fj_converge_al_punto_fijo_analitico]")

    for phi in (0.3, 0.7, 0.95):
        m = FriedkinJohnsenModel(W, phi=phi)
        tray = m.simular(A0, n_pasos=5000)
        exacto = m.punto_fijo()
        error = float(np.abs(tray.opinion_final - exacto).max())
        _assert(error < 1e-7,
                f"phi={phi}: la simulación converge al punto fijo analítico "
                f"(error máx {error:.2e}, {tray.pasos_efectivos} pasos)")

    # phi heterogéneo: mismo resultado, y es la razón de soportar vectores
    rng = np.random.default_rng(11)
    phi_vec = rng.uniform(0.2, 0.9, len(A0))
    m = FriedkinJohnsenModel(W, phi=phi_vec)
    tray = m.simular(A0, n_pasos=5000)
    error = float(np.abs(tray.opinion_final - m.punto_fijo()).max())
    _assert(error < 1e-7,
            f"phi heterogéneo por agente: también converge al punto fijo (error {error:.2e})")


def test_phi_interpola_entre_degroot_y_no_moverse():
    """Los dos casos límite de phi, que es lo que da sentido al parámetro."""
    print("\n[test_phi_interpola_entre_degroot_y_no_moverse]")

    fj1 = FriedkinJohnsenModel(W, phi=1.0).simular(A0, n_pasos=50)
    dg = DeGrootModel(W).simular(A0, n_pasos=50)
    _assert(np.allclose(fj1.opinion_final, dg.opinion_final),
            "phi=1 reproduce DeGroot exactamente")

    fj0 = FriedkinJohnsenModel(W, phi=0.0).simular(A0, n_pasos=50)
    _assert(np.allclose(fj0.opinion_final, A0),
            "phi=0 deja a todos los agentes en su opinión inicial")

    # y en el medio, dispersión intermedia: ni consenso ni inmovilidad
    medias = []
    for phi in (0.0, 0.5, 0.9, 1.0):
        t = FriedkinJohnsenModel(W, phi=phi).simular(A0, n_pasos=300)
        medias.append(t.desviacion[-1])
        print(f"    phi={phi:.1f}: desviación final {t.desviacion[-1]:.4f}")
    _assert(all(a >= b - 1e-9 for a, b in zip(medias, medias[1:])),
            "a mayor phi (más influencia social), menor dispersión final")


def test_fj_permite_desacuerdo_persistente():
    """La razón por la que MODEL_SPECIFICATION.md lo prefiere sobre DeGroot
    para el prototipo: no fuerza consenso."""
    print("\n[test_fj_permite_desacuerdo_persistente]")

    dg = DeGrootModel(W).simular(A0, n_pasos=1000)
    fj = FriedkinJohnsenModel(W, phi=0.7).simular(A0, n_pasos=1000)

    print(f"    DeGroot  -> desviación final {dg.desviacion[-1]:.4f}")
    print(f"    FJ φ=0.7 -> desviación final {fj.desviacion[-1]:.4f}")
    _assert(fj.desviacion[-1] > dg.desviacion[-1],
            "Friedkin-Johnsen conserva más dispersión que DeGroot en la misma red")
    _assert(fj.desviacion[-1] > 0.01,
            f"y el desacuerdo sobrevive de verdad (desviación {fj.desviacion[-1]:.4f}), "
            "que es lo que DeGroot no puede reproducir")


def test_agentes_aislados_conservan_su_opinion():
    """Cierre del círculo con DI-N3 de src/network: un agente sin vecinos
    tiene w_ii=1, así que su opinión debe quedarse donde estaba en los dos
    modelos."""
    print("\n[test_agentes_aislados_conservan_su_opinion]")

    red = crear_generador("aleatoria").generar(AGENTES, k_promedio=1, seed=9)
    aislados = np.where(red.grados == 0)[0]
    _assert(len(aislados) > 0, f"la red de prueba tiene {len(aislados)} agentes aislados")

    for nombre, modelo in [("degroot", DeGrootModel(red.W)),
                           ("friedkin_johnsen", FriedkinJohnsenModel(red.W, phi=0.7))]:
        tray = modelo.simular(A0, n_pasos=100)
        _assert(np.allclose(tray.opinion_final[aislados], A0[aislados]),
                f"{nombre}: los agentes aislados conservan exactamente su opinión inicial")


def test_reproducibilidad_y_determinismo():
    """Los dos modelos son deterministas: dada la red y a(0), la
    trayectoria es única. Importa para el Experimento 2 — la variabilidad
    entre corridas viene de la RED, no de la dinámica."""
    print("\n[test_reproducibilidad_y_determinismo]")

    t1 = FriedkinJohnsenModel(W, phi=0.7).simular(A0, n_pasos=100)
    t2 = FriedkinJohnsenModel(W, phi=0.7).simular(A0, n_pasos=100)
    _assert(np.array_equal(t1.opinion_final, t2.opinion_final),
            "dos corridas con la misma red y la misma a(0) dan trayectorias idénticas")

    otra_red = crear_generador("territorial").generar(AGENTES, k_promedio=8, seed=2, h=10)
    t3 = FriedkinJohnsenModel(otra_red.W, phi=0.7).simular(A0, n_pasos=100)
    _assert(not np.allclose(t1.opinion_final, t3.opinion_final),
            "cambiar la semilla de la RED sí cambia el resultado — de ahí sale la "
            "distribución de resultados que pide RESEARCH.md sección 32")


def test_registro_y_parada_por_convergencia():
    """DI-O3 y DI-O4: qué se guarda y cuándo se corta."""
    print("\n[test_registro_y_parada_por_convergencia]")

    m = FriedkinJohnsenModel(W, phi=0.5)
    tray = m.simular(A0, n_pasos=500)
    _assert(tray.convergio and tray.pasos_efectivos < 500,
            f"se detiene al converger ({tray.pasos_efectivos} de 500 pasos pedidos)")
    _assert(len(tray.media) == 501,
            "pero las series conservan la longitud pedida, para que las corridas "
            "de un barrido sean comparables entre sí")
    _assert(np.allclose(tray.media[tray.pasos_efectivos:], tray.media[tray.pasos_efectivos]),
            "el tramo posterior a la convergencia repite el valor de equilibrio")
    _assert(tray.opiniones is None,
            "por defecto NO guarda la trayectoria completa (4 GB en el Experimento 2)")

    completa = m.simular(A0, n_pasos=10, registrar_opiniones=True)
    _assert(completa.opiniones is not None and completa.opiniones.shape == (11, len(A0)),
            "y la guarda entera cuando se pide explícitamente")
    _assert(np.allclose(completa.opiniones[0], A0),
            "el primer registro es a(0), antes de cualquier paso")

    meta = tray.metadata()
    for clave in ("opinion_model", "parametros_opinion", "n_pasos_efectivos", "convergio"):
        _assert(clave in meta, f"la metadata registra '{clave}'")


def test_errores_explicitos():
    print("\n[test_errores_explicitos]")

    W_mala = np.array([[0.5, 0.2], [0.3, 0.7]])   # la primera fila no suma 1
    casos = [
        ("W con filas que no suman 1",
         lambda: DeGrootModel(W_mala), ModeloOpinionError),
        ("W no cuadrada",
         lambda: DeGrootModel(np.ones((2, 3))), ModeloOpinionError),
        ("W con pesos negativos",
         lambda: DeGrootModel(np.array([[1.5, -0.5], [0.0, 1.0]])), ModeloOpinionError),
        ("phi fuera de [0,1]",
         lambda: FriedkinJohnsenModel(W, phi=1.4), ModeloOpinionError),
        ("phi con longitud equivocada",
         lambda: FriedkinJohnsenModel(W, phi=np.ones(7)), ModeloOpinionError),
        ("opinión inicial de tamaño equivocado",
         lambda: DeGrootModel(W).simular(np.ones(5), n_pasos=10), ModeloOpinionError),
        ("opinión inicial con NaN",
         lambda: DeGrootModel(W).simular(np.full(len(A0), np.nan), n_pasos=10),
         ModeloOpinionError),
        ("FJ: paso() sin anclar a a(0)",
         lambda: FriedkinJohnsenModel(W, phi=0.7).paso(A0), ModeloOpinionError),
        ("punto fijo con phi=1 en todos (es DeGroot)",
         lambda: FriedkinJohnsenModel(W, phi=1.0).punto_fijo(), ModeloOpinionError),
        ("modelo desconocido",
         lambda: crear_modelo("hegselmann_krause", W), ValueError),
        ("parámetro que el modelo no acepta",
         lambda: crear_modelo("degroot", W, phi=0.7), ModeloOpinionError),
    ]
    for descripcion, fn, excepcion in casos:
        try:
            fn()
            raise AssertionError(f"debería haber fallado: {descripcion}")
        except excepcion as e:
            print(f"  OK: falló como se esperaba — {descripcion}\n       ({str(e)[:100]})")


def test_caso_a_mano():
    """Verificación por inspección sobre una red diminuta escrita a mano."""
    print("\n[test_caso_a_mano]")

    # 0 <-> 1, y 2 aislado
    A = np.zeros((3, 3), dtype=bool)
    A[0, 1] = A[1, 0] = True
    Wm = normalizar_pesos(A)   # [[0,1,0],[1,0,0],[0,0,1]]
    a0 = np.array([0.0, 10.0, 4.0])

    paso1 = DeGrootModel(Wm).paso(a0)
    _assert(np.allclose(paso1, [10.0, 0.0, 4.0]),
            f"DeGroot en un par aislado intercambia las opiniones (obtuvo {paso1})")

    fj = FriedkinJohnsenModel(Wm, phi=0.5)
    fj.preparar(a0)
    # agente 0: 0.5*10 + 0.5*0 = 5 ; agente 1: 0.5*0 + 0.5*10 = 5 ; agente 2: 4
    _assert(np.allclose(fj.paso(a0), [5.0, 5.0, 4.0]),
            "FJ con phi=0.5 promedia influencia y anclaje, calculado a mano")

    equilibrio = fj.simular(a0, n_pasos=200).opinion_final
    _assert(np.allclose(equilibrio, fj.punto_fijo()),
            f"y converge a su punto fijo analítico {np.round(fj.punto_fijo(), 4)}")
    _assert(abs(equilibrio[2] - 4.0) < 1e-12,
            "el agente aislado se queda exactamente en 4.0")


if __name__ == "__main__":
    test_matricial_coincide_con_la_ecuacion_del_documento()
    test_degroot_conserva_la_media_y_tiende_al_consenso()
    test_degroot_oscila_en_redes_bipartitas()
    test_fj_converge_al_punto_fijo_analitico()
    test_phi_interpola_entre_degroot_y_no_moverse()
    test_fj_permite_desacuerdo_persistente()
    test_agentes_aislados_conservan_su_opinion()
    test_reproducibilidad_y_determinismo()
    test_registro_y_parada_por_convergencia()
    test_errores_explicitos()
    test_caso_a_mano()
    print("\nTodos los tests pasaron.")
