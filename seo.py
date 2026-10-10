"""SEO pages built from the app's own data: the patterns guide and the learn-latte-art guide.

Two pages on purpose, one per search intent, with no overlap: /latte-art-patterns/ answers "what are the patterns and how do
I pour each one", /learn-latte-art/ answers "how do I start at home". Pattern names, tiers and milk sizes are read from
LatteLearn/src/data/patterns.ts and milk.ts at build time, so the site never drifts from the app. Copy rules are in
Marketing/0_Brand_Book.md: no AI scoring claim, no prices, no reviews, no em dashes, never call Pour Score a course.
"""
import html
import re
from pathlib import Path

from parts import CUP_BODY, CUP_DEFS

HERE = Path(__file__).parent
TS = HERE.parent / 'LatteLearn' / 'src' / 'data' / 'patterns.ts'
MILK_TS = TS.parent / 'milk.ts'
BASE = 'https://pourscoreapp.com/'
HUB = 'latte-art-patterns/'
LEARN = 'learn-latte-art/'
NB = ' '  # keeps '100 ml' on one line in narrow tables
LEVELS = {'beginner': 'Beginner', 'home_pourer': 'Home Pourer', 'confident': 'Confident', 'cafe_ready': 'Café Ready', 'barista': 'Barista'}
TIERS = list(LEVELS.values())  # lowest tier first, used for the tier ladder
SLUGS = {'dot': 'monks-head', 'stacked_tulip': 'stacked-tulip', 'stacked_heart': 'rippled-heart', 'stacked_rosetta': 'stacked-rosetta', 'etched': 'etched-animals'}
HOME_TITLE = 'Pour Score: Latte Art App for the Home Barista'
HOME_DESC = 'Learn latte art at home with Pour Score: barista lessons on your phone, guided pours, a live tilt reading and dry rehearsal for nine coffee art patterns.'
_Q = r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""


def _str(m):
    return next(g for g in m.groups() if g is not None).replace("\\'", "'")


def load():
    """(patterns by key, display order) parsed from the app's patterns.ts."""
    t = TS.read_text()
    heads = list(re.finditer(r"\n  (\w+): \{\n    key: '(\w+)',", t))
    pats = {}
    for i, h in enumerate(heads):
        b = t[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(t)]
        get = lambda n: _str(re.search(r'\n\s+' + n + r':\s*' + _Q, b))
        pats[h.group(2)] = {
            'key': h.group(2), 'name': get('name'), 'tier': LEVELS[re.search(r"level: '(\w+)'", b).group(1)],
            'canvas': int(re.search(r'canvas: (\d+)', b).group(1)),
            'tagline': get('tagline'), 'fix': get('fix'),
            'blurb': re.sub(r'\s*Unlocks once.*$', '', get('blurb')),  # that sentence is about scoring, which is not live
            'phases': [(m.group(1) or m.group(2), (m.group(3) or m.group(4)).replace("\\'", "'"))
                       for m in re.finditer(r"label: " + _Q + r",\n\s+variable: '\w+',\n\s+cue: " + _Q, b)],
        }
    groups = re.findall(r"label: '([^']+)',[^}]*?keys: \[([^\]]*)\]", t[t.index('PATTERN_GROUPS'):])
    order = [(LEVELS[lab.lower().replace(' ', '_').replace('é', 'e')], re.findall(r"'(\w+)'", ks)) for lab, ks in groups]
    return pats, order


def load_milk():
    """Jugs, drinks, cups and steaming steps from the app's milk.ts (the data behind its Station, Milk Math and Milk First screens)."""
    t = MILK_TS.read_text()
    g = lambda m, *ix: next(m.group(i) for i in ix if m.group(i) is not None).replace("\\'", "'").replace('–', ' to ')
    jugs = [(g(m, 1, 2), g(m, 4, 5)) for m in re.finditer(r"\{ name: " + _Q + r", cap: (\d+), note: " + _Q, t.split('export type Drink')[0])]
    drinks = [(g(m, 1, 2), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)), g(m, 7, 8))
              for m in re.finditer(r"\{ name: " + _Q + r", cup: (\d+), esp: (\d+), milk: \[(\d+), (\d+)\], build: " + _Q, t)]
    cups = [(g(m, 1, 2), int(m.group(3)), g(m, 4, 5)) for m in re.finditer(r"\{ name: " + _Q + r", oz: (\d+), note: " + _Q, t)]
    steps = [(g(m, 5, 6), g(m, 7, 8)) for m in re.finditer(r"kicker: " + _Q + r",\s+meta: " + _Q + r",\s+title: " + _Q + r",\s+body:\s+" + _Q, t)]
    return jugs, drinks, cups, steps


def slug(key):
    return SLUGS.get(key, key)


def esc(s):
    return html.escape(s, quote=True)


def lc(s):
    return s[0].lower() + s[1:]


def strip(s):
    return re.sub(r'<[^>]+>', '', s)


def crumbs(*items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': n, 'item': BASE + u} for i, (n, u) in enumerate(items, 1)]}


def table(head, rows):
    return ('<div class="table"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{esc(str(c))}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')


def drinks_table(drinks):
    """Drink and typical milk, nothing else: common knowledge, and enough to answer the search. Cup, espresso and build notes are the
    app's Milk Math. A normal table on desktop; under 600px each row is a card with the milk amount as the big number (style.css .cards).
    The role attributes keep it a table for screen readers when the CSS makes the rows blocks."""
    rows = ''.join(
        f'<tr role="row"><td role="cell" data-k="name">{esc(n)}</td>'
        f'<td role="cell" data-k="milk"><span class="big">{lo} to {hi}</span><small>ml<span class="mm"> milk</span></small></td></tr>'
        for n, c, e, lo, hi, b in drinks)
    return ('<div class="table cards"><table role="table"><thead><tr role="row"><th role="columnheader">Drink</th><th role="columnheader">Milk</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>')


def head(kicker, title, lead, wm):
    """The glass page head: kicker, h1 and lead on a panel in the page colour, with a faint pattern as watermark."""
    return (f'<div class="pagehead"><img class="wm" src="../patterns/{wm}.png" alt="">'
            f'<p class="kicker">{kicker}</p>\n<h1>{title}</h1>\n<p class="lead">{lead}</p></div>')


def ladder(tier):
    """Five bars, passed tiers edged, this pattern's tier lit (the home page's tier ladder, small)."""
    i = TIERS.index(tier)
    return '<span class="lad" aria-hidden="true">' + ''.join(f'<i class="{"on" if j == i else "done" if j < i else ""}"></i>' for j in range(5)) + '</span>'


CTA = '''<section class="final"><img class="l" src="../patterns/rosetta.png" alt=""><img class="r" src="../patterns/heart.png" alt="">
<div class="inner"><h2>Practise it with Pour Score</h2>
<p>Pour Score draws the path across your cup in time with the pour and shows your jug angle live. Rehearse the movement with an empty jug first, then pour. Join the early access list to try it before launch.</p>
<a class="btn" href="../#start">Get early access</a></div></section>'''


ARROW = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def tiles(pats, order, prefix=''):
    """The nine pattern tiles in learning order. prefix is '' on the patterns page (hash links that site.js opens) or the path to that
    page elsewhere (plain links)."""
    out = ''
    for k in [k for _, ks in order for k in ks]:
        name, n = esc(pats[k]['name']), TIERS.index(pats[k]['tier'])
        out += (f'<li><a class="ptile" href="{prefix}#{slug(k)}" data-tier="{n + 1}"><span class="pt-tier">Tier {n + 1}</span>'
                f'<span class="pt-name">{name}</span><span class="pcup"><svg viewBox="0 0 400 400" aria-hidden="true">{CUP_BODY}</svg>'
                f'<img src="../patterns/{k}.png" width="480" height="480" alt="The {name} latte art pattern" loading="lazy"></span>'
                f'<span class="pt-go" aria-hidden="true">{ARROW}</span></a></li>')
    return out


def heart_trace():
    """The Heart's guided path drawn on the cup: the pool grows, then one line is pulled through (paths from the app's patterns.ts,
    in its 200 unit box). Only the Heart gets this, because it is the sample; the other patterns' paths are the lessons."""
    return ('<g class="trace" transform="translate(76 76) scale(1.24)" fill="none" stroke="#FFF6EC" stroke-width="5" stroke-linecap="round">'
            '<circle class="tr-pool" cx="100" cy="108" r="34"/><path class="tr-line" d="M100 150 L100 46" pathLength="1"/></g>')


def patterns_page(pats, order):
    """(title, description, body, json-ld) for latte-art-patterns/ (root ../). A grid of nine tiles in learning order; tap one and a
    glass box shows what it is, its tier, a cup with the art pouring in and a way into the app (site.js moves it under the tile's row).
    The nine boxes are real sections in the page, so search engines and no-JS readers get them. Only the Heart, the free sample, comes
    with a how-to; every other pattern's steps stay in the app."""
    details = ''
    for k in [k for _, ks in order for k in ks]:
        p, name, n = pats[k], esc(pats[k]['name']), TIERS.index(pats[k]['tier'])
        chapters = len(p['phases'])
        extra = heart_trace() if k == 'heart' else ''
        more = ('<a href="#how-to-pour-a-heart">How to pour it is below.</a>' if k == 'heart'
                else f'Guided live in Pour Score: {chapters} chapters, with the path drawn on your cup.')
        details += (f'<section class="pdetail" id="{slug(k)}" aria-label="{name}"><div class="pd-text"><p class="tier">{ladder(p["tier"])}'
                    f'<span class="ml">Tier {n + 1} of 5 &middot; {p["tier"]}</span></p><h3>{name}</h3><p>{esc(p["blurb"])}</p>'
                    f'<p class="teach">{more}</p><a class="btn sm" href="../#start">Get early access</a></div>'
                    f'<div class="pcup pd-cup"><svg viewBox="0 0 400 400" aria-hidden="true">{CUP_BODY}{extra}</svg>'
                    f'<img src="../patterns/{k}.png" width="480" height="480" alt="" loading="lazy"></div></section>')
    h = pats['heart']
    parts = [('Lay the base', f"Fill the cup to about {h['canvas']}% first.")] + [(lab.capitalize(), cue) for lab, cue in h['phases']]
    moves = ''.join(f'<li><span class="mv-n">{i:02d}</span><b>{esc(t)}</b><span class="mv-t">{esc(c)}</span></li>' for i, (t, c) in enumerate(parts, 1))
    lead = 'Nine coffee art patterns, grouped by the tier Pour Score teaches them in. Tap one to see what it is.'
    body = f'''<svg class="cupdefs" width="0" height="0" aria-hidden="true" focusable="false">{CUP_DEFS}</svg>
{head('Pour Score &middot; Patterns', "Latte art patterns, from monk's head to swan", lead, 'swan')}
<h2>The nine latte art patterns</h2>
<ul class="pgrid">{tiles(pats, order, '')}</ul>
<div class="pdetails">{details}</div>
<p>Pour Score groups the nine patterns into five tiers: Beginner, Home Pourer, Confident, Café Ready and Barista. Each tier is earned from real pours.</p>
<section class="fbub how" id="how-to-pour-a-heart"><span class="num">Free guide</span><h2>How to pour a heart</h2>
<p>A free guide to your first latte art heart, in three moves.</p>
<ol class="moves">{moves}</ol>
<p class="how-foot">In Pour Score the path is drawn across your cup and timed for you.</p></section>
<p>New to all of this? Read <a href="../{LEARN}">learn latte art at home</a> first.</p>
{CTA}'''
    desc = "Nine coffee art patterns in learning order, from monk's head to swan, with a how-to for the latte art heart."
    return ('Latte Art Patterns: Heart, Rosetta, Tulip, Swan | Pour Score', desc, body, crumbs(('Home', ''), ('Latte art patterns', HUB)))


def faq():
    """(question, answer html) pairs. Every answer comes from the app or its approved store description."""
    return [
        ('Can you learn latte art at home?',
         "Yes, if you have an espresso machine, a milk jug and a cup. Pour Score is built for this: it guides each pour step by step "
         "and gives you a short drill to practise each day."),
        ('Are there online barista lessons for home baristas?',
         "Pour Score's lessons run on your phone, at your own pace, beside your own espresso machine. They cover milk texture and latte art, from a first monk's head to a swan. "
         "Pour Score is not a video course, a qualification or an accredited course, and there is no live tutor. It does not cover espresso extraction or running a café bar."),
        ('What is the difference between latte art and coffee art?',
         "In everyday use the two terms mean the same thing: patterns made with steamed milk on an espresso drink, such as a heart, a tulip or a rosetta. "
         "Pour Score teaches poured patterns first and finishes with etched designs such as a bear, a kitten or a seahorse."),
        ('How does the live tilt reading work?',
         "Your phone knows its own angle. Rest it against the jug or the cup and Pour Score shows the angle live in degrees, turning green when you are in range for that phase of the pour. "
         "A jug height rail shows when to pull away and when to get close."),
        ('How do the five tiers work?',
         "Pour Score has five tiers: Beginner, Home Pourer, Confident, Café Ready and Barista. Each one is earned from real pours, so you cannot skip ahead "
         "and you cannot be ranked against anyone. Your tier moves when your pours do."),
        ('Is Pour Score available now?',
         "Pour Score is in early access. <a href=\"../#start\">Leave your email on the home page</a> and we will invite you to try it before launch, "
         "and tell you when it is on the App Store and Google Play."),
    ]


def learn_page():
    """(title, description, body, json-ld) for learn-latte-art/ (root ../). The one beginner guide: kit, typical milk, where to start, practice, questions."""
    drinks = load_milk()[1]
    pat = lambda k: f'../{HUB}#{slug(k)}'
    qs = faq()
    questions = ''.join(f'<h3>{esc(q)}</h3>\n<p>{a}</p>\n' for q, a in qs)
    lead = "Latte art for beginners: what a home barista needs, how much milk each drink takes, and where to go next. The milk sizes are the ones Pour Score's coach uses."
    body = f'''{head('Pour Score &middot; Learn', 'Learn latte art at home: a guide for the home barista', lead, 'rosetta')}
<h2>What a home barista needs to start</h2>
<p>An espresso machine, a milk jug, a cup and a phone you can prop up. The size of your jug and cup changes how much room you have for a pattern, so Pour Score asks about your coffee station once and fits the guide to it.</p>
<h3>How much milk for each drink</h3>
<p>Typical starting points. Pour Score's Milk Math fits them to your own jug and cup.</p>
{drinks_table(drinks)}
<h2>Steam the milk first</h2>
<p>Texture decides whether a pattern holds. Pour Score's milk chapters cover stretching, texture and swirling, with fixes for beige milk, big bubbles and thin foam.</p>
<h2>Which latte art pattern to learn first</h2>
<p>Pour Score teaches nine patterns across five tiers, from the <a href="{pat('dot')}">monk's head</a> to the <a href="{pat('swan')}">swan</a>, each tier earned from real pours. See <a href="../{HUB}">all nine latte art patterns</a> and the tier each one belongs to.</p>
<h2>Practise without wasting milk</h2>
<p>For latte art practice that costs no milk, rehearse the movement dry. In Pour Score's dry rehearsal a trace scrolls down the screen and you mirror it with an empty jug, so you can practise the rocking and the pull-through before you steam any milk. Rehearse in the evening, pour in the morning.</p>
<h2>Common questions</h2>
{questions}{CTA}'''
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qs]}
    desc = 'Learn latte art at home: what a home barista needs, how much milk each drink takes, where to start and how to practise without wasting milk.'
    return "Learn Latte Art at Home: A Home Barista's Guide | Pour Score", desc, body, [ld, crumbs(('Home', ''), ('Learn latte art at home', LEARN))]


def home_ld():
    """Organisation, site and app facts for the home page. Only what is true and visible: no rating, no price."""
    org = BASE + '#org'
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': org, 'name': 'Pour Score', 'url': BASE, 'logo': BASE + 'apple-touch-icon.png',
         'email': 'support@pourscoreapp.com',
         'sameAs': ['https://www.instagram.com/pourscoreapp/', 'https://www.tiktok.com/@pourscoreapp']},
        {'@type': 'WebSite', 'name': 'Pour Score', 'url': BASE, 'inLanguage': 'en-GB', 'publisher': {'@id': org}},
        # ponytail: add operatingSystem, installUrl and offers when the store pages are live and plans are decided.
        {'@type': 'MobileApplication', 'name': 'Pour Score', 'url': BASE, 'description': HOME_DESC, 'inLanguage': 'en-GB',
         'applicationCategory': 'EducationalApplication', 'publisher': {'@id': org},
         'featureList': ['Guided pours with a path that draws itself across the cup', 'Live tilt angle reading',
                         "Dry rehearsal with no milk", 'Milk texture lessons',
                         "Nine latte art patterns from monk's head to swan", 'Pour log with photo, streak and five tiers']},
    ]}
