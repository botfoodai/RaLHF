# Playwright Extraction Path

MANDATORY: follow exactly. Don't modify script. Don't chain with `&&`.
Each step = separate Bash call. Failure → report and stop.

## Step 1 — Install (separate Bash)

```bash
mkdir -p /tmp/ralhf-pw && cd /tmp/ralhf-pw && test -d node_modules/playwright && echo "pw:ready" || (npm init -y >/dev/null 2>&1 && npm install playwright >/dev/null 2>&1 && echo "pw:ready")
```

## Step 2 — Write script (separate Bash, only change TARGET_URL)

```bash
cat > /tmp/ralhf-pw/extract.js << 'SCRIPT'
const{chromium}=require('playwright');const fs=require('fs');(async()=>{const pd='/tmp/ralhf-pw/browser-profile';fs.mkdirSync(pd,{recursive:true});const ctx=await chromium.launchPersistentContext(pd,{headless:false,channel:'chrome',args:['--disable-blink-features=AutomationControlled'],ignoreDefaultArgs:['--enable-automation']});const pg=ctx.pages()[0]||await ctx.newPage();await pg.goto('TARGET_URL',{waitUntil:'domcontentloaded',timeout:60000});const url=pg.url();const hasPw=await pg.locator('input[type="password"]').count();if(hasPw>0||/\/(login|signin|auth)/i.test(url)){console.log('AUTH_REQUIRED');await pg.waitForFunction(()=>{const pw=document.querySelectorAll('input[type="password"]').length>0;const otp=document.querySelectorAll('input[autocomplete="one-time-code"],input[name*="otp"],input[name*="totp"]').length>0;const lp=/\/(login|signin|sign_in|auth|oauth|authorize|two.?factor|2fa|mfa|verify|challenge|otp|sso)/i.test(window.location.pathname);const od=/accounts\.google|appleid\.apple|login\.microsoftonline|facebook\.com\/login/i.test(window.location.hostname);return!pw&&!otp&&!lp&&!od},null,{timeout:300000});console.log('AUTH_COMPLETE')}await pg.evaluate(()=>{const sels=['[data-testid*="cookie"] button','[data-testid*="consent"] button','[id*="cookie"] button','[id*="consent"] button','[class*="cookie"] button','[class*="consent"] button','button[id*="accept"]','button[class*="accept"]','[aria-label*="cookie"] button','[aria-label*="consent"] button','[aria-label*="Accept"]','[aria-label*="Agree"]'];for(const s of sels){const b=document.querySelector(s);if(b&&b.offsetParent!==null){b.click();break}}});await pg.waitForTimeout(1000);let ph=0;for(let i=0;i<3;i++){const ch=await pg.evaluate(()=>document.body.scrollHeight);if(ch===ph)break;ph=ch;await pg.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await pg.waitForTimeout(800)}await pg.evaluate(()=>window.scrollTo(0,0));await pg.waitForTimeout(1000);const html=await pg.content();fs.writeFileSync('/tmp/ralhf-pw/page.html',html);console.log('SAVED:'+html.length+' chars');await ctx.close()})();
SCRIPT
echo "script:written"
```

## Step 3 — Run (separate Bash, 360000ms timeout)

```bash
cd /tmp/ralhf-pw && node extract.js
```

`AUTH_REQUIRED` → tell user: "A browser window has opened — please log in
to continue." Say nothing else until done.

## Step 4 — Read HTML (separate Bash)

```bash
head -c 80000 /tmp/ralhf-pw/page.html
```

Process same as curl output.

## Step 5 — Discovery (after reading HTML)

1. **Network capture**: add `page.route('**/*', ...)` interception before
   `page.goto()` (see `strategy-discovery.md` §6).
2. **Embedded JSON**: `page.evaluate` with embedded JSON discovery JS.
3. **Export detection**: `page.evaluate` with export detection JS.
4. **Strategy decision**: same logic as Chrome step 5.

## Rules

Never re-launch browser. Never modify script (only URL). Never chain steps.
Timeout → tell user, stop. Always process received HTML.
