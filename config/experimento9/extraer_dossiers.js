// ---------------------------------------------------------------------------
// Experimento 9 — extracción y selección de los doce dossiers del brazo B.
//
// Script exacto que produjo config/experimento9/dossiers/*.md el 29/09/2026
// (EXPERIMENT_9_SPECIFICATION.md, enmiendas 1, 2 y 3).
//
// Cómo correrlo: abrir cualquier página de es.wikipedia.org, abrir la consola
// del navegador (F12), pegar este archivo completo y presionar Enter. Al final
// imprime la huella SHA-256 (16 primeros caracteres) de cada dossier; deben
// coincidir con los de config/experimento9/dossiers/HUELLAS.txt. Los dossiers
// quedan en window.__md; copy(window.__md['EPC_2014_2015']) copia uno.
//
// Las revisiones están fijadas (REV): el resultado no cambia aunque Wikipedia
// se edite después.
//
// Se escribió en JavaScript porque se ejecutó en el navegador: desde el
// entorno de trabajo de Claude no se puede consultar Wikipedia directamente.
// ---------------------------------------------------------------------------

(async () => {
  const REV = {2013:170534794, 2014:169716920, 2015:166055370, 2016:174778579,
               2017:172005323, 2018:170159379, 2019:174829937, 2020:174701655,
               2021:174207339, 2022:174511108, 2023:170920493, 2024:172591607,
               2025:173797898};

  // Enmienda 2, punto 4: filtro de opinión (sin mayúsculas ni tildes).
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const OPINION = /encuesta|sondeo|aprobacion|favorabilidad|confianza|percepcion/;
  // Enmienda 2, punto 5: qué entrada cuenta como de Bogotá.
  const BOGOTA = /bogot|distrito capital|transmilenio/;

  // Fecha al inicio de la entrada: "5 de abril:", "3 al 6 de septiembre:",
  // "18 de abril al 2 de mayo:", "30 y 31 de octubre:", "9- 15 de septiembre:".
  const MES = 'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre';
  const FECHA = new RegExp(`^((?:\\d{1,2}(?:\\s*(?:y|al|-|–)\\s*\\d{1,2})?(?: de (?:${MES}))?\\s*(?:al|-|–)\\s*)?\\d{1,2}(?:\\s*(?:y|al|-|–)\\s*\\d{1,2})? de (?:${MES}))\\s*:\\s*`, 'i');
  const limpiar = s => s.replace(/[​­]/g, '').replace(/\s+/g, ' ').trim();

  // Enmienda 2, punto 3: solo la sección "Acontecimientos". Cada <li> con texto
  // propio es una entrada; una línea que es solo una fecha agrupa sub-entradas,
  // que heredan esa fecha. Sin fecha propia ni heredada, se usa el mes (H3).
  async function extraer(y) {
    const r = await fetch(`https://es.wikipedia.org/w/api.php?action=parse&oldid=${REV[y]}&prop=text&format=json&formatversion=2&origin=*`).then(r => r.json());
    const d = new DOMParser().parseFromString(r.parse.text, 'text/html');
    d.querySelectorAll('sup, .mw-editsection, style').forEach(e => e.remove());
    const out = []; let inAc = false, mes = null, fechaPadre = null;
    for (const el of d.querySelectorAll('.mw-parser-output > *')) {
      const h = el.matches('.mw-heading') ? el.querySelector('h2,h3,h4') : (el.matches('h2,h3,h4') ? el : null);
      if (h) {
        if (h.tagName === 'H2') { inAc = h.textContent.trim() === 'Acontecimientos'; mes = null; }
        else if (inAc && h.tagName === 'H3') mes = h.textContent.trim().toLowerCase();
        continue;
      }
      if (!inAc) continue;
      el.querySelectorAll('li').forEach(li => {
        const c = li.cloneNode(true); c.querySelectorAll('ul,ol').forEach(u => u.remove());
        let t = limpiar(c.textContent); if (!t) return;
        const anidado = !!li.parentElement.closest('li'); let f = null; const m = t.match(FECHA);
        if (m) { f = m[1]; t = t.slice(m[0].length).trim(); }
        if (!anidado) fechaPadre = f;
        if (!t) return;
        out.push({anio: y, fecha: (f || (anidado ? fechaPadre : null) || mes) + ' de ' + y, texto: t});
      });
    }
    return out;
  }

  // Enmienda 2, punto 5: k posiciones espaciadas parejo entre n, redondeo hacia arriba en .5.
  const pos = (n, k) => k === 1 ? [Math.floor((n - 1) / 2 + 0.5)]
                                : [...Array(k).keys()].map(i => Math.floor(i * (n - 1) / (k - 1) + 0.5));

  const T = [['ECP',2013,2017],['ECP',2017,2019],['ECP',2019,2021],['ECP',2021,2023],
             ['EPC',2014,2015],['EPC',2015,2017],['EPC',2017,2018],['EPC',2018,2019],
             ['EPC',2019,2022],['EPC',2022,2023],['EPC',2023,2024],['EPC',2024,2025]];

  const cache = {}; for (const y in REV) cache[y] = await extraer(+y);
  window.__md = {};
  for (const [s, a, b] of T) {
    let all = []; for (let y = a; y <= b; y++) all = all.concat(cache[y]);   // enmienda 2, punto 2
    all = all.map((e, i) => ({...e, orden: i}));
    const eleg = all.filter(e => !OPINION.test(norm(e.texto)));
    const esB = e => BOGOTA.test(norm(e.texto));
    const bog = eleg.filter(esB), otr = eleg.filter(e => !esB(e));
    const sel = (bog.length >= 15 ? pos(bog.length, 15).map(i => bog[i])
                                  : bog.concat(pos(otr.length, 15 - bog.length).map(i => otr[i])))
                .sort((x, y) => x.orden - y.orden);
    const nb = sel.filter(esB).length;
    const fuentes = []; for (let y = a; y <= b; y++) fuentes.push(`«Anexo:Colombia en ${y}» (revisión ${REV[y]})`);
    window.__md[`${s}_${a}_${b}`] = `# Dossier ${s} ${a}→${b}

- **Serie:** ${s} · **años cubiertos:** ${a} a ${b}, inclusive
- **Fuente:** Wikipedia en español, ${fuentes.join(', ')}. Consultado el 29/09/2026. Licencia CC BY-SA 4.0.
- **Nota (enmienda 1):** Wikipedia en español no tiene cronología anual de Bogotá; los hechos de Bogotá salen de la cronología de Colombia.
- **Selección (enmiendas 2 y 3):** ${all.length} entradas; ${all.length - eleg.length} excluidas por el filtro de opinión; ${bog.length} de Bogotá. Seleccionados: 15 (${nb} de Bogotá${nb < 15 ? `, ${15 - nb} nacionales de relleno` : ''}).

## Hechos

${sel.map((e, i) => `${i + 1}. **${e.fecha}.** ${e.texto}`).join('\n')}
`;
  }

  const huella = async s => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))]
                              .map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
  for (const [k, v] of Object.entries(window.__md)) console.log(k, await huella(v));
})();
