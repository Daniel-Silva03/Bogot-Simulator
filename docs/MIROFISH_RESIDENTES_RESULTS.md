# MIROFISH CON RESIDENTES DE BOGOTÁ, ENTREVISTADOS — resultados

Corrido el **9 de octubre de 2026** contra `MIROFISH_RESIDENTES_SPECIFICATION.md` (pre-registro y código en `f93fffc`, antes
de llamar). **Gasto total: USD 0,15**, dentro del tope de USD 1 (el saldo pasó de 16,3557 a 16,5049):
- la corrida que terminó: USD 0,12;
- cuatro intentos trabados en la ontología y dos diagnósticos (§5): unos USD 0,03.

## 1. Qué hizo MiroFish

- **Agentes:** 32. **Once son residentes** de la semilla; faltó Hernando Quintero, de estrato 3. Los demás son
  instituciones y medios.
- **Simulación:** 10 rondas, con 87 acciones.
- **Entrevistas:** las cinco preguntas, con la simulación abierta. Respondieron los 32 agentes, en Reddit.
- **Las respuestas** quedan en `data/processed/mirofish/residentes/entrevistas.json`, sin subir.

## 2. Contra la regla

| Pregunta | EPC 2025 | MiroFish (residentes, ponderado) | Simulador |
|---|---|---|---|
| Satisfecho con Bogotá | 61 % | 72,1 % | 51,2 % |
| Orgulloso de Bogotá | 57 % | 100 % | 48,7 % |
| Va por buen camino | 59 % | 0 % | 33,3 % |
| Aprueba a Galán | 26 % | 0 % | 47,3 % |
| Víctima de delito | 15 % | 0 % | 25,3 % |

| | MiroFish | Simulador (no decide) | 50 % para todo |
|---|---|---|---|
| Error medio | **30,8** | 15,1 | 17,2 |
| Spearman con la EPC 2025 | 0,45 | 0,70 | — |
| Separación | 100 | 25,9 | 0 |

| | Criterio | MiroFish | |
|---|---|---|---|
| R1 | Spearman ≥ 0,7 | 0,45 | **no se cumple** |
| R2 | Separación ≥ 20 | 100 | se cumple |
| R3 | Error medio < 17,2 | 30,8 | **no se cumple** |

**MiroFish con residentes no distingue** (§5). Se equivoca casi el doble que decir 50 % para todo.

| | Predicción | Resultado | |
|---|---|---|---|
| PR1 | No cumple la regla | no la cumple | se cumple |
| PR2 | El simulador se equivoca menos | 15,1 contra 30,8 | se cumple |
| PR3 | MiroFish exagera la victimización (más de 25 %) | 0 % | **falla** |

**El simulador, que no decidía,** cumple los tres criterios: Spearman 0,70, separación 25,9 y error 15,1. Hay que leerlo con
cuidado: para cuatro de las cinco preguntas usa el dato medido de 2022-2024, y el «buen camino» subió mucho en 2025 (de
33 % a 59 %), algo que no podía anticipar.

## 3. Lo que muestran las respuestas

**Muchos «NO» no son opiniones: son negativas a opinar.** Esto se cuenta después de ver las respuestas, y no está
pre-registrado:

| Pregunta | «No tengo información», «soy una cuenta simulada»… |
|---|---|
| Aprueba a Galán | 10 de 11 |
| Víctima de delito | 10 de 11 |
| Buen camino | 3 de 11 |
| Satisfacción | 2 de 11 |
| Orgullo | 0 de 11 |

Algunos ejemplos, textuales:
- **Aprobación:** «NO. No tengo información suficiente para aprobar o desaprobar su gestión sin evaluar resultados
  concretos».
- **Víctima de delito:** «NO; soy una cuenta simulada y no tengo experiencias personales verificables».
- **Orgullo:** los 11 dicen «SÍ», con frases casi iguales sobre «la diversidad y el esfuerzo de su gente».

## 4. Qué se aprende

1. **Luna no hace de encuestado.** Aunque tenga un personaje con barrio, estrato y oficio, se sale de él para no
   inventarse una opinión política ni una experiencia. Cuando acepta opinar, da la respuesta socialmente cómoda: orgullo,
   sí; buen camino, no. No hay variedad entre residentes: estrato 1 y estrato 6 responden lo mismo.
2. **Es lo que encontró el Experimento 8,** por otra vía: el modelo de lenguaje no reemplaza las respuestas de las
   personas.
3. **Lo que sí sirve es lo medido.** Con datos de 2022-2024, el simulador ordena las cinco preguntas casi como la EPC 2025.
   Donde más falla es donde la ciudad cambió («buen camino») o donde no tiene dato (Galán).
4. **Con eso, las cuatro pruebas de MiroFish cuentan lo mismo:** no sirve para cifras de opinión. Sirve para ordenar
   temas y marcos de discusión.

## 5. Lo que pasó en las corridas (DI-MF8 a DI-MF10)

- **Tres intentos se trabaron en la ontología,** el primer paso, y uno más se detuvo por falta de tiempo.
- **La causa:** MiroFish pide la ontología sin límite de largo, y esta tarde Luna no la terminó ni en 30 minutos. Con la
  tabla de residentes, la ontología es más larga.
- **Una llamada aparte con tope** terminó en 5 minutos.
- **Se corrigió:**
  - un tope de 16.000 tokens para la ontología;
  - 30 minutos de espera por llamada;
  - sin reintentos automáticos, que cobraban respuestas que nadie recibía.

  Los cambios están en la instalación local de MiroFish y se activan por variables de entorno.
- **El modelo no cambió.** El quinto intento corrió completo.

## Corrección (13/10/2026): la cifra real de «buen camino» es 48,2 %, no 59 %

Al verificar la EPC 2025 contra sus microdatos (`DATA_INVENTORY.md` §13.10), la pregunta «¿las cosas en Bogotá van por buen
camino o por mal camino?» (`GOB_1`) da **48,2 %**. Es el «optimismo sobre el rumbo» que reportó la prensa. El 59 % que se
usó aquí, tomado de la misma nota de El Tiempo, no corresponde a esta pregunta. Las otras cuatro cifras sí coinciden con
los microdatos.

**Recalculado con las cinco cifras de los microdatos** (61,4; 56,6; 48,2; 26,4; 14,6):

| | Error medio | Spearman |
|---|---|---|
| Simulador | 12,9 (antes 15,1) | 0,90 (antes 0,70) |
| MiroFish con residentes | 28,7 (antes 30,8) | 0,78 (antes 0,45) |
| TinyTroupe A | 25,2 (antes 27,2) | 0,87 (antes 0,62) |
| TinyTroupe B | 27,1 (antes 29,1) | 0,78 (antes 0,45) |
| 50 % para todo | 15,8 (antes 17,2) | — |

**Qué cambia en la regla:**
- **R1 (Spearman ≥ 0,7)** pasa a cumplirse en las herramientas. El orden de las cinco preguntas se parece más al real que
  lo que decía la cifra equivocada.
- **R3 (error menor que decir 50 % para todo)** sigue sin cumplirse, y por mucho.

**El veredicto no cambia: no pasan.** Lo de arriba no se borra (§45).
