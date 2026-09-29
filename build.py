"""Builds pourscoreapp.com: home/support, /privacy, /terms.

The legal pages come straight from Legal Docs/extracted/*.md, so after a doc
changes, rerun this and push:  python3 build.py
Needs the `markdown` package (pip3 install markdown).
"""
import re
from pathlib import Path

import markdown

HERE = Path(__file__).parent
LEGAL = HERE.parent / 'Legal Docs' / 'extracted'
SUPPORT = 'support@pourscoreapp.com'
LEGAL_EMAIL = 'legal@pourscoreapp.com'


def page(title, desc, body, current, root):
    nav = ''.join(
        f'<a href="{root}{href}"{" aria-current=page" if key == current else ""}>{label}</a>'
        for key, href, label in [('support', '#support', 'Support'), ('privacy', 'privacy/', 'Privacy'), ('terms', 'terms/', 'Terms')]
    )
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{root}favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header><div class="wrap">
<a class="brand" href="{root}"><img src="{root}favicon.png" alt="">Pour Score</a>
<nav>{nav}</nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<span>&copy; 2026 Pour Score. Marlon Kazim May, trading as Pour Score.</span>
<span><a href="{root}#support">Support</a> &middot; <a href="{root}privacy/">Privacy</a> &middot; <a href="{root}terms/">Terms</a></span>
</div></footer>
</body>
</html>
'''


def legal(md_name, title, slug):
    text = (LEGAL / md_name).read_text()
    text = re.sub(r'^# .*\n', '', text, count=1)  # the page supplies its own <h1>
    html = markdown.markdown(text, extensions=['tables'])
    html = html.replace('<table>', '<div class="table"><table>').replace('</table>', '</table></div>')
    html = re.sub(r'([\w.+-]+@pourscoreapp\.com)', r'<a href="mailto:\1">\1</a>', html)
    body = f'<p class="kicker">Pour Score</p>\n<h1>{title}</h1>\n{html}'
    out = HERE / slug / 'index.html'
    out.write_text(page(f'{title} | Pour Score', f'Pour Score {title}.', body, slug, '../'))


home = f'''<section class="hero">
<div>
<p class="kicker">Latte art coaching</p>
<h1>Learn latte art, one pour at a time.</h1>
<p class="lead">Pour Score guides each pour step by step, from your first heart to a swan. Your phone's tilt sensor shows the cup angle as you pour, and every pour you log builds your progress and your streak.</p>
<p>Coming soon to the App Store.</p>
</div>
<img src="heart.png" alt="A rippled heart latte art pattern">
</section>

<section id="support" class="card">
<h2>Support</h2>
<p>Questions, problems or ideas for the app: <a href="mailto:{SUPPORT}">{SUPPORT}</a></p>
<p>Privacy, your data and legal questions: <a href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></p>
<p>We aim to reply within 5 working days.</p>
<h3>Deleting your account</h3>
<p>Open <strong>Profile</strong> in the app and tap <strong>Delete account</strong> at the bottom. Your account, pours and photos are permanently deleted within 30 days. See the <a href="privacy/">Privacy Policy</a> for details.</p>
<h3>Who runs Pour Score</h3>
<p>Marlon Kazim May, trading as Pour Score (sole trader)<br>
168a Battersea Park Road, London, SW11 4ND, United Kingdom<br>
<a href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></p>
</section>
'''

(HERE / 'index.html').write_text(page('Pour Score | Latte art coaching', 'Pour Score guides each latte art pour step by step, from your first heart to a swan.', home, 'home', ''))
legal('Pour_Score_Privacy_Policy.md', 'Privacy Policy', 'privacy')
legal('Pour_Score_Terms_of_Service.md', 'Terms of Service', 'terms')
print('built index.html, privacy/index.html, terms/index.html')
