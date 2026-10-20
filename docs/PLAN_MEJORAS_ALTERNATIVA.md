# INSTRUCCIONES DE ACTUALIZACIÓN: Simulador de Opinión Pública Bogotá

**Rol:** Eres un Científico de Datos Senior y experto en simulaciones con LLMs. Tu tarea es implementar una serie de mejoras estructurales y matemáticas al Simulador de Opinión Pública de Bogotá.

**Contexto del Sistema:** 
Actualmente usamos la EPC (Encuesta de Percepción Ciudadana) 2022-2025, encuestas propias (cuyos microdatos no pueden ir al LLM) y una población sintética de 20.000 agentes. El enfoque actual de *roleplay* ciudadano individualizado con 200 agentes LLM genera demasiado ruido (±7 puntos por azar) y no captura bien el paso del tiempo post-encuesta.

**Objetivo de esta iteración:**
Evolucionar de un modelo de *roleplay* puro a un **Proyector Estructural**, utilizando el LLM para modelar distribuciones demográficas y razonamiento experto, pero apoyándonos en modelos matemáticos y anclas empíricas para predecir el comportamiento a nivel de ciudad.

A continuación, detallo las 4 estrategias principales a implementar. Procede paso a paso según mis indicaciones futuras, utilizando este documento como mapa de ruta.

---

## 1. Mapeo de Preguntas a un Espacio Latente (Reducción a Dimensiones)
**Objetivo:** Reducir la varianza del LLM y escalar a los 20.000 agentes al instante sin llamadas individuales repetitivas.
**Implementación requerida:**
- **Paso 1:** Escribe un *script* para que el LLM clasifique cualquier pregunta entrante en un espacio de 4 dimensiones latentes (ej. Izquierda/Derecha, Oficialismo/Oposición, Optimismo/Pesimismo, Pro/Anti-Galán) asignando un peso a cada eje.
- **Paso 2:** Desarrolla el código en Python para calcular la posición exacta de nuestros 20.000 agentes sintéticos en estos mismos ejes, utilizando sus respuestas históricas de la EPC 2024.
- **Paso 3:** Implementa una función de distancia (ej. similitud coseno o euclidiana) donde la probabilidad de que un agente responda afirmativamente dependa de su cercanía al vector de la nueva pregunta.

## 2. Calibración MRP (Multilevel Regression and Poststratification) con Anclas Agregadas
**Objetivo:** Evitar predicciones fuera de la realidad anclando el promedio global a encuestas de medios recientes, usando al LLM solo como "distribuidor".
**Implementación requerida:**
- **Paso 1:** Configura el sistema para que, al ingresar un dato macro público (ej. Aprobación Galán = 40% según Invamer), los 200 agentes LLM se ejecuten únicamente para estimar las *pendientes demográficas* (las diferencias relativas de opinión entre estratos, edades y localidades).
- **Paso 2:** Escribe el ajuste matemático (el intercepto) para que la curva demográfica proyectada por los agentes se calibre forzosamente al dato ancla general, garantizando el 40% a nivel ciudad pero conservando la distribución por localidad y perfil.

## 3. Dinámica de Opinión en Red (Modelos Hegselmann-Krause / DeGroot)
**Objetivo:** Simular el impacto de noticias coyunturales mediante propagación social matemática, en lugar de pedirle al LLM que "lea noticias".
**Implementación requerida:**
- **Paso 1:** Construye un modelo de grafo (`NetworkX` o similar) que conecte a los 20.000 agentes. Define los enlaces (aristas) basándote en afinidad sociodemográfica (localidad compartida, estrato, grupo etario).
- **Paso 2:** Programa un modelo de Confianza Limitada (Hegselmann-Krause).
- **Paso 3:** Define el mecanismo de "Choque": una función donde una noticia altera la opinión inicial solo de un subconjunto de nodos altamente informados, y luego el algoritmo propaga el cambio por la red hasta el equilibrio.

## 4. Panel de "Superpronosticadores" Sintéticos
**Objetivo:** Sustituir la simulación de "ciudadano promedio" en preguntas complejas nacionales por paneles de expertos sintéticos, que son más precisos al usar datos agregados.
**Implementación requerida:**
- **Paso 1:** Diseña 5 *system prompts* robustos de expertos analíticos (ej. Estratega político, Sociólogo de datos, Periodista local).
- **Paso 2:** Estructura un *prompt* que inyecte "Estado Empírico" cuantitativo (indicadores DANE, inflación, desempleo) y datos históricos de la EPC.
- **Paso 3:** Programa la recolección y promedio de la predicción numérica exacta que entreguen los 5 expertos frente a la nueva pregunta.

---

### Protocolo de Pruebas (Restricción Estricta)
Toda implementación generada debe someterse a nuestras pruebas pre-registradas. El criterio de éxito base es **vencer a la métrica de "repetir el último dato medido de la EPC"**.
- Usa la EPC 2024 como entrenamiento/contexto.
- Usa la EPC 2025 oculta como *Ground Truth* para evaluar el error.
- Costo máximo por pregunta: < USD 0,05 (optimiza los *prompts* y prefiere las soluciones de espacio latente y matemáticas en Python sobre la generación de texto masiva).

**¿Entendido? Confirma la recepción de estas instrucciones y dime por cuál de los 4 módulos prefieres que empecemos a escribir el código.**