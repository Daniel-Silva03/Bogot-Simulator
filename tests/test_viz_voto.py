"""
tests/test_viz_voto.py

Pruebas de la capa de Voto del tablero (DI-V53 a DI-V56): el paquete
`voto_bogota.json` contra sus fuentes, y la página contra las reglas de la capa.
Se ejecuta directo:  python tests/test_viz_voto.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd

FALLOS = []
PAQUETE = RAIZ / "data" / "processed" / "viz" / "voto_bogota.json"
PAGINA = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.html"
RESULTADO = RAIZ / "data" / "processed" / "geografia_electoral" / "resultado.json"
ELECTORAL = RAIZ / "data" / "external" / "electoral"


def probar(nombre, condicion, detalle=""):
    print(f"  {'ok   ' if condicion else 'FALLA'}  {nombre}" + (f"\n         {detalle}" if not condicion and detalle else ""))
    if not condicion:
        FALLOS.append(nombre)


def main():
    V = json.loads(PAQUETE.read_text(encoding="utf-8"))
    R = json.loads(RESULTADO.read_text(encoding="utf-8"))
    votos = pd.read_csv(ELECTORAL / "presidente_1v_localidad.csv")
    zonas = pd.read_csv(ELECTORAL / "presidente_1v_zonas.csv")
    L = V["localidades"]

    print("paquete (DI-V53, DI-V54)")
    probar("20 localidades con código de dos dígitos", sorted(L) == [f"{i:02d}" for i in range(1, 21)])
    probar("nueve candidatos presidenciales y dos partidos del Senado",
           sum(c["tipo"] == "candidato" for c in V["candidatos"]) == 9
           and sum(c["tipo"] == "partido" for c in V["candidatos"]) == 2)
    probar("cada opción dice a qué grupo y elección pertenece",
           all(c["grupo"] in V["grupos"] and c["eleccion"] and c["fuera"] in V["votos_sin_localidad"]
               for c in V["candidatos"]))
    probar("el candidato por defecto es el principal del pre-registro", V["por_defecto"] == "2022_petro")

    # Las proporciones son sobre votos por candidato, las mismas del análisis.
    malas = []
    for c in [x for x in V["candidatos"] if x["tipo"] == "candidato"]:
        a, k = c["anio"], c["id"]
        for cod, l in L.items():
            fila = votos[(votos.anio == a) & (votos.cod_loc == int(cod)) & (votos.clave == k)]
            base = zonas[(zonas.anio == a) & (zonas.cod_loc == int(cod))].votos_candidatos
            esperado = round(float(fila.votos.sum() / base.sum()), 4)
            if l["votos"][c["clave"]] != esperado:
                malas.append((c["clave"], cod, l["votos"][c["clave"]], esperado))
    probar("cada proporción coincide con la tabla electoral (sobre votos por candidato)", not malas, str(malas[:3]))

    suma = {a: max(sum(l["votos"][c["clave"]] for c in V["candidatos"] if c["anio"] == a and c["tipo"] == "candidato")
                   for l in L.values()) for a in V["elecciones"]}
    probar("los tres candidatos de un año nunca suman más del 100 %", all(s <= 1.0001 for s in suma.values()), str(suma))

    todas = [v for l in L.values() for v in l["votos"].values()]
    probar("el dominio de voto es el máximo observado, uno solo para todos (DI-V54)",
           V["dominio_voto"] == round(max(todas), 4))
    probar("el dominio de residuo cubre todos los residuos",
           all(abs(v) <= V["dominio_residuo"] + 1e-9 for l in L.values() for v in l["residuo"].values() if v is not None))

    print("Senado 2018 y los dos polos (DI-V59)")
    import numpy as np
    from src.experiments import eje_partidos as ep
    RP = json.loads((RAIZ / "data" / "processed" / "eje_partidos" / "resultado.json").read_text(encoding="utf-8"))
    S = RP["por_corporacion"]["senado_nacional"]
    cv = pd.read_csv(ELECTORAL / "congreso_2018_localidad.csv")
    cz = pd.read_csv(ELECTORAL / "congreso_2018_zonas.csv")
    prop = ep.proporciones_partido(cv, cz, "senado", "nacional")
    for clave, partido in (("senado2018_decencia", ep.DECENCIA), ("senado2018_cd", ep.CENTRO_DEMOCRATICO)):
        probar(f"{clave}: la proporción es la de la tabla del Congreso",
               all(L[f"{c:02d}"]["votos"][clave] == round(float(prop.loc[c, partido]), 4) for c in prop.index))
        probar(f"{clave}: el residuo es el del resultado pre-registrado, sin recalcular",
               all(L[f"{int(c):02d}"]["residuo"][clave] == round(v, 4) for c, v in S[partido]["residuos"].items()))
    P = V["polos"]
    probar("la lectura de dos polos está marcada como no pre-registrada", P["pre_registrado"] is False)
    probar("ninguna opción está en los dos polos", not set(P["izquierda"]) & set(P["derecha"]))
    # La pertenencia no se escribe a mano sin respaldo: cada opción de un polo tiene
    # que parecerse a su partido. Si un análisis futuro lo cambia, esto falla primero.
    locs = [f"{c:02d}" for c in range(1, 20)]
    vec = lambda k: np.array([L[c]["residuo"][k] for c in locs], float)          # noqa: E731
    malos = [(k, polo) for polo, ref in (("izquierda", "senado2018_decencia"), ("derecha", "senado2018_cd"))
             for k in P[polo] if np.corrcoef(vec(k), vec(ref))[0, 1] < 0.69]
    probar("cada opción de un polo se parece a su partido (r ≥ 0,69)", not malos, str(malos))
    probar("las correlaciones del paquete son las que salen de los residuos",
           all(abs(P["correlaciones"][k]["con_cd"] - np.corrcoef(vec(k), vec("senado2018_cd"))[0, 1]) < 0.006
               for k in P["correlaciones"]))

    print("residuos (DI-V55, DI-V56)")
    iguales = all(L[f"{int(cod):02d}"]["residuo"][k] == round(v, 4)
                  for k, r in R["resultados"].items() for cod, v in r["residuos"].items())
    probar("los residuos son los del resultado pre-registrado, sin recalcular", iguales)
    probar("Sumapaz tiene voto pero no residuo",
           L["20"]["votos"]["2022_petro"] is not None
           and all(v is None for v in L["20"]["residuo"].values())
           and all(v is None for v in L["20"]["residuo_participacion"].values()))
    probar("la vista con participación está marcada como exploratoria", V["participacion_exploratoria"] is True)
    probar("el análisis citado es el del resultado",
           V["analisis"]["persistencia_r"] == R["persistencia"]["r"]
           and V["analisis"]["r2_loo_principal"] == R["resultados"]["2022_petro"]["r2_loo_m1"])

    print("salvedades (DI-V53)")
    probar("el paquete trae los votos sin localidad por año", set(V["votos_sin_localidad"]) == {"2014", "2018", "2022", "senado_2018"})
    esp = zonas[zonas.cod_loc.isna() & zonas.anio.isin(V["elecciones"])].groupby("anio").votos_total.sum()
    probar("los votos sin localidad son los de las zonas 90 y 98",
           all(V["votos_sin_localidad"][str(a)]["votos"] == int(esp[a]) for a in esp.index))
    probar("la razón de inscripción está para las 20 localidades",
           all(l["inscritos_sobre_adultos"] is not None for l in L.values()))
    probar("La Candelaria tiene más inscritos que adultos (la salvedad es real)",
           L["17"]["inscritos_sobre_adultos"] > 2)

    print("página")
    p = PAGINA.read_text(encoding="utf-8")
    for marca, que in [
        ('data-capa="voto"', "hay un botón de voto"),
        ('<script id="votoDatos" type="application/json">{', "el paquete de voto llegó a la página"),
        ("const RAMPA_VOTO", "hay una rampa de voto propia"),
        ("const RAMPA_RESID", "hay una rampa de residuos propia"),
        ("const votoDe =", "una sola puerta para leer la capa"),
        ("(v + domResid()) / (2*domResid())", "el residuo usa un dominio simétrico con el cero al centro"),
        ("v / V.dominio_voto", "el voto usa el dominio único del paquete"),
        ("function leyendaVoto(", "la capa tiene su propia leyenda"),
        ("function avisoVoto(", "la capa tiene su propio aviso"),
        ("function fichaVoto(", "la ficha de la localidad tiene su bloque de voto"),
        ("'poblacion','opinion','crecimiento','voto'", "la capa se oculta en vista Ciudad, como las otras"),
        ("No pre-registrado.", "la vista exploratoria lo dice"),
        ("inscrita</i>, no donde vive", "el aviso dice la salvedad de inscripción"),
        ("V.votos_sin_localidad", "el aviso cita los votos sin localidad desde el paquete"),
        ("ecológico", "el aviso dice que es ecológico"),
        ("Son dos polos, no un eje.", "el aviso da la lectura de dos polos (DI-V59)"),
        ("const poloDe =", "una sola puerta para saber el polo de una opción"),
        ("Lectura descriptiva, no pre-registrada", "la lectura de dos polos se declara no pre-registrada en el aviso"),
        ("if(!V) document.querySelector('[data-capa=\"voto\"]').remove();", "sin paquete, no hay botón"),
    ]:
        probar(que, marca in p)

    # Ninguna cifra del análisis puede estar escrita a mano en la plantilla: si se
    # rehace el análisis, la página tiene que cambiar sola (como DI-V34 con la escala).
    plantilla = (RAIZ / "src" / "viz" / "plantilla_mapa.html").read_text(encoding="utf-8")
    probar("la plantilla no trae escritas las cifras del análisis",
           all(x not in plantilla for x in ("0,87", "0,874", "84 %", "84,0", "3,04", "0,70", "0,77", "0,86", "0,42")))
    probar("las rampas nuevas son distintas de las que ya existían",
           "[[175,158,205]" in p and "[[128, 70, 15]" in p and "[[  0,143,137]" in p and "[[ 20, 88,146]" in p)
    probar("la página sigue siendo autocontenida salvo tipografías (DI-V6)",
           p.count("https://") == p.count("https://fonts.") + p.count("https://opendatacommons.org"))

    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron: {', '.join(FALLOS)}")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
