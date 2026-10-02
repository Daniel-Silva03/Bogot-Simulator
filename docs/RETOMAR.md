# RETOMAR — dónde quedó la sesión del 30/09-1/10/2026

**Para seguir en otro computador. Léelo después de `ESTADO_DEL_PROYECTO.md`.**

## Lo que se hizo en estas dos jornadas (todo en GitHub)

1. **Página de consulta (D17)** con la población EPC 2022-2024 (`PAGINA_CONSULTA.md` §5.5-5.7):
   cada pregunta del catálogo dice de qué años sale; preguntas nuevas con la fuerza del puente y las
   barras por grupo escondidas tras «ver de todos modos».
2. **Pruebas del puente en preguntas nuevas**, todas contra pre-registro o regla escrita antes:
   - `PUENTE_LOCALIDADES_RESULTS.md`: el puente no ordena localidades (artefacto de ruido compartido). Lectura B.
   - `PUENTE_SIN_BASE_RESULTS.md`: «sin base» no es confiable; la fuerza sí separa casos.
   - `PREGUNTAS_REALES_NUEVAS_RESULTS.md`: metro elevado y Corredor Verde (encuesta del CNC, 2023): 8 de 24, el Corredor al revés.
   - `BANCO_PREGUNTAS_NUEVAS.md` §10: **banco de 165 preguntas reales nuevas** (114 práctica / 51 guardadas,
     sorteo con semilla 20261001). Tres versiones del puente en la práctica (actual, «afectados»,
     perfiles+ejemplos con validación cruzada): **60-63 % de diferencias entre grupos bien ordenadas,
     igual que el «tono general» sin API (62 %)**. La regla de salida (67 %) dijo **parar**.
3. **Traslado:** `TRASLADO.md`, `requirements.txt` completo, `revisar_datos.py` al día, `empacar_traslado.py`.

## La decisión pendiente (lo primero al retomar)

Por la regla escrita (`BANCO_PREGUNTAS_NUEVAS.md` §10.3), la página adopta el «camino 2» para las
preguntas nuevas. Propuesta hecha a Daniel, **sin respuesta todavía**:

1. **Grupos:** mostrar el tono general por grupo, a la vista, rotulado «Así suelen responder estos
   grupos en la encuesta» (no es una medición de esta pregunta). Reemplaza las barras del puente.
2. **Preguntas relacionadas:** junto a las preguntas del catálogo en que se apoyó el modelo, mostrar lo
   que la gente respondió de verdad a cada una, con enlace a verla completa con su mapa.
3. **Quitar el nivel propuesto por el modelo** (en la prueba real dio 3,7 en las dos preguntas y no
   distinguió cuál tenía más apoyo).

Escribirlo como **D18** en `PROJECT_CONTEXT.md` §39 cuando Daniel lo apruebe (o cambie).

**Resuelta el 2/10 en el PC del CNC:** Daniel aprobó los tres puntos, sin cifra propia y sin la
fuerza. Es **D18**, y está en la página (`PAGINA_CONSULTA.md` §5.8). No queda decisión pendiente
de esta nota.

## Otras cosas abiertas

- Segunda vuelta 2026 (`SEGUNDA_VUELTA_2026_SPECIFICATION.md`): esperando los datos mesa a mesa del CNC.
- El banco guardado (51 preguntas) no se ha usado: queda para probar una idea nueva de verdad, pre-registrada.
- `Claude Setup.exe` apareció en `data/processed/` del computador de casa: no es del proyecto; no se empacó.
- La memoria de Claude (`~/.claude/…`) no viaja con el repo; lo necesario está en estos documentos.
