# DOM Stripping

> **Scope**: Applies to `dom_css` and `dom_xpath` strategies. For
> API/JSON/export strategies, DOM stripping still runs in Phase 1 for
> context (layout analysis, context fingerprint generation) but is not the
> primary extraction mechanism.

Reduces a full HTML page to a minimal DOM representation that fits within
~4,000 tokens. Used during cold extraction (Phase 2) to give the recipe-
authoring model a clean view of the page structure.

## Stripping Rules

Run this JavaScript via `javascript_tool`. It operates on `document.body`
and returns a serialized HTML string.

```javascript
(() => {
  const clone = document.body.cloneNode(true);

  // 1. Bulk remove non-content tags + structural chrome (one query, prunes large subtrees early).
  clone.querySelectorAll(
    'script,style,noscript,svg,iframe,video,audio,canvas,map,object,embed,' +
    'link,meta,template,nav,header,footer,aside'
  ).forEach(el => el.remove());

  // 2. Remove hidden elements by attribute.
  clone.querySelectorAll('[aria-hidden="true"], [hidden]').forEach(el => el.remove());

  // 3. Single-pass: hidden class check, consent check, data-* strip, style strip, class cleanup.
  //    Replaces 4+ separate querySelectorAll('*') passes with one loop.
  const hiddenRe = /\bhidden\b|\bd-none\b|\bsr-only\b|\bvisually-hidden\b|\binvisible\b|\bdisplay-none\b|\bhide\b|\bis-hidden\b|\bu-hidden\b/;
  const consentRe = /cookie|consent|gdpr|privacy|onetrust|cookiebot|cc-banner|cookie-banner|consent-banner/i;
  const keepData = new Set([
    'data-testid', 'data-src', 'data-srcset', 'data-lazy-src', 'data-original', 'data-bg'
  ]);
  const toRemove = [];
  const allElements = clone.querySelectorAll('*');

  for (let i = 0; i < allElements.length; i++) {
    const el = allElements[i];
    const cn = el.className;

    // Hidden class or consent class/id → mark for batch removal, skip rest.
    if (typeof cn === 'string' && cn) {
      if (hiddenRe.test(cn)) { toRemove.push(el); continue; }
      if (consentRe.test(cn + (el.id || ''))) { toRemove.push(el); continue; }
    } else if (el.id && consentRe.test(el.id)) {
      toRemove.push(el); continue;
    }

    // Strip data-* and style attributes (reverse iteration, no array spread).
    for (let j = el.attributes.length - 1; j >= 0; j--) {
      const attr = el.attributes[j];
      if (attr.name === 'style') el.removeAttribute('style');
      else if (attr.name.startsWith('data-') && !keepData.has(attr.name)) {
        el.removeAttribute(attr.name);
      }
    }

    // Clean hash-based classes.
    if (typeof cn === 'string' && cn) {
      const classes = cn.split(/\s+/).filter(c =>
        c.length > 0 && c.length < 30 && !/[A-Z_]{3,}|[0-9a-f]{5,}/.test(c)
      );
      if (classes.length > 0) el.className = classes.join(' ');
      else el.removeAttribute('class');
    }
  }
  toRemove.forEach(el => el.remove());

  // 4. Collapse empty containers — single bottom-up pass (replaces while loop).
  const containers = clone.querySelectorAll('div, span, section');
  for (let i = containers.length - 1; i >= 0; i--) {
    const el = containers[i];
    if (el.parentNode && el.children.length === 0 && el.textContent.trim() === '') {
      el.remove();
    }
  }

  // 5. Find main content area.
  const mainContent = clone.querySelector('main, article, [role="main"]');
  const target = mainContent || clone;

  // 6. Find densest repeated-structure container and trim to first 3 items.
  let bestEl = null;
  let bestScore = 0;
  let bestTag = '';
  target.querySelectorAll('*').forEach(el => {
    const children = [...el.children];
    if (children.length < 4) return;
    const tagCounts = {};
    children.forEach(c => { tagCounts[c.tagName] = (tagCounts[c.tagName] || 0) + 1; });
    const [tag, score] = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])[0];
    if (score >= 4 && score > bestScore) {
      bestScore = score;
      bestEl = el;
      bestTag = tag;
    }
  });

  // Trim repeated items to first 3 (enough to author selectors).
  if (bestEl) {
    const items = [...bestEl.children].filter(c => c.tagName === bestTag);
    items.slice(3).forEach(el => el.remove());
  }

  const html = target.innerHTML;

  // 7. Rough token estimate: ~4 chars per token. Target ≤4K tokens (~16K chars).
  if (html.length > 16000) {
    const focusHtml = bestEl ? (bestEl.parentElement || bestEl).innerHTML : html;
    return focusHtml.length > 16000
      ? focusHtml.substring(0, 16000) + '\n<!-- TRUNCATED -->'
      : focusHtml;
  }
  return html;
})();
```

## What Gets Kept

| Tag/Attribute | Kept? | Reason |
|---|---|---|
| `<h1>`–`<h6>`, `<p>`, `<li>`, `<td>`, `<th>` | Yes | Semantic content |
| `<a href="...">` | Yes | Links are fields |
| `<img alt="..." src="...">` | Yes | Image references |
| `<time datetime="...">` | Yes | Date fields |
| `data-testid` | Yes | Stable selectors |
| `data-src`, `data-srcset`, `data-lazy-src`, `data-original`, `data-bg` | Yes | Lazy-load image URLs |
| `role`, `aria-label` | Yes | Accessibility selectors |
| `id` | Yes | Anchor selectors |
| `class` (semantic only) | Yes | CSS selectors |
| `<script>`, `<style>`, `<svg>` | No | Noise |
| `data-*` (except testid and lazy-load) | No | Framework noise |
| Cookie/consent overlays | No | Blocks content, not extractable data |
| `style` attribute | No | Layout noise |
| Hash-based classes | No | Unstable selectors |
| Hidden elements | No | Not visible to user |
| `<nav>`, `<header>`, `<footer>`, `<aside>` | No | Chrome/boilerplate, not extractable content |

## Token Budget

Target: ≤ 4,000 tokens (~16,000 characters). The script strips `nav`,
`header`, `footer`, and `aside` elements before searching for main content.
If a repeated-structure container is found (product grid, article feed,
table body), items are trimmed to the first 3 (enough to author selectors).
If the result still exceeds the budget, it truncates from the densest
container. If no repeated structure is found, it falls back to the first
16,000 characters of the main content container.

Always note in feedback if truncation occurred — it may mean the recipe misses
fields in the truncated portion.

## Combined Script (Phase 1 Step 4)

Single `javascript_tool` call that does cookie dismiss + scroll + DOM strip +
hints extraction. Returns `JSON.stringify({ dom, hints })`.

Use this instead of the basic stripping script above during Phase 1 cold path.

**Hints returned**: `listContainer`, `itemCount`, `sampleItems` (first 3),
`contentTypeGuess` (`table`/`listing`/`feed`/`article`/`profile`).

```javascript
(async()=>{const sels=['[data-testid*="cookie"] button','[data-testid*="consent"] button','[id*="cookie"] button','[id*="consent"] button','[class*="cookie"] button','[class*="consent"] button','button[id*="accept"]','button[class*="accept"]','[aria-label*="cookie"] button','[aria-label*="consent"] button','[aria-label*="Accept"]','[aria-label*="Agree"]'];for(const s of sels){const b=document.querySelector(s);if(b&&b.offsetParent!==null){b.click();break;}}await new Promise(r=>setTimeout(r,1000));let p=0;for(let i=0;i<3;i++){window.scrollTo(0,document.body.scrollHeight);await new Promise(r=>setTimeout(r,800));if(document.body.scrollHeight===p)break;p=document.body.scrollHeight;}window.scrollTo(0,0);const c=document.body.cloneNode(true);c.querySelectorAll('script,style,noscript,svg,iframe,video,audio,canvas,map,object,embed,link,meta,template,nav,header,footer,aside').forEach(e=>e.remove());c.querySelectorAll('[aria-hidden="true"],[hidden]').forEach(e=>e.remove());const hRe=/\bhidden\b|\bd-none\b|\bsr-only\b|\bvisually-hidden\b|\binvisible\b|\bdisplay-none\b|\bhide\b|\bis-hidden\b|\bu-hidden\b/;const cRe=/cookie|consent|gdpr|privacy|onetrust|cookiebot|cc-banner|cookie-banner|consent-banner/i;const kd=new Set(['data-testid','data-src','data-srcset','data-lazy-src','data-original','data-bg']);const rm=[];const all=c.querySelectorAll('*');for(let i=0;i<all.length;i++){const e=all[i];const cn=e.className;if(typeof cn==='string'&&cn){if(hRe.test(cn)){rm.push(e);continue}if(cRe.test(cn+(e.id||''))){rm.push(e);continue}}else if(e.id&&cRe.test(e.id)){rm.push(e);continue}for(let j=e.attributes.length-1;j>=0;j--){const a=e.attributes[j];if(a.name==='style')e.removeAttribute('style');else if(a.name.startsWith('data-')&&!kd.has(a.name))e.removeAttribute(a.name)}if(typeof cn==='string'&&cn){const cls=cn.split(/\s+/).filter(x=>x.length>0&&x.length<30&&!/[A-Z_]{3,}|[0-9a-f]{5,}/.test(x));if(cls.length>0)e.className=cls.join(' ');else e.removeAttribute('class')}}rm.forEach(e=>e.remove());const ct=c.querySelectorAll('div,span,section');for(let i=ct.length-1;i>=0;i--){const e=ct[i];if(e.parentNode&&e.children.length===0&&e.textContent.trim()==='')e.remove()}const m=c.querySelector('main,article,[role="main"]')||c;let bestEl=null,bs=0,bestTag='';m.querySelectorAll('*').forEach(e=>{const ch=[...e.children];if(ch.length<4)return;const tc={};ch.forEach(x=>{tc[x.tagName]=(tc[x.tagName]||0)+1});const[tag,sc]=Object.entries(tc).sort((a,b)=>b[1]-a[1])[0];if(sc>=4&&sc>bs){bs=sc;bestEl=e;bestTag=tag}});const hints={};if(bestEl){const id=bestEl.id?'#'+bestEl.id:null;const cls=bestEl.className?'.'+bestEl.className.trim().split(/\s+/).join('.'):null;hints.listContainer=id||(bestEl.tagName.toLowerCase()+(cls||''));hints.itemCount=bs;const items=[...bestEl.children].filter(x=>x.tagName===bestTag);hints.sampleItems=items.slice(0,3).map(el=>{const a=el.querySelector('a');const img=el.querySelector('img');return{title:(el.querySelector('h1,h2,h3,h4,h5,h6,[class*="title"],[class*="name"]')||{}).textContent?.trim()?.substring(0,100)||null,link:a?a.href:null,image:img?(img.src||img.getAttribute('data-src')):null,text:el.textContent?.trim()?.substring(0,200)||null}});items.slice(3).forEach(el=>el.remove());const tag=bestTag.toLowerCase();hints.contentTypeGuess=(tag==='tr'||bestEl.tagName==='TABLE'||bestEl.tagName==='TBODY')?'table':(tag==='article'?'feed':'listing')}else{hints.contentTypeGuess=m.querySelector('form')?'profile':'article'}const h=m.innerHTML;let dom;if(h.length>16000){const f=bestEl?(bestEl.parentElement||bestEl).innerHTML:h;dom=f.length>16000?f.substring(0,16000)+'\n<!-- TRUNCATED -->':f}else{dom=h}return JSON.stringify({dom,hints})})();
```
