"""Builds pourscoreapp.com: home (src/home.html + support), /features (src/features.html), /privacy, /terms.

The legal pages come straight from Legal Docs/extracted/*.md, so after a doc
changes, rerun this and push:  python3 build.py
Needs the `markdown` package (pip3 install markdown).
"""
import hashlib
import re
from pathlib import Path

import markdown
from parts import SUBS, header_stores

HERE = Path(__file__).parent
LEGAL = HERE.parent / 'Legal Docs' / 'extracted'
SUPPORT = 'support@pourscoreapp.com'
LEGAL_EMAIL = 'legal@pourscoreapp.com'
# The one postal address shown on the site and in both legal pages ({{ADDRESS}}). Use a service address
# that accepts legal and recorded mail, not a home address. Keep it identical to the ICO register entry and
# to the POSTAL_ADDRESS secret on the waitlist function.
ADDRESS = '168a Battersea Park Road, London, SW11 4ND, United Kingdom'
if not ADDRESS:
    raise SystemExit('Set ADDRESS in build.py before building.')


def v(name):
    """Asset URL with a content stamp, so browsers fetch the new file after every change."""
    return f'{name}?v={hashlib.md5((HERE / name).read_bytes()).hexdigest()[:8]}'


def page(title, desc, body, current, root, wide=False):
    nav = ''.join(
        f'<a href="{root}{href}"{" aria-current=page" if key == current else ""}>{label}</a>'
        for key, href, label in [('features', 'features/', 'Features'), ('support', '#support', 'Support'), ('privacy', 'privacy/', 'Privacy'), ('terms', 'terms/', 'Terms')]
    )
    stores = f'<div class="hstores">{header_stores(root)}</div>' if wide else ''
    extra = f'<link rel="stylesheet" href="{root}{v("landing.css")}">\n<script>document.documentElement.className="js"</script>' if wide else ''
    tail = f'<script src="{root}{v("site.js")}" defer></script>' if wide else ''
    open_, close_ = ('', '') if wide else ('<div class="wrap">', '</div>')
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{root}favicon.png">
<link rel="stylesheet" href="{root}{v("style.css")}">
{extra}
</head>
<body{' class="wide"' if wide else ''}>
<header><div class="wrap">
<a class="brand" href="{root}"><img src="{root}favicon.png" alt="">Pour Score</a>
<nav>{nav}</nav>
{stores}
</div></header>
<main>{open_}
{body}
{close_}</main>
<footer><div class="wrap">
<span>&copy; 2026 Pour Score. Marlon Kazim May, trading as Pour Score.</span>
<span><a href="{root}features/">Features</a> &middot; <a href="{root}#support">Support</a> &middot; <a href="{root}privacy/">Privacy</a> &middot; <a href="{root}terms/">Terms</a></span>
</div></footer>
{tail}
</body>
</html>
'''


def legal(md_name, title, slug):
    text = (LEGAL / md_name).read_text()
    text = re.sub(r'^# .*\n', '', text, count=1)  # the page supplies its own <h1>
    text = text.replace('{{ADDRESS}}', ADDRESS)
    html = markdown.markdown(text, extensions=['tables'])
    html = html.replace('<table>', '<div class="table"><table>').replace('</table>', '</table></div>')
    html = re.sub(r'([\w.+-]+@pourscoreapp\.com)', r'<a href="mailto:\1">\1</a>', html)
    body = f'<p class="kicker">Pour Score</p>\n<h1>{title}</h1>\n{html}'
    out = HERE / slug / 'index.html'
    out.write_text(page(f'{title} | Pour Score', f'Pour Score {title}.', body, slug, '../'))


def fill(src, root=''):
    for k, v in SUBS.items():
        src = src.replace(k, v)
    return src.replace('src="patterns/', f'src="{root}patterns/')


def read(name):
    return (HERE / 'src' / name).read_text()


home = fill(read('home.html')) + f'''
<section class="sec support" id="support"><div class="wrap">
<div class="sec-head rv"><h2>Support</h2><p>We aim to reply within 5 working days.</p></div>
<div class="sgrid">
<div class="scard rv"><span class="ic"><svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></svg></span>
<h3>Questions, problems or ideas for the app</h3><a class="mail" href="mailto:{SUPPORT}">{SUPPORT}</a></div>
<div class="scard rv"><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/></svg></span>
<h3>Privacy, your data and legal questions</h3><a class="mail" href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></div>
<div class="scard rv"><span class="ic"><svg viewBox="0 0 24 24"><path d="M3 21h18M5 21V8l7-5 7 5v13M10 21v-6h4v6"/></svg></span>
<h3>Who runs Pour Score</h3>
<address>Marlon Kazim May, trading as Pour Score (sole trader)<br>
{ADDRESS}<br>
<a href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></address></div>
<div class="scard del rv">
<div><span class="ic"><svg viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/></svg></span>
<h3>Deleting your account</h3>
<p>Your account, pours and photos are permanently deleted within 30 days. See the <a href="privacy/">Privacy Policy</a> for details.</p></div>
<ol class="steps">
<li>Tap your <b>profile picture</b> at the top of Home or Community.</li>
<li>Tap <b>Edit profile</b>.</li>
<li>Under <b>Account</b> at the bottom, tap <b>Delete account</b>.</li>
<li>Tap <b>Delete account</b> again to confirm.</li>
</ol>
</div>
</div>
</div></section>
'''

(HERE / 'features').mkdir(exist_ok=True)
(HERE / 'features' / 'index.html').write_text(page('Features | Pour Score', 'Guided pours, a live tilt reading, dry rehearsal, milk tutorials and streaks. See what is inside Pour Score.', fill(read('features.html'), '../'), 'features', '../', wide=True))
(HERE / 'index.html').write_text(page('Pour Score | Turn practice into art you are proud of', 'Pour Score coaches every latte art pour step by step, with a live tilt reading, streaks and five tiers to climb.', home, 'home', '', wide=True))
legal('Pour_Score_Privacy_Policy.md', 'Privacy Policy', 'privacy')
legal('Pour_Score_Terms_of_Service.md', 'Terms of Service', 'terms')
print('built index.html, features/index.html, privacy/index.html, terms/index.html')
