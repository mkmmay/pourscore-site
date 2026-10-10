"""Builds pourscoreapp.com: home (src/home.html + support), /features (src/features.html), /privacy, /terms, /security,
the two SEO pages in seo.py (/latte-art-patterns/, /learn-latte-art/), plus .well-known/security.txt.

The legal pages come straight from Legal Docs/extracted/*.md, so after a doc
changes, rerun this and push:  python3 build.py
Needs the `markdown` package (pip3 install markdown).
"""
import datetime
import hashlib
import json
import re
from pathlib import Path

import markdown
import seo
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


BASE = 'https://pourscoreapp.com/'
# Search Console ownership, second method (the first is googlecc591ae8fcff4c2f.html in the site root). Keep both.
GOOGLE_VERIFY = 'OoHxtDR82EIO0-OP8ReTyXgVBRHtZ3T2AelK3DLApL4'
PATHS = {'home': '', 'features': 'features/', 'support': 'support/', 'privacy': 'privacy/', 'terms': 'terms/', 'security': 'security/',
         'patterns': seo.HUB, 'learn': seo.LEARN}
PATTERNS, ORDER = seo.load()
SUBS['{pattern_tiles}'] = seo.tiles(PATTERNS, ORDER, '../latte-art-patterns/')
SUBS['{cupdefs}'] = f'<svg class="cupdefs" width="0" height="0" aria-hidden="true" focusable="false">{seo.CUP_DEFS}</svg>'


def page(title, desc, body, current, root, wide=False, ld=(), tab=None):
    nav = ''.join(
        f'<a href="{root}{href}"{" aria-current=page" if key == current else ""}>{label}</a>'
        for key, href, label in [('features', 'features/', 'Features'), ('support', 'support/', 'Support'), ('privacy', 'privacy/', 'Privacy'), ('terms', 'terms/', 'Terms')]
    )
    stores = f'<div class="hstores">{header_stores(root)}</div>'
    extra = (f'<link rel="stylesheet" href="{root}{v("landing.css")}">\n' if wide else '') + '<script>document.documentElement.className="js"</script>'
    tail = f'<script src="{root}{v("site.js")}" defer></script>'
    if current in PATHS:
        url = BASE + PATHS[current]
        share = (f'<link rel="canonical" href="{url}">\n'
                 f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Pour Score">\n'
                 f'<meta property="og:title" content="{title}">\n<meta property="og:description" content="{desc}">\n'
                 f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}og.png">\n'
                 f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                 f'<meta property="og:image:alt" content="Pour Score: turn practice into art you are proud of">\n'
                 f'<meta name="twitter:card" content="summary_large_image">\n')
    else:
        share = '<meta name="robots" content="noindex">\n'
    open_, close_ = ('', '') if wide else ('<div class="wrap">', '</div>')
    # JSON-LD is a data block, so the script-src rule in the CSP below does not apply to it.
    for block in [ld] if isinstance(ld, dict) else ld:
        share += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'sha256-cvlem2Rlcb+inScVb7910PMAU98gRDEfAIUVUKXOWd4='; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src https://brgzrpfjavmqajmaqdjc.supabase.co; base-uri 'none'; form-action 'self'; object-src 'none'">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="google-site-verification" content="{GOOGLE_VERIFY}">
{share}<link rel="icon" href="{root}favicon.png">
<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
<link rel="stylesheet" href="{root}{v("style.css")}">
{extra}
</head>
<body class="{'wide' if wide else 'sub' + (' t-' + tab if tab else '')}">
<a class="skip" href="#main">Skip to main content</a>
<header><div class="wrap">
<a class="brand" href="{root}"><img src="{root}favicon.png" alt="">Pour Score</a>
<nav>{nav}</nav>
{stores}
</div></header>
<main id="main" tabindex="-1">{open_}
{body}
{close_}</main>
<footer><div class="wrap">
<span>&copy; 2026 Pour Score. Marlon Kazim May, trading as Pour Score.</span>
<span><a href="{root}{seo.HUB}">Patterns</a> &middot; <a href="{root}{seo.LEARN}">Learn latte art</a> &middot; <a href="{root}features/">Features</a> &middot; <a href="{root}support/">Support</a> &middot; <a href="{root}privacy/">Privacy</a> &middot; <a href="{root}terms/">Terms</a> &middot; <a href="{root}security/">Security</a></span>
<span><a href="https://www.instagram.com/pourscoreapp/" rel="me noopener">Instagram</a> &middot; <a href="https://www.tiktok.com/@pourscoreapp" rel="me noopener">TikTok</a></span>
</div></footer>
{tail}
</body>
</html>
'''


LEGAL_DESC = {
    'privacy': 'How Pour Score collects, uses and protects your data, your rights under UK GDPR, and how to contact us.',
    'terms': 'The terms for using Pour Score: accounts, acceptable use and community content.',
    'security': 'How to report a security problem in the Pour Score app or website, and what to expect when you do.',
}


def meta_card(html):
    """The Last updated / Operator lines at the top of a legal page as a labelled card (the Markdown has them on separate lines)."""
    m = re.match(r'((?:<p><strong>[^<]+:</strong>.*?</p>\n)+)<hr />\n', html, re.S)
    if not m:
        return '', html
    cells = ''.join(
        f'<div{" class=w2" if label in ("Operator", "Address") else ""}><span class="ml">{label}</span><b>{value}</b></div>'
        for label, value in re.findall(r'<strong>([^<]+):</strong> (.*?)(?:<br />\n|</p>)', m.group(1), re.S))
    return f'<div class="meta">{cells}</div>\n', html[m.end():]


def contents(html):
    """Give every <h2> an id and return (html, a jump bar linking to them). The bar is a sticky rail on a wide screen."""
    links, seen = '', set()

    def put(m):
        nonlocal links
        text = re.sub(r'<[^>]+>', '', m.group(1))
        base = re.sub(r'[^a-z0-9]+', '-', re.sub(r'^\d+\.\s*', '', text).lower()).strip('-') or 'section'
        slug_, n = base, 2
        while slug_ in seen:
            slug_, n = f'{base}-{n}', n + 1
        seen.add(slug_)
        links += f'<a href="#{slug_}">{m.group(1)}</a>'
        return f'<h2 id="{slug_}">{m.group(1)}</h2>'
    html = re.sub(r'<h2>(.*?)</h2>', put, html)
    return html, f'<nav class="jumpbar" aria-label="Sections on this page">{links}</nav>\n' if len(seen) > 2 else ''


def legal(md_name, title, slug):
    text = (LEGAL / md_name).read_text()
    text = re.sub(r'^# .*\n', '', text, count=1)  # the page supplies its own <h1>
    text = text.replace('{{ADDRESS}}', ADDRESS)
    html = markdown.markdown(text, extensions=['tables', 'nl2br'])
    html = html.replace('<table>', '<div class="table"><table>').replace('</table>', '</table></div>')
    html = re.sub(r'([\w.+-]+@pourscoreapp\.com)', r'<a href="mailto:\1">\1</a>', html)
    html = re.sub(r'<p>(Our <code>security\.txt</code> file is at <a [^>]+>[^<]+</a>\.)</p>', r'<p class="note">\1</p>', html)
    meta, html = meta_card(html)
    html, bar = contents(html)
    body = (f'<div class="legal-grid">\n<div class="pagehead"><p class="kicker">Pour Score</p>\n<h1>{title}</h1></div>\n'
            f'{meta}{bar}<div class="legal-body">\n{html}</div>\n</div>')
    out = HERE / slug / 'index.html'
    out.write_text(page(f'{title} | Pour Score', LEGAL_DESC[slug], body, slug, '../', tab=slug))


def fill(src, root=''):
    for k, v in SUBS.items():
        src = src.replace(k, v)
    return src.replace('src="patterns/', f'src="{root}patterns/')


def read(name):
    return (HERE / 'src' / name).read_text()


def support_cards(root):
    """The Support cards as a dict, so the home Support section and the /support/ page use the same markup. root is '' or '../'."""
    ic = lambda d: f'<span class="ic"><svg viewBox="0 0 24 24"><path d="{d}"/></svg></span>'
    return {
        'help': f'<div class="scard rv">{ic("M4 5h16v11H9l-5 4z")}\n<h3>Questions, problems or ideas for the app</h3><a class="mail" href="mailto:{SUPPORT}">{SUPPORT}</a></div>',
        'legal': f'<div class="scard rv">{ic("M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z")}\n<h3>Privacy, your data and legal questions</h3><a class="mail" href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></div>',
        'who': f'''<div class="scard rv">{ic("M3 21h18M5 21V8l7-5 7 5v13M10 21v-6h4v6")}
<h3>Who runs Pour Score</h3>
<address>Marlon Kazim May, trading as Pour Score (sole trader)<br>
{ADDRESS}<br>
<a href="mailto:{LEGAL_EMAIL}">{LEGAL_EMAIL}</a></address></div>''',
        'security': f'<div class="scard rv">{ic("M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6zM9 12l2 2 4-4")}\n<h3>Found a security problem?</h3><p>Pour Score is run by one person, who reads every report.</p><a class="mail" href="{root}security/">How to report it</a></div>',
        'delete': f'''<div class="scard del rv">
<div>{ic("M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6")}
<h3>Deleting your account</h3>
<p>Your account, pours and photos are permanently deleted within 30 days. See the <a href="{root}privacy/">Privacy Policy</a> for details.</p></div>
<ol class="steps">
<li>Tap your <b>profile picture</b> at the top of Home or Community.</li>
<li>Tap <b>Edit profile</b>.</li>
<li>Under <b>Account</b> at the bottom, tap <b>Delete account</b>.</li>
<li>Tap <b>Delete account</b> again to confirm.</li>
</ol>
</div>''',
    }


_s = support_cards('')
home = fill(read('home.html')) + f'''
<section class="sec support" id="support"><div class="wrap">
<div class="sechead rv"><div><h2>Support</h2></div><p>We aim to reply within 5 working days.</p></div>
<div class="sgrid">
{_s['help']}
{_s['legal']}
{_s['who']}
{_s['delete']}
</div>
</div></section>
'''

(HERE / 'features').mkdir(exist_ok=True)
(HERE / 'features' / 'index.html').write_text(page('Latte Art App Features: Guided Pours, Live Tilt | Pour Score', 'See every Pour Score feature: guided latte art pours, a live tilt reading, dry rehearsal, milk tutorials and streaks.', fill(read('features.html'), '../'), 'features', '../', wide=True))
(HERE / 'index.html').write_text(page(seo.HOME_TITLE, seo.HOME_DESC, home, 'home', '', wide=True, ld=seo.home_ld()))

# SEO pages generated from the app's own data (seo.py): the patterns guide and the learn-latte-art guide.
def write(path, current, root, built, tab=None):
    title, desc, body, ld = built
    (HERE / path).mkdir(parents=True, exist_ok=True)
    (HERE / path / 'index.html').write_text(page(title, esc_attr(desc), body, current, root, ld=ld, tab=tab))


def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;')


write(seo.HUB, 'patterns', '../', seo.patterns_page(PATTERNS, ORDER))
write(seo.LEARN, 'learn', '../', seo.learn_page(), 'learn')
_s = support_cards('../')
(HERE / 'support').mkdir(exist_ok=True)
(HERE / 'support' / 'index.html').write_text(page(
    'Support: Help, Contact, Delete Your Account | Pour Score',
    'Contact Pour Score support, ask a privacy or legal question, report a security problem or see how to delete your account.',
    '<div class="pagehead"><p class="kicker">Pour Score &middot; Support</p>\n<h1>Support</h1>\n<p class="lead">We aim to reply within 5 working days.</p></div>\n'
    f'<div class="sgrid two">\n{_s["help"]}\n{_s["legal"]}\n{_s["security"]}\n{_s["who"]}\n{_s["delete"]}\n</div>',
    'support', '../', ld=seo.crumbs(('Home', ''), ('Support', 'support/')), tab='support'))
legal('Pour_Score_Privacy_Policy.md', 'Privacy Policy', 'privacy')
legal('Pour_Score_Terms_of_Service.md', 'Terms of Service', 'terms')
(HERE / 'security').mkdir(exist_ok=True)
legal('Pour_Score_Security_Page.md', 'Report a security issue', 'security')

# 404 page: GitHub Pages serves 404.html for any missing path, so every link and asset is root-absolute.
(HERE / '404.html').write_text(page('Page not found | Pour Score', 'That page does not exist.',
    '<div class="pagehead"><p class="kicker">404</p>\n<h1>That page is not here</h1>\n'
    '<p class="lead">The link may be old or mistyped. Looking for a pattern? Try the <a href="/latte-art-patterns/">latte art patterns guide</a> or <a href="/learn-latte-art/">learn latte art at home</a>. '
    'Otherwise head back to the <a href="/">home page</a> or see the <a href="/features/">features</a>.</p></div>',
    '404', '/'))

# robots.txt and sitemap.xml. /confirmed/ is the landing page for the sign-up email link, not content.
today = datetime.date.today().isoformat()
(HERE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /confirmed/\n\nSitemap: {BASE}sitemap.xml\n')
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>\n' for p in PATHS.values()) + '</urlset>\n')
(HERE / 'sitemap.xml').write_text(sitemap)
# Same list under a second name and as plain text: Search Console sometimes sticks on "could not be read" for one
# address on a new property (10 Oct 2026). Submit whichever it accepts; robots.txt keeps pointing at sitemap.xml.
(HERE / 'sitemap-pages.xml').write_text(sitemap)
(HERE / 'sitemap.txt').write_text(''.join(f'{BASE}{p}\n' for p in PATHS.values()))

# security.txt (RFC 9116). Expires is reset on every build, so rebuild and push at least once a year or it
# goes stale. Contact is the support mailbox; point it at a security@ alias once one exists in Zoho.
(HERE / '.well-known').mkdir(exist_ok=True)
expires = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=330)).strftime('%Y-%m-%dT%H:%M:%SZ')
(HERE / '.well-known' / 'security.txt').write_text(
    f'Contact: mailto:{SUPPORT}\n'
    f'Expires: {expires}\n'
    'Preferred-Languages: en\n'
    'Canonical: https://pourscoreapp.com/.well-known/security.txt\n'
    'Policy: https://pourscoreapp.com/security/\n')
# GitHub Pages runs Jekyll, which silently drops folders starting with a dot unless this file exists.
(HERE / '.nojekyll').write_text('')
print('built index.html, features/index.html, privacy/index.html, terms/index.html, security/index.html, .well-known/security.txt')
