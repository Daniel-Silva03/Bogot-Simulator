"""
src/utils/seeds.py

Derivación de semillas para las corridas de un experimento.

POR QUÉ NO `seed_base + i`
---------------------------
Lo obvio sería numerar las corridas y usar `seed_base + i`. Tiene dos
problemas concretos para este proyecto:

1. Agregar una configuración al barrido corre la numeración de todas las
   posteriores, así que una corrida que antes tenía la semilla 137 pasa a
   tener otra. Los resultados de dos versiones del mismo experimento
   dejan de ser comparables corrida por corrida sin que nada avise.

2. Semillas consecutivas producen secuencias correlacionadas en algunos
   generadores. Con `numpy.random.default_rng` (PCG64) el riesgo es bajo,
   pero no hay razón para correrlo.

En su lugar, la semilla se deriva de un hash de la semilla base más los
identificadores de la corrida (nombre de la configuración, número de run).
Eso hace que cada corrida tenga una semilla estable y determinista que
depende solo de su propia identidad: agregar o quitar configuraciones no
mueve las semillas de las demás, y volver a correr el mismo experimento
seis meses después da exactamente los mismos números.
"""

from __future__ import annotations

import hashlib

# numpy acepta semillas hasta 2**32-1 en muchas rutas; se recorta ahí para
# evitar sorpresas de plataforma.
MAX_SEMILLA = 2**32 - 1


def semilla_para(seed_base: int, *componentes: object) -> int:
    """
    Semilla determinista para una corrida concreta.

    >>> semilla_para(42, "territorial_k10_h20", 7) == semilla_para(42, "territorial_k10_h20", 7)
    True

    Los componentes se convierten a texto, así que sirven strings, enteros
    o cualquier cosa con `str()` estable. No usar objetos cuyo `str()`
    incluya direcciones de memoria: la semilla dejaría de ser reproducible.
    """
    clave = "|".join([str(seed_base), *(str(c) for c in componentes)])
    digest = hashlib.blake2b(clave.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % MAX_SEMILLA
