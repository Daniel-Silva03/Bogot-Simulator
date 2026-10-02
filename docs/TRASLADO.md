# TRASLADO — pasar el proyecto a otro computador

**GitHub trae el código, los documentos y los resultados. Lo demás se copia a mano, en tres paquetes.**

Fecha: 1 de octubre de 2026 (primer traslado al computador de la oficina)

---

## 1. En el computador de origen

1. Que todo esté subido:
   ```
   git status        # solo debe aparecer .claude/
   git push
   ```
2. Empacar lo pequeño que solo existe aquí (cachés de la API, poblaciones construidas, resultados
   locales, diccionario de la ECP; ~4 MB):
   ```
   python src/utils/empacar_traslado.py
   ```
   Deja `bss_traslado_<fecha>.zip` en el Escritorio.
3. Copiar a una memoria, OneDrive o la red de la oficina:

| Qué | Dónde está | Peso | Para qué |
|---|---|---|---|
| El zip del paso 2 | Escritorio | ~4 MB | cachés (sin ellas, rehacer análisis vuelve a gastar), poblaciones, resultados |
| `data/raw/` | dentro del repo | ~1,3 GB | encuestas fuente (EPC, ECP del DANE, Multipropósito); **nunca va a GitHub** |
| `CNC_datos/` | `C:\Users\User\Desktop\CNC_datos` | ~1,8 GB | resultados electorales (D16) y la biblioteca pública del CNC. Solo hace falta para Polos 2026 y la segunda vuelta |

**Lo que NO se copia:** los microdatos del CNC con datos de personas (R10, `DATA_INVENTORY.md`
§12.4). La página y los experimentos actuales no los usan. Si algún día hicieran falta en la
oficina, es una decisión aparte.

## 2. En el computador de destino

1. Python 3.11 (el que se usó aquí es 3.11.9) y git.
2. Clonar e instalar:
   ```
   git clone <url del repositorio>
   cd bogota_social_simulator
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Poner `data/raw/` dentro del repo, tal cual (misma estructura de carpetas).
4. Extraer el zip **desde la raíz del repo**:
   ```
   python src/utils/empacar_traslado.py --extraer <ruta>\bss_traslado_<fecha>.zip
   ```
5. Si copiaste `CNC_datos/`, en cada terminal donde la uses:
   ```
   $env:BSS_ELECTORAL_DIR = "<ruta>\CNC_datos"
   ```
6. La clave de OpenRouter, en cada terminal donde se llame a la API (nunca en un archivo):
   ```
   $env:OPENROUTER_API_KEY = "..."
   ```
7. Revisar:
   ```
   python src/utils/revisar_datos.py
   ```
   Todo en `[OK ]`, salvo la clave y la carpeta electoral si no las pusiste (`[opc]`).
8. Probar:
   ```
   python tests/test_consulta.py
   python src/consulta/servidor.py --simulado
   ```
   y abrir `http://127.0.0.1:8765`.

## 3. Si algo falla

- **Falta una librería:** `pip install -r requirements.txt` dentro del venv.
- **Faltan las poblaciones** (no copiaste el zip): se regeneran, en este orden, en unos minutos:
  `python src/population/poblacion_epc.py` y `python src/population/poblacion_epc_olas.py`.
- **La EPC está en otra carpeta:** `$env:BSS_EPC_DIR = "<ruta a 'Microdatos 2014 - 2025'>"`.
- **Faltan las cachés:** todo corre igual; solo que repetir un análisis con la API vuelve a gastar y
  puede dar resultados un poco distintos. Los resultados ya publicados están en GitHub.
- `.claude/launch.json` (la configuración del navegador de Claude) no viaja: tiene la ruta del
  Python de este computador. Claude lo recrea cuando haga falta.
