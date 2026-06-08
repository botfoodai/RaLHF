# Strategy Discovery

JavaScript snippets and decision logic for selecting the optimal extraction
strategy. Referenced by SKILL.md Phase 1 steps 1–4.

## 1. Network / API Discovery

Captures JSON API calls made during page load. Two variants depending on
the JavaScript execution world available.

### MAIN world variant (preferred)

When `javascript_tool` executes in the page's MAIN world (same origin,
access to `window.fetch` and `XMLHttpRequest`), inject this interceptor
**before navigation if possible** or immediately after, then reload:

```javascript
(() => {
  const captured = [];
  const maxCapture = 50;
  const minBodySize = 100;

  // Patch fetch
  const origFetch = window.fetch;
  window.fetch = async function (...args) {
    const resp = await origFetch.apply(this, args);
    try {
      const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
      const clone = resp.clone();
      const ct = clone.headers.get('content-type') || '';
      if (ct.includes('json') && captured.length < maxCapture) {
        const body = await clone.text();
        if (body.length >= minBodySize) {
          captured.push({
            type: 'fetch',
            url: url.substring(0, 500),
            method: (args[1]?.method || 'GET').toUpperCase(),
            status: resp.status,
            bodyPreview: body.substring(0, 2000),
            bodySize: body.length
          });
        }
      }
    } catch (_) {}
    return resp;
  };

  // Patch XHR
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this._ralhf = { method: method.toUpperCase(), url: String(url).substring(0, 500) };
    return origOpen.apply(this, [method, url, ...rest]);
  };
  XMLHttpRequest.prototype.send = function (...args) {
    this.addEventListener('load', function () {
      try {
        const ct = this.getResponseHeader('content-type') || '';
        if (ct.includes('json') && captured.length < maxCapture) {
          const body = this.responseText || '';
          if (body.length >= minBodySize) {
            captured.push({
              type: 'xhr',
              url: this._ralhf?.url || '',
              method: this._ralhf?.method || 'GET',
              status: this.status,
              bodyPreview: body.substring(0, 2000),
              bodySize: body.length
            });
          }
        }
      } catch (_) {}
    });
    return origSend.apply(this, args);
  };

  // Expose retrieval function
  window.__ralhfCaptured = () => JSON.stringify(captured);
})();
```

After ~8 seconds of page load, retrieve results:

```javascript
window.__ralhfCaptured ? window.__ralhfCaptured() : '[]'
```

### DOM-only fallback (ISOLATED world)

When `javascript_tool` runs in an ISOLATED world (Chrome extensions default),
it cannot monkey-patch `fetch`/`XHR`. Instead, inspect the DOM for API
indicators:

```javascript
(() => {
  const indicators = [];

  // Check for data attributes containing API URLs
  document.querySelectorAll('[data-api-url], [data-endpoint], [data-api]').forEach(el => {
    for (const attr of el.attributes) {
      if (/^data-(api|endpoint)/.test(attr.name) && attr.value) {
        indicators.push({ type: 'data-attr', attr: attr.name, value: attr.value.substring(0, 500) });
      }
    }
  });

  // Check inline scripts for fetch/XHR calls
  document.querySelectorAll('script:not([src])').forEach(script => {
    const text = script.textContent || '';
    // Look for fetch() calls with URL patterns
    const fetchMatches = text.match(/fetch\s*\(\s*['"`]([^'"`\s]{10,})['"]/g);
    if (fetchMatches) {
      fetchMatches.slice(0, 5).forEach(m => {
        const url = m.match(/['"`]([^'"`]+)['"]/)?.[1];
        if (url) indicators.push({ type: 'inline-fetch', url: url.substring(0, 500) });
      });
    }
    // Look for GraphQL endpoints
    if (/graphql|\/gql\b/i.test(text)) {
      indicators.push({ type: 'graphql-hint', source: 'inline-script' });
    }
  });

  // Check meta tags and link tags for API hints
  document.querySelectorAll('meta[name*="api"], link[rel="preconnect"]').forEach(el => {
    const value = el.content || el.href || '';
    if (value && /api\.|\/api\/|\/v\d\//i.test(value)) {
      indicators.push({ type: 'meta-api', tag: el.tagName.toLowerCase(), value: value.substring(0, 500) });
    }
  });

  return JSON.stringify(indicators);
})();
```

This is less reliable than MAIN world interception — it detects evidence
of API usage but cannot capture actual responses. Use it as a signal to
escalate to Playwright (which supports true interception) or to guide
manual API endpoint testing.

## 2. Embedded JSON Discovery

Scans the DOM for server-rendered data blobs. Works in any JS world (reads
DOM only — no patching required).

```javascript
(() => {
  const found = [];

  // Check common SSR data containers
  const checks = [
    { key: '__NEXT_DATA__', selector: 'script#__NEXT_DATA__', global: '__NEXT_DATA__' },
    { key: '__NUXT__', selector: null, global: '__NUXT__' },
    { key: '__INITIAL_STATE__', selector: null, global: '__INITIAL_STATE__' },
    { key: '__REDUX_STATE__', selector: null, global: '__REDUX_STATE__' },
    { key: '__APOLLO_STATE__', selector: null, global: '__APOLLO_STATE__' },
  ];

  for (const check of checks) {
    // Try DOM selector first
    if (check.selector) {
      const el = document.querySelector(check.selector);
      if (el && el.textContent.trim().length > 10) {
        found.push({
          key: check.key,
          source: 'script-tag',
          selector: check.selector,
          preview: el.textContent.trim().substring(0, 2000),
          size: el.textContent.length
        });
        continue;
      }
    }
    // Try window global
    try {
      if (check.global && typeof window[check.global] !== 'undefined') {
        const json = JSON.stringify(window[check.global]);
        found.push({
          key: check.key,
          source: 'window-global',
          preview: json.substring(0, 2000),
          size: json.length
        });
      }
    } catch (_) {}
  }

  // Check for data-injector-instances (Airbnb pattern)
  document.querySelectorAll('[data-injector-instances]').forEach(el => {
    const raw = el.getAttribute('data-injector-instances');
    if (raw && raw.length > 10) {
      found.push({
        key: 'data-injector-instances',
        source: 'data-attr',
        selector: el.tagName.toLowerCase() + '[data-injector-instances]',
        preview: raw.substring(0, 2000),
        size: raw.length
      });
    }
  });

  // Check for ld+json structured data
  document.querySelectorAll('script[type="application/ld+json"]').forEach((el, i) => {
    const text = el.textContent.trim();
    if (text.length > 10) {
      found.push({
        key: 'ld+json',
        source: 'script-tag',
        selector: `script[type="application/ld+json"]:nth-of-type(${i + 1})`,
        preview: text.substring(0, 2000),
        size: text.length
      });
    }
  });

  // Check for any large script tags with JSON-like content
  document.querySelectorAll('script[type="application/json"], script[data-state]').forEach(el => {
    const text = el.textContent.trim();
    if (text.length > 100 && (text.startsWith('{') || text.startsWith('['))) {
      const id = el.id ? `script#${el.id}` : (el.dataset.state ? `script[data-state="${el.dataset.state}"]` : null);
      if (id) {
        found.push({
          key: id,
          source: 'script-tag',
          selector: id,
          preview: text.substring(0, 2000),
          size: text.length
        });
      }
    }
  });

  return JSON.stringify(found);
})();
```

### CLI variant (curl)

Embedded JSON can be checked from raw HTML without JS execution:

```bash
# Extract __NEXT_DATA__ from raw HTML
grep -oP '<script id="__NEXT_DATA__"[^>]*>\K[^<]+' /tmp/ralhf-page.html | head -c 5000

# Check for ld+json
grep -oP '<script type="application/ld\+json">\K[^<]+' /tmp/ralhf-page.html | head -c 5000

# Check for data-injector-instances
grep -oP 'data-injector-instances="[^"]*"' /tmp/ralhf-page.html | head -c 2000

# Check for common SSR globals assigned in inline scripts
grep -oP 'window\.__\w+__\s*=' /tmp/ralhf-page.html
```

## 3. Export Feature Detection

Finds download/export buttons on the page. Works in any JS world.

```javascript
(() => {
  const exports = [];

  // Links with download attribute
  document.querySelectorAll('a[download]').forEach(el => {
    exports.push({
      type: 'download-link',
      text: el.textContent.trim().substring(0, 100),
      href: el.href?.substring(0, 500) || '',
      selector: buildSelector(el)
    });
  });

  // Buttons/links with export-related text or classes
  const exportPatterns = /\b(export|download|csv|xlsx|pdf)\b/i;
  document.querySelectorAll('button, a, [role="button"]').forEach(el => {
    const text = el.textContent.trim();
    const cls = el.className || '';
    const aria = el.getAttribute('aria-label') || '';
    if (exportPatterns.test(text) || exportPatterns.test(cls) || exportPatterns.test(aria)) {
      // Skip if already captured as download link
      if (el.hasAttribute('download')) return;
      exports.push({
        type: 'export-button',
        text: text.substring(0, 100),
        ariaLabel: aria.substring(0, 100),
        selector: buildSelector(el)
      });
    }
  });

  function buildSelector(el) {
    if (el.id) return '#' + el.id;
    const testid = el.getAttribute('data-testid');
    if (testid) return `[data-testid="${testid}"]`;
    const aria = el.getAttribute('aria-label');
    if (aria) return `${el.tagName.toLowerCase()}[aria-label="${aria}"]`;
    const tag = el.tagName.toLowerCase();
    const text = el.textContent.trim().substring(0, 30);
    return `${tag}:has-text("${text}")`;
  }

  return JSON.stringify(exports);
})();
```

## 4. Strategy Decision Matrix

After running discovery steps 1–3, evaluate results in **rank order**.
Select the highest-ranked strategy whose discovery produced a viable signal.

| Rank | Strategy | Key | Discovery signal required | When to select |
|---|---|---|---|---|
| 1 | Pure API | `api_direct` | Network capture contains a JSON endpoint that returns the target data directly (or DOM-only fallback found GraphQL/REST indicators) | The API response contains the same fields the user wants, with structured JSON. No DOM parsing needed. |
| 2 | Hybrid API | `api_intercept` | Network capture contains JSON endpoints triggered by user interaction (scroll, click, page navigation) | Data loads via API on interaction. Need page context to trigger the call but parse the API response. |
| 3 | Embedded JSON | `embedded_json` | Embedded JSON discovery found a blob containing the target data | SSR data in script tags has the fields. Extraction = parse JSON, no selectors needed. |
| 4 | Export/Download | `export_download` | Export detection found a download link or export button | Site provides its own export. More reliable than scraping, especially for large datasets. |
| 5 | DOM Scraping | `dom_css` / `dom_xpath` | None of the above, but stripped DOM has identifiable structure | Last resort. Author CSS/XPath selectors against the DOM. |

### Decision rules

1. **Try strategies in rank order.** Select the highest-ranked that yields the data.
2. A strategy is "viable" if its discovery step returned at least one result AND
   the discovered data source contains (or can be made to contain) the fields
   the user wants.
3. If network discovery found API calls but none contain the target data, skip
   to rank 3 (embedded JSON).
4. If multiple strategies are viable, prefer the higher-ranked one.
5. If no discovery step yielded results, default to `dom_css`.
6. Document the discovery findings (which APIs were found, which blobs exist)
   in the view file's Notes section for future reference.

### Quick-check table

| Discovery result | Likely strategy |
|---|---|
| GraphQL endpoint returning full data | `api_direct` |
| REST endpoint with pagination params | `api_direct` |
| API calls triggered only by scroll/click | `api_intercept` |
| `__NEXT_DATA__` with target data in `props` | `embedded_json` |
| `ld+json` with full structured data | `embedded_json` |
| "Download all" / "Export CSV" button | `export_download` |
| No API, no JSON blobs, DOM has clear structure | `dom_css` |
| SPA with no pre-rendered data, API behind auth | `api_intercept` (with auth) |

## 5. CLI Limitations

`curl` fetches raw HTML with no JavaScript execution. This limits discovery:

| Discovery step | CLI support | Notes |
|---|---|---|
| Network/API discovery | No | Requires JS execution to intercept fetch/XHR |
| Embedded JSON discovery | Partial | Can grep for `__NEXT_DATA__`, `ld+json`, and `data-injector-instances` in raw HTML. Cannot access `window.*` globals. |
| Export feature detection | No | Requires JS to find interactive export buttons; `a[download]` can be found in raw HTML but cannot be triggered |
| DOM stripping | Partial | Can process raw HTML but misses JS-rendered content |

**Escalation**: For SPA sites or when API/export strategies are suspected,
escalate to Playwright or Chrome. Note this to the user only if they
explicitly asked about CLI support.

## 6. Playwright Adaptations

Playwright supports all discovery strategies with slight API differences.

### Network capture (equivalent to MAIN world interception)

```javascript
// In the Playwright extraction script, before page.goto():
const captured = [];
await page.route('**/*', async (route) => {
  const resp = await route.fetch();
  const ct = resp.headers()['content-type'] || '';
  if (ct.includes('json')) {
    try {
      const body = await resp.text();
      if (body.length >= 100) {
        captured.push({
          url: route.request().url().substring(0, 500),
          method: route.request().method(),
          status: resp.status(),
          bodyPreview: body.substring(0, 2000),
          bodySize: body.length
        });
      }
    } catch (_) {}
  }
  await route.fulfill({ response: resp });
});

await page.goto(url, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(8000);
// captured[] now has all JSON API calls
```

### Embedded JSON

```javascript
const blobs = await page.evaluate(() => {
  // Same embedded JSON discovery script from section 2
  // (it reads DOM only, works identically in Playwright's evaluate)
});
```

### Export feature detection

```javascript
const exports = await page.evaluate(() => {
  // Same export detection script from section 3
});
```

### Download interception

```javascript
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.click('a[download], button:has-text("Export")')
]);
const path = await download.path();
const content = fs.readFileSync(path, 'utf-8');
```
