"""
src/scenarios/informe.py

Informe HTML autocontenido de un escenario.

El informe es parte del producto, no un adorno. El riesgo R05 del proyecto
—que los escenarios se lean como predicciones— está marcado como elevado, y
el sitio donde ese riesgo se materializa es exactamente aquí: en el gráfico
que alguien va a poner en una presentación.

DECISIONES DE DISEÑO
====================

DI-I1. **Nunca se dibuja una línea sola.** Toda trayectoria va con su banda
    de incertidumbre (p05-p95 y p25-p75) y con el escenario nulo al lado. Un
    número central sin banda no aparece en ningún lado del informe.

DI-I2. **El supuesto declarado se imprime completo**, con sus incertidumbres,
    arriba de los resultados. Quien lea el informe tiene que ver de dónde
    salen las cifras antes de ver las cifras.

DI-I3. **La descomposición de la incertidumbre es visible, no un apéndice.**
    Si el grueso viene del supuesto, el informe lo dice: el margen refleja lo
    que no sabemos, no lo que el modelo calculó.

DI-I4. **El gráfico de distribución se adapta a la escala.** Con pocas
    categorías, barras; con muchas, un área. Forzar barras sobre 154 valores
    produce una pared ilegible.

DI-I5. **Las advertencias van en el informe, no en la documentación.** Que
    esto no predice, que la red no aporta, que la tercera perilla se
    disolvió: van al pie de cada informe, siempre.
"""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

import numpy as np

from src.opinion.forzamiento_categorico import distribucion_de
from src.scenarios.especificacion import Escenario
from src.scenarios.motor import Resultado, comparar_con_nulo, correr, descomponer, escenario_nulo

AZUL_L, AZUL_D = "#2a78d6", "#3987e5"
NARANJA_L, NARANJA_D = "#eb6834", "#d95926"
W, H = 720, 300
MARGEN = dict(iz=64, de=24, ar=20, ab=44)


def _esc(t) -> str:
    return html.escape(str(t))


def _fmt(v: float) -> str:
    """La grilla puede ser entera (1-5) o racional (medias de k ítems)."""
    return f"{v:g}" if float(v).is_integer() else f"{v:.2f}"


def _escalas(xs, ys, pad_x: float = 0.0):
    x0, x1 = min(xs) - pad_x, max(xs) + pad_x
    y0, y1 = min(ys), max(ys)
    pad = (y1 - y0) * 0.15 or 0.1
    y0, y1 = y0 - pad, y1 + pad
    ix, iy = MARGEN["iz"], MARGEN["ar"]
    aw = W - MARGEN["iz"] - MARGEN["de"]
    ah = H - MARGEN["ar"] - MARGEN["ab"]
    fx = lambda v: ix + (0 if x1 == x0 else (v - x0) / (x1 - x0)) * aw          # noqa: E731
    fy = lambda v: iy + ah - (0 if y1 == y0 else (v - y0) / (y1 - y0)) * ah     # noqa: E731
    return fx, fy, (y0, y1)


def _grafico_trayectoria(r: Resultado, rn: Resultado, etiqueta_var: str) -> str:
    etiquetas = ["inicio"] + r.etiquetas
    xs = list(range(len(etiquetas)))
    q = lambda m, p: [r.media_inicial] + list(np.quantile(m, p, axis=0))        # noqa: E731
    p05, p25, p50, p75, p95 = (q(r.medias, p) for p in (.05, .25, .5, .75, .95))
    n50 = [rn.media_inicial] + list(np.quantile(rn.medias, .5, axis=0))
    n05 = [rn.media_inicial] + list(np.quantile(rn.medias, .05, axis=0))
    n95 = [rn.media_inicial] + list(np.quantile(rn.medias, .95, axis=0))
    fx, fy, (y0, y1) = _escalas(xs, p05 + p95 + n05 + n95)

    def area(lo, hi):
        a = " ".join(f"{fx(x):.1f},{fy(v):.1f}" for x, v in zip(xs, hi))
        b = " ".join(f"{fx(x):.1f},{fy(v):.1f}" for x, v in zip(reversed(xs), reversed(lo)))
        return f'<polygon points="{a} {b}"'

    def linea(v):
        return " ".join(f"{fx(x):.1f},{fy(y):.1f}" for x, y in zip(xs, v))

    ticks = np.linspace(y0, y1, 5)
    rejilla = "".join(
        f'<line x1="{MARGEN["iz"]}" x2="{W-MARGEN["de"]}" y1="{fy(t):.1f}" y2="{fy(t):.1f}" '
        f'class="rejilla"/><text x="{MARGEN["iz"]-10}" y="{fy(t)+4:.1f}" class="eje" '
        f'text-anchor="end">{t:.2f}</text>' for t in ticks)
    ejex = "".join(
        f'<text x="{fx(x):.1f}" y="{H-MARGEN["ab"]+22}" class="eje" text-anchor="middle">'
        f'{_esc(e)}</text>' for x, e in zip(xs, etiquetas))
    puntos = "".join(
        f'<circle cx="{fx(x):.1f}" cy="{fy(v):.1f}" r="4.5" class="pt" '
        f'data-t="{_esc(etiquetas[x])}" data-v="{v:.3f}" data-lo="{p05[x]:.3f}" '
        f'data-hi="{p95[x]:.3f}" data-n="{n50[x]:.3f}"/>' for x, v in zip(xs, p50))
    return f"""
<svg viewBox="0 0 {W} {H}" class="gr" role="img"
     aria-label="Trayectoria de la media con banda de incertidumbre, comparada con el escenario sin cambios">
  {rejilla}
  {area(n05, n95)} class="banda-nulo"/>
  {area(p05, p95)} class="banda-90"/>
  {area(p25, p75)} class="banda-50"/>
  <polyline points="{linea(n50)}" class="linea-nulo"/>
  <polyline points="{linea(p50)}" class="linea"/>
  {puntos}{ejex}
  <text x="{fx(xs[-1])-6:.1f}" y="{fy(p50[-1])-14:.1f}" class="dir azul" text-anchor="end">escenario</text>
  <text x="{fx(xs[-1])-6:.1f}" y="{fy(n50[-1])+20:.1f}" class="dir gris" text-anchor="end">sin cambios</text>
</svg>"""


def _grafico_distribucion(r: Resultado, p_inicial) -> str:
    """Distribución final contra la de partida (DI-I4: barras si caben, área si no)."""
    fin = r.distribuciones[:, -1, :].mean(axis=0)
    k = r.grilla
    xs = list(range(len(k)))
    pocas = len(k) <= 12
    # con barras, medio hueco de aire a cada lado: si no, la primera barra se
    # monta sobre las etiquetas del eje vertical
    fx, fy, (y0, y1) = _escalas(xs, [0] + list(fin) + list(p_inicial),
                                pad_x=0.6 if pocas else 0.0)
    if pocas:
        paso_px = (W - MARGEN["iz"] - MARGEN["de"]) / len(k)
        ancho = paso_px * 0.34
        gap = 2                     # el espaciador de 2px entre rellenos vecinos
        marcas = "".join(
            f'<rect x="{fx(x)-ancho-gap/2:.1f}" y="{fy(a):.1f}" width="{ancho:.1f}" '
            f'height="{max(fy(0)-fy(a),0):.1f}" rx="4" class="barra-ini" '
            f'data-t="{_fmt(k[x])}" data-v="{a:.4f}" data-s="al inicio"/>'
            f'<rect x="{fx(x)+gap/2:.1f}" y="{fy(b):.1f}" width="{ancho:.1f}" '
            f'height="{max(fy(0)-fy(b),0):.1f}" rx="4" class="barra" '
            f'data-t="{_fmt(k[x])}" data-v="{b:.4f}" data-s="al final"/>'
            for x, a, b in zip(xs, p_inicial, fin))
    else:
        ini = " ".join(f"{fx(x):.1f},{fy(v):.1f}" for x, v in zip(xs, p_inicial))
        pts = " ".join(f"{fx(x):.1f},{fy(v):.1f}" for x, v in zip(xs, fin))
        marcas = (f'<polygon points="{fx(xs[0]):.1f},{fy(0):.1f} {pts} '
                  f'{fx(xs[-1]):.1f},{fy(0):.1f}" class="areadist"/>'
                  f'<polyline points="{ini}" class="linea-nulo"/>'
                  f'<polyline points="{pts}" class="linea"/>')
    paso = max(1, len(k) // 8)
    ejex = "".join(
        f'<text x="{fx(x):.1f}" y="{H-MARGEN["ab"]+22}" class="eje" text-anchor="middle">'
        f'{_fmt(k[x])}</text>' for x in xs[::paso])
    ticks = np.linspace(0, y1, 4)
    rejilla = "".join(
        f'<line x1="{MARGEN["iz"]}" x2="{W-MARGEN["de"]}" y1="{fy(t):.1f}" y2="{fy(t):.1f}" '
        f'class="rejilla"/><text x="{MARGEN["iz"]-10}" y="{fy(t)+4:.1f}" class="eje" '
        f'text-anchor="end">{t*100:.0f}%</text>' for t in ticks)
    # la muestra de la leyenda tiene que ser la misma marca que el gráfico usa
    y0l = MARGEN["ar"]
    if pocas:
        m1 = f'<rect x="{W-MARGEN["de"]-150}" y="{y0l}" width="10" height="10" rx="3" class="barra-ini"/>'
        m2 = f'<rect x="{W-MARGEN["de"]-66}" y="{y0l}" width="10" height="10" rx="3" class="barra"/>'
    else:
        m1 = (f'<line x1="{W-MARGEN["de"]-152}" x2="{W-MARGEN["de"]-138}" '
              f'y1="{y0l+5}" y2="{y0l+5}" class="linea-nulo"/>')
        m2 = (f'<line x1="{W-MARGEN["de"]-68}" x2="{W-MARGEN["de"]-54}" '
              f'y1="{y0l+5}" y2="{y0l+5}" class="linea"/>')
    leyenda = (f'<g>{m1}<text x="{W-MARGEN["de"]-134}" y="{y0l+9}" class="eje">al inicio</text>'
               f'{m2}<text x="{W-MARGEN["de"]-50}" y="{y0l+9}" class="eje">al final</text></g>')
    return f"""
<svg viewBox="0 0 {W} {H}" class="gr" role="img"
     aria-label="Distribución de la variable al final del escenario, comparada con la de partida">
  {rejilla}{marcas}{ejex}{leyenda}
</svg>"""


def construir(esc: Escenario, corridas: int | None = None) -> str:
    r = correr(esc, corridas=corridas)
    rn = correr(escenario_nulo(esc), corridas=corridas)
    comp = comparar_con_nulo(esc, corridas=min(esc.corridas, 120))
    desc = descomponer(esc, corridas=min(esc.corridas, 120))
    resumen = r.resumen()

    final = comp.iloc[-1]
    supuestos = "".join(
        f"<tr><td>{_esc(p.etiqueta)}</td>"
        f"<td>{'cambio ' + format(p.nivel.cambio, '+.3f') if p.nivel.cambio is not None else 'valor ' + format(p.nivel.valor, '.3f')}"
        f" <span class='pm'>± {p.nivel.incertidumbre:.3f}</span></td>"
        f"<td>{'cambio ' + format(p.dispersion.cambio, '+.3f') if p.dispersion.cambio is not None else 'valor ' + format(p.dispersion.valor, '.3f')}"
        f" <span class='pm'>± {p.dispersion.incertidumbre:.3f}</span></td></tr>"
        for p in esc.periodos)

    fil_res = "".join(
        f"<tr><td>{_esc(x.periodo)}</td><td class='num'>{x.media:.3f}</td>"
        f"<td class='num'>{x.p05:.3f} – {x.p95:.3f}</td>"
        f"<td class='num'>{x.dispersion:.3f}</td></tr>"
        for x in resumen.itertuples())
    fil_cmp = "".join(
        f"<tr><td>{_esc(x.periodo)}</td><td class='num'>{x.escenario:.3f}</td>"
        f"<td class='num'>{x.sin_cambios:.3f}</td>"
        f"<td class='num'>{x.diferencia:+.3f}</td>"
        f"<td class='num'>{x.veces_el_error:.1f}×</td></tr>"
        for x in comp.itertuples())
    fil_inc = "".join(
        f"<tr><td>{_esc(x.fuente)}</td><td class='num'>{x.sd_de_la_media_final:.4f}</td>"
        f"<td class='num'>{'' if np.isnan(x.porcentaje_de_la_total) else format(x.porcentaje_de_la_total,'.0f')+' %'}</td></tr>"
        for x in desc.itertuples())

    dom = desc.set_index("fuente").sd_de_la_media_final
    quien = ("el supuesto declarado" if dom.get("solo del supuesto", 0) >= dom.get("solo muestral", 0)
             else "el tamaño de la población sintética")
    nota_inc = ("La mayor parte del margen viene de <b>" + quien + "</b>. "
                + ("Afinar el supuesto estrecharía el intervalo; simular más agentes no."
                   if quien.startswith("el supuesto")
                   else "Subir el número de agentes estrecharía el intervalo; afinar el supuesto no."))

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(esc.nombre)} — Bogotá Social Simulator</title>
<style>
:root {{ color-scheme: light; --s1:#fcfcfb; --s2:#f4f4f1; --tp:#0b0b0b; --ts:#52514e;
  --tm:#7a7975; --bd:#e2e1dc; --az:{AZUL_L}; --na:{NARANJA_L}; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ color-scheme: dark;
  --s1:#1a1a19; --s2:#232321; --tp:#ffffff; --ts:#c3c2b7; --tm:#8f8e86; --bd:#35342f;
  --az:{AZUL_D}; --na:{NARANJA_D}; }} }}
:root[data-theme="dark"] {{ color-scheme: dark; --s1:#1a1a19; --s2:#232321; --tp:#fff;
  --ts:#c3c2b7; --tm:#8f8e86; --bd:#35342f; --az:{AZUL_D}; --na:{NARANJA_D}; }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--s1); color:var(--tp); font:16px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:56px 16px 96px }}
h1 {{ font-size:32px; line-height:1.2; margin:0 0 6px; font-weight:600 }}
h2 {{ font-size:20px; margin:44px 0 10px; font-weight:600 }}
p.sub {{ color:var(--ts); margin:0 0 4px }}
p.meta {{ color:var(--tm); font-size:14px; margin:0 }}
.aviso {{ background:var(--s2); border:1px solid var(--bd); border-left:3px solid var(--na);
  border-radius:10px; padding:14px 18px; margin:26px 0; color:var(--ts); font-size:15px }}
.hero {{ display:flex; flex-wrap:wrap; gap:14px; margin:26px 0 8px }}
.tile {{ flex:1 1 200px; background:var(--s2); border:1px solid var(--bd); border-radius:12px; padding:18px 20px }}
.tile .n {{ font-size:34px; font-weight:600; line-height:1.1; font-variant-numeric:tabular-nums }}
.tile .l {{ color:var(--ts); font-size:14px; margin-top:4px }}
table {{ width:100%; border-collapse:collapse; margin:10px 0 4px; font-size:15px }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--bd) }}
th {{ color:var(--ts); font-weight:600; font-size:13px; text-transform:uppercase; letter-spacing:.04em }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums }}
.pm {{ color:var(--tm) }}
.gr {{ width:100%; height:auto; display:block; margin:8px 0 4px }}
.rejilla {{ stroke:var(--bd); stroke-width:1 }}
.eje {{ fill:var(--tm); font-size:12px }}
.banda-90 {{ fill:var(--az); opacity:.14 }}
.banda-50 {{ fill:var(--az); opacity:.22 }}
.banda-nulo {{ fill:var(--tm); opacity:.10 }}
.linea {{ fill:none; stroke:var(--az); stroke-width:2; stroke-linejoin:round }}
.linea-nulo {{ fill:none; stroke:var(--tm); stroke-width:2; stroke-dasharray:5 4 }}
.areadist {{ fill:var(--az); opacity:.18 }}
.barra {{ fill:var(--az) }}
.barra-ini {{ fill:var(--tm); opacity:.55 }}
.pt {{ fill:var(--az); stroke:var(--s1); stroke-width:2 }}
.dir {{ font-size:13px; font-weight:600 }}
.dir.azul {{ fill:var(--az) }} .dir.gris {{ fill:var(--tm) }}
#tt {{ position:fixed; pointer-events:none; opacity:0; transition:opacity .12s;
  background:var(--s1); border:1px solid var(--bd); border-radius:8px; padding:8px 11px;
  font-size:13px; box-shadow:0 6px 24px rgba(0,0,0,.14); z-index:9 }}
footer {{ margin-top:52px; padding-top:20px; border-top:1px solid var(--bd); color:var(--tm); font-size:14px }}
footer ul {{ padding-left:18px }} footer li {{ margin:6px 0 }}
</style></head><body>
<main>
<h1>{_esc(esc.nombre)}</h1>
<p class="sub">{_esc(esc.descripcion)}</p>
<p class="meta">{_esc(esc.etiqueta_variable)} · {len(esc.poblacion):,} agentes ·
{r.medias.shape[0]} corridas · semilla {esc.semilla} · {date.today().isoformat()}</p>

<div class="aviso"><b>Esto no es una predicción.</b> El nivel y la dispersión de cada
periodo son <b>supuestos declarados</b>, no resultados del modelo. Lo que el simulador
calcula es la distribución completa que esos supuestos implican, con su incertidumbre.</div>

<div class="hero">
  <div class="tile"><div class="n">{final.escenario:.2f}</div>
    <div class="l">media al final del escenario<br>(partía de {esc.media_inicial:.2f})</div></div>
  <div class="tile"><div class="n">{final.diferencia:+.2f}</div>
    <div class="l">diferencia contra no hacer nada<br>{final.veces_el_error:.1f}× el error de la comparación</div></div>
  <div class="tile"><div class="n">{resumen.p05.iloc[-1]:.2f}–{resumen.p95.iloc[-1]:.2f}</div>
    <div class="l">intervalo del 90 % de las corridas<br>al final del escenario</div></div>
</div>

<h2>Los supuestos declarados</h2>
<table><thead><tr><th>Periodo</th><th>Nivel</th><th>Dispersión</th></tr></thead>
<tbody>{supuestos}</tbody></table>

<h2>Trayectoria</h2>
{_grafico_trayectoria(r, rn, esc.etiqueta_variable)}
<table><thead><tr><th>Periodo</th><th>Media</th><th>Intervalo 90 %</th><th>Dispersión</th></tr></thead>
<tbody>{fil_res}</tbody></table>

<h2>Contra el escenario sin cambios</h2>
<p class="sub">La pregunta útil nunca es cuánto da, sino cuánto más que no hacer nada.</p>
<table><thead><tr><th>Periodo</th><th>Escenario</th><th>Sin cambios</th><th>Diferencia</th><th>Veces el error</th></tr></thead>
<tbody>{fil_cmp}</tbody></table>

<h2>Distribución al final</h2>
{_grafico_distribucion(r, distribucion_de(esc.poblacion, esc.grilla))}

<h2>De dónde viene la incertidumbre</h2>
<p class="sub">{nota_inc}</p>
<table><thead><tr><th>Fuente</th><th>Desviación de la media final</th><th>% del total</th></tr></thead>
<tbody>{fil_inc}</tbody></table>

<footer>
<b>Qué hay detrás de estas cifras, y qué no.</b>
<ul>
<li>Siete experimentos pre-registrados establecieron que <b>no hay mecanismo de dinámica
de opinión identificable</b> con los datos públicos disponibles. Por eso el escenario
declara el nivel y la dispersión en vez de generarlos.</li>
<li>La estructura de red <b>no aporta</b> nada medible al ajuste y no interviene aquí.</li>
<li>El forzamiento es el <b>ladeo categórico</b>: la distribución se mueve sobre el
soporte real de la variable, sin salirse a valores que la escala no puede tomar.</li>
<li>La incertidumbre mostrada cubre el error muestral de la población sintética y la
incertidumbre declarada de los supuestos. <b>No</b> cubre el error de que el supuesto
esté equivocado.</li>
{"<li><b>" + str(r.corridas_proyectadas) + " corridas</b> pidieron combinaciones fuera de lo que la escala admite y se proyectaron al borde: las colas del intervalo están comprimidas.</li>" if r.corridas_proyectadas else ""}
</ul>
</footer>
</main>
<div id="tt"></div>
<script>
const tt=document.getElementById('tt');
document.querySelectorAll('.pt,.barra').forEach(el=>{{
  el.addEventListener('pointerenter',e=>{{
    const d=el.dataset;
    tt.innerHTML = d.v!==undefined && d.lo!==undefined
      ? `<b>${{d.t}}</b><br>media ${{d.v}}<br>90 %: ${{d.lo}} – ${{d.hi}}<br>sin cambios: ${{d.n}}`
      : `<b>${{d.t}}</b> · ${{d.s}}<br>${{(d.v*100).toFixed(1)}} %`;
    tt.style.opacity=1;
  }});
  el.addEventListener('pointermove',e=>{{
    tt.style.left=Math.min(e.clientX+14, innerWidth-220)+'px';
    tt.style.top=(e.clientY-10)+'px';
  }});
  el.addEventListener('pointerleave',()=>tt.style.opacity=0);
}});
</script>
</body></html>"""


def escribir(esc: Escenario, destino: str | Path, corridas: int | None = None) -> Path:
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(construir(esc, corridas=corridas), encoding="utf-8")
    return destino
