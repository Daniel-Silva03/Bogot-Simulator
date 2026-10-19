# GALÁN HOY: ¿SE ACERCAN LOS AGENTES A LA MEDICIÓN MÁS RECIENTE? — mejora 2 del daily

Pre-registro escrito el **19 de octubre de 2026**, antes de ver la cifra real. Lo pidió Daniel: la percepción de Galán es el
resultado que más le importa a su jefe, y lo ideal es acercarse a una medición actual. Gasto: **unos USD 0,06, con tope de USD 1**.

## 1. Pregunta

En `GRUPOS_Y_GALAN_2026`, cada perfil acertó una de las dos mediciones de 2026:
- **sin opiniones de gobierno (P),** la aprobación de Guarumo de abril;
- **con todo el perfil (F),** la imagen de CB de junio.

Ninguno bajó del error de repetir el dato de la EPC 2025. **¿Combinarlos, o avisarle al agente que su opinión es de hace un
año, lo acerca a la medición más reciente de Galán?**

## 2. Lo real (aún no visto)

- **La medición:** el ranking de alcaldes de capitales de CB Global Data, de **septiembre de 2026** (publicado el 30 de
  septiembre). Es lo más reciente publicado y la misma serie que G2 (CB, junio de 2026).
- **La cifra:** la imagen positiva de Galán en Bogotá.
- **Lo que no se sabe de la ficha:** la nota no da la pregunta exacta, la escala, la muestra ni el método. Se usa la misma
  pregunta y escala de G2 («¿Qué imagen tiene usted del alcalde de Bogotá, Carlos Fernando Galán?», cuatro puntos), y se cuenta
  positiva o muy positiva.

**Se declara, antes de ver la cifra:**
- El buscador mostró, sin pedirlo, que en septiembre Galán tuvo **la mayor caída de la región: −3,5 puntos frente a agosto.**
  El nivel de septiembre no lo he visto, y tampoco el de agosto.
- Del lado de los agentes, P, F y su mezcla **ya se conocen** (G2 de la prueba anterior): 57,9, 46,9 y unos 52,4. Lo único a
  ciegas es la cifra real. El brazo FT (§3) es nuevo.

## 3. Los brazos

Los 200 agentes del panel, con probabilidades y la misma llamada de G1 y G2 de `GRUPOS_Y_GALAN_2026`. Se usa G2.

| Brazo | Qué es | Llamadas |
|---|---|---|
| P | sin opiniones de gobierno; de la caché | 0 |
| F | con todo el perfil; de la caché | 0 |
| **M, la combinación** | mitad y mitad: la distribución de cada agente es el promedio de la de P y la de F | 0 |
| **FT, el aviso** | F, más esta nota después del perfil | 200 |

La nota de FT:

> Las respuestas de arriba son de 2025. Estas preguntas son de septiembre de 2026, casi un año después: la persona puede haber
> cambiado de opinión sobre el alcalde.

No dice en qué dirección cambió ni da ninguna cifra.

## 4. Las referencias

- **repetir la EPC 2025:** la imagen favorable de Galán, 45,0;
- **repetir la última de CB antes de septiembre (agosto):** por lo declarado en §2, su error es de unos 3,5 si la caída es en la
  misma cifra;
- **repetir CB de junio (G2):** 44,3.

## 5. Reglas (escritas antes de ver la cifra)

**La combinación (M) se acerca a Galán hoy si cumple las tres:**
- **RG1:** su error es de **4 puntos o menos.**
- **RG2:** su error es menor que el de repetir la EPC 2025.
- **RG3:** su error es menor que el de repetir CB de agosto.

**El aviso (FT)** se juzga con las mismas tres (RT1, RT2, RT3).

No se elige el mejor brazo después de ver la cifra: se reportan los dos contra sus reglas.

## 6. Predicciones

- **PG1.** La cifra real de septiembre queda entre 38 y 46.
- **PG2.** M no cumple RG1: con unos 52,4, queda alto.
- **PG3.** FT queda por debajo de F (el aviso baja la imagen).
- **PG4.** Ningún brazo le gana a repetir CB de agosto (RG3 y RT3 no se cumplen).

## 7. Gasto, código y orden

- **Gasto:** 200 llamadas (FT), unos USD 0,06, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC (pública, anónima) y el texto de G1, G2 y la nota.
- **Código:** `src/experiments/galan_actual.py`, con su prueba. Resultados en `GALAN_ACTUAL_RESULTS.md`.
- **El orden:** se sube este pre-registro; se corre FT; después se buscan las cifras de CB de septiembre y agosto, y se anotan
  con su fuente en los resultados.
