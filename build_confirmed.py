"""Builds confirmed/index.html: where the sign-up email link lands, then hands people back into the app.

Separate from build.py on purpose, so it can be rebuilt without touching the other pages:
    python3 build_confirmed.py

Flow (see Latte Learn app, src/context/AuthContext.tsx):
  email link -> Supabase confirms the account -> this page, with the sign-in in the address after the #
  -> after ~2 s the page opens pourscore://auth/confirmed#<same sign-in> -> the app signs in and starts onboarding.
If the app does not open (Expo Go, no app installed, a laptop), after ~4.5 s the page shows an Open button and plain steps.
"""
import hashlib
from pathlib import Path

from parts import header_stores

HERE = Path(__file__).parent
SUPPORT = 'support@pourscoreapp.com'
LEGAL_EMAIL = 'legal@pourscoreapp.com'
CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
WARN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8v5M12 16.5v.5"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3zM3 7l9 7 9-7"/></svg>'


def v(name):
    return f'{name}?v={hashlib.md5((HERE / name).read_bytes()).hexdigest()[:8]}'


CSS = """
/* Page-only styles. The frame (header, footer, tokens) comes from style.css and landing.css. */
body.wide { min-height: 100vh; min-height: 100dvh; display: flex; flex-direction: column; }
body.wide main { flex: 1; display: flex; flex-direction: column; }
.cf { flex: 1; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 32px 22px 7vh; overflow: hidden; }
.cf::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 100%; background: radial-gradient(60% 50% at 50% 42%, rgba(228,87,46,.22), transparent 70%); pointer-events: none; }
.cf section[hidden] { display: none; }
.cf section { position: relative; width: 100%; max-width: 420px; display: flex; flex-direction: column; align-items: center; }
.cf h1 { font-size: clamp(32px, 8vw, 52px); letter-spacing: -.03em; line-height: 1.04; margin: 0 0 12px; text-wrap: balance; }
.cf h1 em { font-style: normal; color: var(--accent); }
.cf p { margin: 0 0 12px; font-size: 17px; line-height: 1.5; color: var(--ink2); }
.cf .kicker { margin: 0 0 12px; }
.cf .hint { font-size: 14px; color: var(--muted); max-width: 340px; }
.ok-tile { position: relative; width: 88px; height: 88px; margin: 0 auto 24px; }
.ok-tile .t { width: 100%; height: 100%; border-radius: 22%; background: var(--milk); display: grid; place-items: center; box-shadow: 0 14px 28px rgba(0,0,0,.45); transform: rotate(-6deg); }
.ok-tile img { width: 74%; filter: invert(1) brightness(.18) sepia(.5); }
.ok-tile .b { position: absolute; right: -9px; bottom: -9px; width: 32px; height: 32px; border-radius: 50%; background: var(--accent); border: 3px solid var(--bg); display: grid; place-items: center; }
.ok-tile .b svg { width: 16px; height: 16px; stroke: var(--bg); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.ring { position: relative; width: 76px; height: 76px; margin: 0 0 22px; display: grid; place-items: center; }
.ring svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; transform: rotate(-90deg); }
.ring circle { fill: none; stroke-width: 4; }
.ring .tr { stroke: rgba(244,236,228,.12); }
.ring .pr { stroke: var(--accent); stroke-linecap: round; stroke-dasharray: 176; stroke-dashoffset: 176; animation: fill 2.2s linear forwards; }
.ring img { position: relative; display: block; width: 38px; height: 38px; margin: 0; padding: 0; border-radius: 50%; }
@keyframes fill { to { stroke-dashoffset: 0; } }
.cf-btn { display: flex; align-items: center; justify-content: center; width: 100%; min-height: 54px; margin: 12px 0 14px; padding: 0 24px; border-radius: 999px; background: var(--accent); color: var(--bg); font: 600 17px/1 'Archivo', sans-serif; text-decoration: none; transition: transform .2s, background .2s; }
.cf-btn:hover { background: #F07A50; transform: translateY(-2px); }
.cf-btn:focus-visible, .cf-help:focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; }
.cf-help { display: flex; align-items: center; gap: 14px; width: 100%; margin-top: 16px; padding: 14px 16px; background: var(--card); border: 1px solid var(--line); border-radius: 18px; text-align: left; text-decoration: none; }
.cf-help .ic { width: 42px; height: 42px; border-radius: 13px; background: rgba(228,87,46,.14); display: grid; place-items: center; flex: none; }
.cf-help .ic svg { width: 22px; height: 22px; stroke: var(--accent); fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.cf-help b { display: block; color: var(--ink); font-size: 15px; }
.cf-help .addr { color: var(--ink); font-weight: 600; font-size: 15px; border-bottom: 1px solid rgba(228,87,46,.55); }
/* Short phones (iPhone SE and similar): tighten spacing so the whole page still fits one screen. */
@media (max-height: 720px) {
  .cf { padding: 14px 20px 14px; }
  .ok-tile { width: 64px; height: 64px; margin-bottom: 16px; }
  .ok-tile .b { width: 26px; height: 26px; right: -7px; bottom: -7px; }
  .cf h1 { font-size: 30px; margin-bottom: 8px; }
  .cf p { font-size: 15.5px; margin-bottom: 8px; }
  .cf-btn { min-height: 50px; margin: 8px 0 10px; }
  .cf .hint { font-size: 13px; }
  .cf-help { margin-top: 10px; padding: 10px 14px; }
  .ring { width: 64px; height: 64px; margin-bottom: 14px; }
  .ring img { width: 32px; height: 32px; }
  footer { padding: 14px 0 18px; font-size: 13px; }
  footer .wrap { gap: 6px; }
}
@media (max-width: 600px) { footer a { display: inline-block; padding: 14px 6px; margin: -14px -6px; } }
@media (prefers-reduced-motion: reduce) { .ring .pr { animation: none; stroke-dashoffset: 0; } .cf-btn { transition: none; } }
"""

SCRIPT = """
(function () {
  var hash = location.hash.slice(1);
  var search = location.search; // read before the address bar is cleared below
  if (hash) history.replaceState(null, '', location.pathname); // keep the sign-in out of the address bar
  var p = new URLSearchParams(hash);
  // Where to hand the sign-in. Real builds answer pourscore://. While testing in Expo Go the app asks for
  // its own exp:// address (only our dev tunnel shape is accepted). Delete this before public launch.
  var scheme = 'pourscore://auth/confirmed';
  var asked = new URLSearchParams(search).get('app') || '';
  if (/^exps?:\/\/[a-z0-9-]+\.exp\.direct\/--\/auth\/confirmed$/i.test(asked)) scheme = asked;
  var link = scheme + (hash ? '#' + hash : '');
  function show(id) {
    ['opening', 'done', 'problem'].forEach(function (s) { document.getElementById(s).hidden = s !== id; });
  }
  document.getElementById('open').href = link;
  if (p.get('error') || p.get('error_description')) return show('problem');
  if (p.get('type') !== 'signup' || !p.get('access_token') || !p.get('refresh_token')) return; // opened directly: keep the button
  show('opening');
  setTimeout(function () { location.href = link; }, 2200);
  setTimeout(function () { show('done'); }, 4500);
})();
"""

page = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Email confirmed | Pour Score</title>
<meta name="description" content="Your email address is confirmed. Open the Pour Score app to carry on.">
<link rel="icon" href="../favicon.png">
<link rel="stylesheet" href="../{v("style.css")}">
<link rel="stylesheet" href="../{v("landing.css")}">
<style>{CSS}</style>
</head>
<body class="wide">
<header><div class="wrap">
<a class="brand" href="../"><img src="../favicon.png" alt="">Pour Score</a>
<nav><a href="../features/">Features</a><a href="../#support">Support</a><a href="../privacy/">Privacy</a><a href="../terms/">Terms</a></nav>
<div class="hstores">{header_stores("../")}</div>
</div></header>
<main>
<div class="cf" aria-live="polite">
<section id="opening" hidden>
<div class="ring"><svg viewBox="0 0 64 64" aria-hidden="true"><circle class="tr" cx="32" cy="32" r="28"/><circle class="pr" cx="32" cy="32" r="28"/></svg><img src="../favicon.png" alt=""></div>
<p class="kicker">Email confirmed</p>
<h1>Opening Pour&nbsp;Score</h1>
<p>One moment, taking you back to the app.</p>
</section>
<section id="done">
<div class="ok-tile"><div class="t"><img src="../patterns/stacked_heart.png" alt=""></div><div class="b">{CHECK}</div></div>
<h1>Your email is <em>confirmed</em></h1>
<p>Open Pour Score to carry on setting up your account.</p>
<a class="cf-btn" id="open" href="pourscore://auth/confirmed">Open Pour Score</a>
<p class="hint">Nothing happened? Open the app yourself and sign in with your email and password.</p>
<a class="cf-help" href="mailto:{SUPPORT}"><span class="ic">{MAIL}</span><span><b>Need a hand?</b><span class="addr">{SUPPORT}</span></span></a>
</section>
<section id="problem" hidden>
<div class="ok-tile"><div class="t"><img src="../patterns/stacked_heart.png" alt=""></div><div class="b">{WARN}</div></div>
<h1>That link has <em>expired</em></h1>
<p>Open the Pour Score app and sign in. We will offer to send you a new confirmation email.</p>
<a class="cf-help" href="mailto:{SUPPORT}"><span class="ic">{MAIL}</span><span><b>Need a hand?</b><span class="addr">{SUPPORT}</span></span></a>
</section>
</div>
</main>
<footer><div class="wrap">
<span>&copy; 2026 Pour Score. Marlon Kazim May, trading as Pour Score.</span>
<span><a href="../features/">Features</a> &middot; <a href="../#support">Support</a> &middot; <a href="../privacy/">Privacy</a> &middot; <a href="../terms/">Terms</a></span>
</div></footer>
<script>{SCRIPT}</script>
</body>
</html>
'''

(HERE / 'confirmed').mkdir(exist_ok=True)
(HERE / 'confirmed' / 'index.html').write_text(page)
print('built confirmed/index.html')
