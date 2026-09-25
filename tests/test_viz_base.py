"""Pruebas de la capa base urbana. Se corren solas: python3 tests/test_viz_base.py

Lo que se verifica aquí no es que el mapa se vea bonito, sino tres cosas que,
si se rompen, hacen que la página mienta:

1. Que la geometría decodificada caiga donde dice caer. Si la codificación
   delta (DI-V13) se desalinea, las vías aparecen desplazadas sobre las
   localidades y el usuario lee una avenida en la localidad equivocada.
2. Que la capa base no arrastre ningún atributo de OpenStreetMap al paquete.
   La capa es decorado: si llevara nombres, anchos o clasificaciones, alguien
   terminaría calculando algo con ella.
3. Que la atribución ODbL esté en la página construida. Es obligación de la
   licencia (DI-V8), no una nota al pie opcional.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.viz.preparar_base import (  # noqa: E402
    DECIMALES,
    ESCALA,
    caja_urbana,
    construir,
    douglas_peucker,
    unir_tramos,
)

FALLOS: list[str] = []


def probar(nombre, condicion, detalle=""):
    if condicion:
        print(f"  ok   {nombre}")
    else:
        print(f"  FALLA {nombre} {detalle}")
        FALLOS.append(nombre)


def decodificar(plano):
    pts, x, y = [], 0, 0
    for i in range(0, len(plano), 2):
        x += plano[i]
        y += plano[i + 1]
        pts.append((x / ESCALA, y / ESCALA))
    return pts


def todas_las_lineas(d):
    for lineas in d["vias"].values():
        yield from lineas
    for nivel in ("g", "p"):
        yield from d["verde"][nivel]
        yield from d["agua"]["areas"][nivel]
    yield from d["agua"]["cauces"]


def todos_los_poligonos(d):
    for nivel in ("g", "p"):
        yield from d["verde"][nivel]
        yield from d["agua"]["areas"][nivel]


def main():
    d = construir()
    caja = caja_urbana()
    x0, y0, x1, y1 = caja

    print("estructura")
    probar("el paquete trae las tres capas", {"vias", "verde", "agua"} <= set(d))
    probar("la caja del paquete es la caja urbana calculada",
           [round(v, 4) for v in caja] == d["meta"]["caja"])
    probar("solo hay clases de vía arterial (trunk/primary)",
           set(d["vias"]) <= {"trunk", "primary"}, str(set(d["vias"])))
    probar("hay vías dibujables", sum(len(v) for v in d["vias"].values()) > 50)
    probar("hay áreas verdes en el primer nivel", len(d["verde"]["g"]) > 50)
    probar("hay más áreas verdes en el nivel de detalle", len(d["verde"]["p"]) > len(d["verde"]["g"]),
           f'{len(d["verde"]["g"])} vs {len(d["verde"]["p"])}')
    probar("las dos capas de polígonos traen los dos niveles",
           set(d["verde"]) == {"g", "p"} and set(d["agua"]["areas"]) == {"g", "p"})
    probar("la licencia queda declarada en los metadatos", "ODbL" in d["meta"]["licencia"])

    print("codificación delta (DI-V13)")
    planos = list(todas_las_lineas(d))
    probar("toda polilínea tiene un número par de enteros",
           all(len(p) % 2 == 0 for p in planos))
    probar("toda polilínea tiene al menos dos puntos",
           all(len(p) >= 4 for p in planos))
    probar("los deltas son enteros", all(isinstance(v, int) for p in planos for v in p))
    ida = [[-74.0721, 4.6097], [-74.0700, 4.6110], [-74.0688, 4.6131]]
    from src.viz.preparar_base import codificar

    probar("codificar y decodificar es la identidad a 4 decimales",
           [[round(x, DECIMALES), round(y, DECIMALES)] for x, y in decodificar(codificar(ida))] == ida)

    print("encuadre")
    fuera = 0
    for p in planos:
        for x, y in decodificar(p):
            if not (x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 1e-6 <= y <= y1 + 1e-6):
                fuera += 1
    total = sum(len(p) // 2 for p in planos)
    # Una geometría se conserva entera si TOCA la caja, así que puede salirse un
    # poco por el borde; lo que no puede pasar es que se salga la mitad del
    # paquete, que sería recorte roto.
    probar("casi todos los puntos caen dentro de la caja urbana",
           fuera / max(total, 1) < 0.05, f"{fuera}/{total} fuera")

    print("polígonos")
    cortos = sum(1 for anillo in todos_los_poligonos(d) if len(decodificar(anillo)) < 4)
    probar("todo polígono tiene al menos cuatro puntos", cortos == 0)

    print("la capa base no lleva datos")
    texto = json.dumps(d, ensure_ascii=False)
    for etiqueta in ("name", "highway", "leisure", "@id", "maxspeed", "lanes", "surface"):
        probar(f"no sobrevive la etiqueta OSM «{etiqueta}» fuera de las claves de clase",
               f'"{etiqueta}"' not in texto)

    print("unión de tramos (DI-V10)")
    tramos = [[[0, 0], [1, 1]], [[1, 1], [2, 2]], [[5, 5], [6, 6]]]
    unidas = unir_tramos(tramos)
    probar("dos tramos contiguos se vuelven una polilínea de tres puntos",
           sorted(len(l) for l in unidas) == [2, 3], str(unidas))

    print("simplificación (DI-V9)")
    recta = [[0, 0], [1, 1.0000001], [2, 2]]
    probar("Douglas-Peucker colapsa una recta a sus extremos",
           len(douglas_peucker(recta, 0.0002)) == 2)
    esquina = [[0, 0], [1, 0], [1, 1]]
    probar("Douglas-Peucker conserva una esquina real",
           len(douglas_peucker(esquina, 0.0002)) == 3)

    print("página construida")
    pagina = (RAIZ / "data" / "processed" / "viz" / "mapa_bogota.html").read_text(encoding="utf-8")
    probar("la atribución a OpenStreetMap está en la página", "OpenStreetMap" in pagina)
    probar("la licencia ODbL está en la página", "ODbL" in pagina)
    probar("la página dice que la capa base no entra en ningún cálculo",
           "ninguna cifra de esta página se calcula con ella" in pagina)
    probar("no quedan marcadores sin sustituir",
           not any(m in pagina for m in ("/*__DATOS__*/", "/*__BASE__*/", "/*__SERIE__*/")))
    print("navegación")
    for marca, que in [
        ('id="btnAjustar"', "el botón de ajuste está"),
        ('id="escala"', "la barra de escala está"),
        ("ZOOM_MAX", "hay tope de acercamiento"),
        ("function mundo()", "el mundo se calcula con la forma del lienzo"),
        ("ev.ctrlKey || ev.metaKey", "la rueda sola no secuestra el scroll (DI-V16)"),
        ("touch-action:none", "el arrastre táctil llega al mapa"),
        ("encuadrarLocalidad", "se puede encuadrar una localidad"),
        ("if(huboArrastre) return", "arrastrar no cambia la selección"),
        ("A este acercamiento se nota", "el acercamiento explica DI-V3"),
        ('<meta charset="utf-8">', "la página declara UTF-8 para abrirse desde el disco (DI-V22)"),
    ]:
        probar(que, marca in pagina)

    print("ficha de la escala (A05)")
    for marca, que in [
        ('id="ficha"', "la página tiene el bloque de la ficha"),
        ("function fichaEscala()", "la ficha se dibuja desde el metadata"),
        ("D.escala_opinion", "la ficha lee la descripción del pipeline, no texto a mano"),
        ("Qué mide la escala de 1 a 5", "el bloque se anuncia como tal"),
        ("confía mucho", "las anclas verbales llegaron a la página"),
        ("Confianza institucional", "el concepto medido aparece en la página"),
        ("Lo que no es", "la página advierte que no es un porcentaje"),
    ]:
        probar(que, marca in pagina)

    # DI-V36: el color de población no es proporcional a la población. Mientras
    # la leyenda imprimía solo los extremos, el lector no tenía cómo saberlo.
    print("rampa de población (DI-V36)")
    for marca, que in [
        ("const tPob =", "la transformación de la rampa tiene un nombre"),
        ("interp(RAMPA, tPob(", "el color usa esa transformación"),
        ("tPob(v)*100", "las marcas de la leyenda usan la MISMA transformación"),
        ("color en escala de raíz", "la leyenda declara que la escala no es lineal"),
        # Las etiquetas se arman en tiempo de ejecución, así que lo que se
        # comprueba es la fuente de los valores, no el texto ya formateado.
        ("[50000, 200000, 500000]", "hay marcas intermedias con valores redondos"),
        ('class="marca"', "las marcas se dibujan sobre la rampa"),
    ]:
        probar(que, marca in pagina)

    # La prueba que de verdad protege: una sola raíz en toda la página. Si
    # alguien reimplementa la transformación en la leyenda, color y marcas se
    # separan sin que nada falle a la vista.
    probar("la raíz se calcula en un solo lugar",
           pagina.count("Math.sqrt") == 1,
           f"hay {pagina.count('Math.sqrt')} usos de Math.sqrt en la página")

    print("el año en la página (DI-V43 a DI-V46)")
    for marca, que in [
        ("let anioSel", "la página tiene un año seleccionado"),
        ("function irAlAnio(", "hay una sola puerta para cambiar de año"),
        ("const C = () =>", "la ciudad se lee del año, no de un bloque fijo"),
        ("const opDe = (l, campo)", "la opinión de una localidad se lee del año"),
        ("function botonesAnio()", "hay botones de año"),
        ("function marcarAnioSerie(", "el año activo se marca en la serie"),
        ("function pintarAgentes()", "los agentes se colorean por su opinión del año"),
        ("piso_medido", "la página conoce el piso de ruido medido"),
        ("const pobDe =", "la población de la coropleta se lee del año"),
        ("D.poblacion_max", "la rampa verde se ancla al máximo de todos los años"),
        ("El color apenas se mueve entre", "la página dice que el verde casi no cambia"),
        ("no cambia con el año", "la página aclara que «esperados» es del muestreo"),
        ("no registra la localidad",
         "la página da la razón de fondo: el donante no trae localidad (DI-V52)"),
    ]:
        probar(que, marca in pagina)

    # DI-V52: comparar la corrida publicada contra el rango de sus propias
    # semillas no puede detectar señal (el percentil sale uniforme haya o no
    # efecto). Si la página vuelve a leer ese campo, vuelve a afirmar algo que
    # la prueba no sostiene.
    probar("la página no lee hay_senal_territorial (DI-V52)",
           ".hay_senal_territorial" not in pagina)

    # DI-V46: el estado del año es uno solo. Si quedara un `D.ciudad` o un
    # `l.opinion_media` suelto, media pantalla mostraría el año base y la otra
    # media el año elegido, y nadie lo notaría hasta que los números no cuadren.
    for muerto, que in [
        ("D.ciudad.", "no queda ninguna lectura del bloque de ciudad viejo"),
        ("l.opinion_media", "no queda ninguna lectura de la media sin año"),
        ("l.opinion_ee", "no queda ninguna lectura del error sin año"),
    ]:
        probar(que, muerto not in pagina)

    print("capa de crecimiento (DI-V51)")
    for marca, que in [
        ('data-capa="crecimiento"', "hay un botón de crecimiento"),
        ("const RAMPA_CREC", "hay una rampa propia, no se reusa la de opinión"),
        ("const crecDe =", "el crecimiento se calcula desde el año base"),
        ("(v + crecMax) / (2*crecMax)", "el dominio es simétrico, con el cero al centro"),
        ("function leyendaCrecimiento(", "la capa tiene su propia leyenda"),
        ("es el año base", "la leyenda explica el corte base, donde todo es cero"),
        ("function avisoCrecimiento(", "la capa tiene su propio aviso"),
        ("personas)", "el aviso da el cambio absoluto, no solo el porcentaje"),
        ("dos permisos distintos", "el aviso contrasta con la capa de opinión"),
        ("'poblacion','opinion','crecimiento'", "la capa se oculta en vista Ciudad, como las otras"),
    ]:
        probar(que, marca in pagina)

    # La rampa de crecimiento NO puede ser la de opinión: son dos cantidades
    # divergentes distintas y reusar el color haría que un azul significara
    # «poca confianza» en una capa y «pierde población» en otra.
    probar("la rampa de crecimiento es distinta de la de opinión",
           "[[  0,143,137]" in pagina and "[[ 20, 88,146]" in pagina)

    probar("la página sigue siendo autocontenida salvo tipografías (DI-V6)",
           pagina.count("https://") == pagina.count("https://fonts.") + pagina.count("https://opendatacommons.org"),
           "hay peticiones de red que no son tipografías ni el enlace de la licencia")

    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron: {', '.join(FALLOS)}")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
