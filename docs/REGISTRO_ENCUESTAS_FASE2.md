# PLAN V3, FASE 2: EL REGISTRO DE ENCUESTAS PÚBLICAS DE GALÁN

Hecho el **19 de octubre de 2026**, siguiendo `PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V3.md` §6. **Gasto: USD 0.** Es un registro, no una
prueba: no lleva pre-registro.

**El archivo:** `config/mediciones_publicadas.csv`. Lo revisa `tests/test_mediciones_publicadas.py`, que comprueba:
- que estén los campos del plan;
- una fila por medición;
- que cada dato diga de dónde salió;
- que cada serie sea un solo concepto de una sola encuestadora;
- que ninguna fecha de campo quede después de la publicación.

## 1. Qué tiene

**19 mediciones, en 5 series que no se mezclan:**

| Serie | Concepto | Encuestadora | Mediciones | Periodo |
|---|---|---|---|---|
| `invamer_aprobacion` | aprobación de la gestión | Invamer | 9 | feb. 2024 – jun. 2025 |
| `guarumo_aprobacion` | aprobación de la gestión | Guarumo y EcoAnalítica | 1 | abr. 2026 |
| `cb_calificacion` | calificación de la gestión (muy buena o buena, de cuatro) | CB Global Data | 6 | mar. – sep. 2026 |
| `epc_gestion` | calificación de la gestión (buena o muy buena, de cinco con «regular») | EPC | 2 | 2024, 2025 |
| `epc_imagen` | imagen favorable | EPC | 1 | 2025 |

**De dónde salió cada dato:**

| Verificación | Mediciones |
|---|---|
| informe original | 1 (Guarumo) |
| nota de prensa | 13 |
| nota de prensa, vía resumen del buscador | 1 (Invamer, feb. 2024) |
| microdato propio | 3 (EPC) |
| pendiente: derivada | 1 (CB, sep. 2026: agosto menos la caída publicada) |

**Lo que falta**, marcado «pendiente», nunca inferido:
- **la pregunta exacta:** 16 de 19;
- **las fechas de campo, la muestra de Bogotá, el método y el margen:** unas 12 de 19;
- **el «no sabe»:** 18 de 19.

## 2. Lo que se aprendió armándolo

1. **La prensa casi nunca publica la ficha técnica.** Para completarla hacen falta los informes originales.
   - **Invamer:** el informe de junio de 2025 está en la web, pero es un PDF de imágenes que no se pudo leer.
   - **Guarumo:** su informe sí trae texto y dio la ficha completa: 664 encuestados en Bogotá, margen de ±4,5 y la pregunta
     literal.
2. **Lo que CB llama «imagen positiva» es una calificación de la gestión:** «muy buena» más «buena», de cuatro opciones. La prensa
   la llama «imagen», «favorabilidad» o «aprobación» según el medio. Es online, con cuotas: no es una muestra probabilística.
3. **Guarumo mide a los adultos con intención de votar,** no a todos los adultos. Por eso no se promedia con Invamer, aunque la
   pregunta se parezca.
4. **La EPC califica la gestión en cinco puntos con «regular».** Por eso da menos «buena» que la escala de cuatro de CB, sin que
   eso sea un cambio de opinión: 26 % en la EPC 2025 contra 43-49 % en CB en 2026.
5. **Las series casi no se cruzan en el tiempo.** No hay dos encuestadoras midiendo el mismo concepto en el mismo mes. Por eso,
   como dice el plan (§6.3 y §8.2), **no se agrega nada todavía:** las mediciones se muestran separadas, con su fecha y su fuente.

## 3. Lo que queda para completarlo

- **Leer a mano los informes de Invamer** (Invamer Poll) para la pregunta, el método y la muestra de Bogotá. Son PDF de imágenes.
- **Buscar los informes de CB Global Data** en su sitio, con la ficha por ciudad.
- **Sumar nuevas mediciones a medida que salgan,** con la misma regla: de dónde salió cada dato y nada inferido.
