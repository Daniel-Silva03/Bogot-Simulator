# AGENTES 2026: EL VOTO POR GRUPOS Y LA APROBACIÓN DE GALÁN — dos pruebas de D23

Pre-registro escrito el **16 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel: ver si los agentes reparten bien el
voto por grupos y si se acercan a la aprobación de Galán en 2026. Gasto: **parte A, USD 0** (usa la caché de `VOTO_CAMPANA`);
**parte B, unos USD 0,12, con tope de USD 1**. Falta el visto bueno de Daniel para la B.

---

## Parte A. El voto por grupos

### A1. Pregunta

En la primera vuelta de 2026, los 200 agentes con la campaña y la encuesta (C2, `VOTO_CAMPANA_RESULTS.md`) acertaron el total de
Bogotá con 3,5 de error. **¿Aciertan también cómo se reparte por sexo, estrato y edad?** Eso es lo que la encuesta publicada no
trae para Bogotá.

### A2. Datos

**Los agentes:**
- las respuestas de C2, leídas de la caché de `voto_campana`, sin llamar al modelo;
- sus grupos:
  - **sexo:** `DMO_1`;
  - **estrato:** `DMO_4_1`, en 1-2, 3 y 4-6;
  - **edad:** `DMO_3_1`, en joven (18-25), media (26-55) y mayor (56 o más).

  Son los cortes gruesos de `voto_grupos.GRUESOS`.

**Lo real por grupo:** la encuesta del CNC de mayo de 2026 (CC893701, Bogotá), con el voto por la fórmula de Cepeda (`P1_1`) y
la de De la Espriella (`P1_2`) en cada grupo. Se combinan con `voto_grupos.gruesos`. Es lo más cercano a la elección que trae
grupos.
- **Por D21,** sus cifras se calculan en el equipo y **no se imprimen:** se reporta solo el error.
- **Unos 305 encuestados en Bogotá:** cada grupo tiene su propio margen, de ±8 a ±14 puntos. La medida es ruidosa de los dos lados.

**La medida:** la parte de Cepeda entre los dos primeros, Cepeda / (Cepeda + De la Espriella), en cada uno de los 8 grupos.

### A3. Lo que se mide

- **Error por grupo de los agentes:** la media, sobre los 8 grupos, de la diferencia con el CNC.
- **Error de «la ciudad para todos»:** dar a cada grupo la cifra de los agentes para toda Bogotá. Es lo que daría un método que
  no distingue grupos.
- **El signo de las tres brechas** (mujeres contra hombres, estrato 1-2 contra 4-6, jóvenes contra mayores): si los agentes dicen
  hacia qué lado se inclina cada grupo igual que el CNC.

### A4. Regla

**Los agentes reparten bien por grupos si se cumplen las dos:**
- **RA1:** su error por grupo es al menos **1 punto menor** que el de «la ciudad para todos».
- **RA2:** aciertan el signo en al menos **2 de las 3 brechas.**

### A5. Predicciones

- **PA1.** RA2 se cumple: el estrato y la edad salen en la dirección esperada (más Cepeda en estratos bajos y en jóvenes).
- **PA2.** RA1 no se cumple: el ruido del CNC en grupos de 50 a 150 personas tapa la diferencia.

---

## Parte B. La aprobación de Galán en 2026

### B1. Pregunta

D23 trata la percepción del alcalde como pregunta nueva. **¿Se acercan los agentes a lo que midieron en 2026 otras encuestadoras?**

### B2. Lo real (publicado)

| # | Pregunta, como la hizo la encuestadora | Escala para el agente | Lo que se cuenta | Real | Fuente |
|---|---|---|---|---|---|
| G1 | ¿Usted aprueba o desaprueba la gestión del alcalde de Bogotá, Carlos Fernando Galán? | 1=Aprueba; 2=Desaprueba; 9=No sabe | Aprueba | 53,3 | Guarumo y Ecoanalítica, campo del 22 al 29 de abril de 2026 |
| G2 | ¿Qué imagen tiene usted del alcalde de Bogotá, Carlos Fernando Galán? | 1=Muy negativa; 2=Negativa; 3=Positiva; 4=Muy positiva; 9=No sabe | Positiva o muy positiva | 44,3 | Global CB, junio de 2026 |

**Lo que se declara:**
- **G2 se pide en cuatro puntos sin punto medio.** La nota publicada reporta «muy positiva» (18,9) y «favorable» (25,4), y no
  dice con qué escala exacta se preguntó.
- **Las dos son de otras encuestadoras,** con muestras nacionales y su submuestra de Bogotá.
- **Ya conozco las dos cifras.**

### B3. Los brazos

**Los 200 agentes del panel, con probabilidades, una llamada por persona con G1 y G2:**
- **P, sin sus opiniones de gobierno:** el perfil sin las siete preguntas de gobierno de `PERSONAS_POLITICA` (la gestión de
  Galán y del Concejo, la transparencia, la respuesta a la ciudadanía, la participación, el rumbo y la corrupción).
- **F, con todo el perfil:** incluida su calificación de la gestión de Galán en 2025.

**Las referencias:**
- **decir 50 %;**
- **el dato de la EPC 2025 más parecido:** la imagen favorable de Galán, 45,0 (`PERSONAS_POLITICA_RESULTS.md`), para las dos.

### B4. Regla

**Los agentes se acercan a la aprobación de Galán en 2026 si el mejor de P y F cumple las dos:**
- **RB1:** su error medio en G1 y G2 es de **7 puntos o menos**.
- **RB2:** su error medio es **menor que el de la EPC 2025** (45,0 para las dos).

### B5. Predicciones

- **PB1.** F se acerca más que P.
- **PB2.** No le gana a la EPC 2025 en G2: ese dato ya está casi exacto (45,0 contra 44,3).
- **PB3.** En G1, los agentes quedan por debajo del 53,3. Desde la EPC, Galán sale más mal calificado que en las encuestas
  telefónicas.

---

## Código y datos

- **Código:** `src/experiments/grupos_y_galan_2026.py`, con su prueba. Resultados en `GRUPOS_Y_GALAN_2026_RESULTS.md`.
- **Al modelo** (solo parte B) van los perfiles de la EPC (pública, anónima) y el texto de G1 y G2.
- **Las cifras del CNC por grupo** no se imprimen ni se suben.
