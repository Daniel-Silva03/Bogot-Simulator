# MIROFISH ANTE LA APROBACIÓN DE GALÁN — resultados

Corrido el **9 de octubre de 2026** contra `MIROFISH_GALAN_SPECIFICATION.md` (pre-registro y código en `5223861`, antes de
llamar). **Gasto total: unos USD 0,05**, dentro del tope de USD 1:
- paso 0: USD 0,0001;
- simulador: unos USD 0,003;
- simulación de MiroFish y un primer informe a medias: USD 0,037;
- informe rehecho: USD 0,0097.

## 1. Paso 0: Luna no conoce la cifra

A la pregunta directa por la aprobación de Galán en la EPC 2025, Luna respondió: «No lo sé con certeza y no quiero adivinar
el porcentaje». La prueba sigue.

## 2. Qué dio cada uno

**MiroFish:**
- **Agentes:** 15, sacados del documento: el alcalde, el presidente, los medios, entidades. **Ningún residente común.**
- **Simulación:** 10 rondas, con 26 acciones en Twitter y 34 en Reddit.
- **Su cifra, textual:** «模拟对成年波哥大居民施政认可度的预测为 **46%**». Es decir: los adultos de Bogotá aprueban la
  gestión en un 46 %.
- **De dónde sale, según el propio informe:**
  - la entrevista obtuvo respuesta de «0/15 agentes», y en la lista «no hay ningún adulto común de Bogotá»;
  - el 46 % «no puede describirse como resultado calculado a partir de opiniones de residentes de la simulación»;
  - no trae muestra ni método de cálculo.
- **El informe** es `report_3a75557f92f2`, en chino, y queda en `data/processed/mirofish/galan/informe.md`, sin subir.

**El simulador** tomó la pregunta como nueva, la reformuló como «En Bogotá, ¿qué tanto aprueba o desaprueba la gestión del
alcalde Carlos Fernando Galán?» y la estimó así:
- **47,3 %, entre 25,6 % y 69,0 %: «dividida».**
- **Se apoyó en tres preguntas** de la Encuesta Distrital de Percepción 2025 de la Secretaría de Planeación, del gobierno
  de Galán. Ninguna es del CNC, así que su cifra se puede publicar.

**El dato anterior** (la calificación positiva de Claudia López en `GG3`, EPC 2022-2023): 33,1 %.

## 3. Contra el resultado real

**El resultado real:** el 26 % de aprobación en la Encuesta de Percepción Ciudadana 2025 de Bogotá Cómo Vamos.

| | Cifra | Error (puntos) |
|---|---|---|
| MiroFish | 46 | 20,0 |
| El simulador | 47,3 (25,6 a 69,0) | 21,3 |
| **El dato anterior (Claudia López, `GG3`)** | 33,1 | **7,1** |
| *Invamer, junio de 2025 (otra pregunta; no decide)* | *42* | *16* |

| | Predicción | Resultado | |
|---|---|---|---|
| PG1 | MiroFish da una cifra | 46 % | se cumple |
| PG2 | MiroFish se equivoca más de 10 puntos | 20,0 | se cumple |
| PG3 | El rango del simulador incluye el 26 % | 25,6 a 69,0 | se cumple, por 0,4 |
| PG4 | Luna no conoce la cifra | no la conoce | se cumple |

**Regla (§4):** MiroFish no se equivoca menos que el dato anterior (20,0 contra 7,1). **No sirve para estimar aprobación;
queda como herramienta para explorar narrativas.**

## 4. Qué se aprende

1. **Sin una cifra que reescalar, MiroFish no acierta.** En la segunda vuelta acertó porque reescaló la primera vuelta del
   documento. Aquí no había nada que reescalar, y dio un 46 % sin base.
2. **Sus agentes no son la población.** Las dos veces, MiroFish creó agentes con los actores del documento (políticos,
   medios, entidades), no con residentes, y las entrevistas no respondieron. Lo que simula es una conversación entre
   instituciones, no una opinión pública.
3. **El simulador tampoco acierta, pero lo dice.** Dio un número cerca del medio, igual que MiroFish, y lo marcó como
   «dividida», con un rango que apenas alcanza el 26 %. Sin una pregunta medida sobre Galán, no tiene con qué.
4. **Lo mejor fue la referencia más simple:** la aprobación de la alcaldesa anterior, medida en la misma encuesta. Las dos
   herramientas quedaron muy por detrás.
5. **Lo que MiroFish sí aporta:** un mapa ordenado de los temas y de los marcos en disputa (el agua, el pasaje y el choque con
   Petro, la seguridad), y la honestidad de decir que no tiene voces de residentes. Puede servir para preparar un
   cuestionario o un análisis cualitativo, no para dar cifras.

## 5. Errores del script (DI-MF6), sin efecto en la cifra

- **Justo después de pedir el informe,** el script consultó su avance antes de que existiera, recibió un 404, cerró MiroFish
  y el informe quedó a medias. La simulación ya estaba guardada.
- **Se corrigió:** un 404 al esperar cuenta como «todavía no», y `--informe` rehace solo el informe. Así se generó
  `report_3a75557f92f2`.
- **Un intento de rehacerlo falló sin gasto,** por la carpeta de trabajo.
