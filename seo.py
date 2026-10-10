"""SEO pages built from the app's own data: the patterns hub, one guide per pattern, and the learn-latte-art FAQ.

Steps, fixes and tiers are read from LatteLearn/src/data/patterns.ts at build time, so the site never drifts from
the app. Copy rules are in Marketing/0_Brand_Book.md: no AI scoring claim, no prices, no reviews, no em dashes.
"""
import html
import re
from pathlib import Path

TS = Path(__file__).parent.parent / 'LatteLearn' / 'src' / 'data' / 'patterns.ts'
BASE = 'https://pourscoreapp.com/'
HUB = 'latte-art-patterns/'
LEARN = 'learn-latte-art/'
BARISTA = 'home-barista/'
NB = '\u00a0'  # keeps '100 ml' on one line in narrow tables
MILK_TS = TS.parent / 'milk.ts'
LEVELS = {'beginner': 'Beginner', 'home_pourer': 'Home Pourer', 'confident': 'Confident', 'cafe_ready': 'Café Ready', 'barista': 'Barista'}
SLUGS = {'dot': 'monks-head', 'stacked_tulip': 'stacked-tulip', 'stacked_heart': 'rippled-heart', 'stacked_rosetta': 'stacked-rosetta'}
NO_PAGE = {'etched'}  # one step and a blurb is a thin page, so it is listed on the hub only
HOME_TITLE = 'Pour Score: Latte Art App for the Home Barista'
HOME_DESC = 'Latte art lessons for the home barista. Pour Score guides every pour step by step, with a live tilt reading, dry rehearsal and nine coffee art patterns.'
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


CTA = '''<div class="card"><h2>Practise it with Pour Score</h2>
<p>Pour Score draws the path across your cup in time with the pour and shows your jug angle live. Rehearse the movement with an empty jug first, then pour. Join the early access list to try it before launch.</p>
<a class="pbtn" href="{root}#start">Get early access</a></div>'''


def pattern_page(p, prev, nxt):
    """(title, description, body, json-ld) for one pattern guide, served at latte-art-patterns/<slug>/ (root ../../)."""
    root, lname = '../../', p['name'].lower()
    title = f"How to Pour a Latte Art {p['name']} | Pour Score"
    desc = f"How to pour a latte art {lname}, step by step. {p['tagline']} Plus the fix for the most common fault."
    steps = [f"<strong>Lay the base.</strong> Swirl the crema away first, tilt the cup a little and start low in the middle. "
             f"Rise 2 to 3 cm and move gently side to side until the cup is about {p['canvas']}% full. "
             "Stay off the edges, or foam rides up the wall and shows white."]
    steps += [f"<strong>{esc(lab.capitalize())}.</strong> {esc(cue)}" for lab, cue in p['phases']]
    art = (Path(__file__).parent / 'patterns' / f'{p["key"]}.png').exists()  # Monk's Head has no illustration yet
    img = f'<img src="{root}patterns/{p["key"]}.png" width="480" height="480" alt="The {esc(p["name"])} latte art pattern">' if art else ''
    link = lambda q: f'<a href="../{slug(q["key"])}/">{esc(q["name"])}</a>'
    more = ''.join(f'<li>{lab}: {link(q)}, {esc(lc(q["tagline"]))}</li>' for lab, q in (('Before it', prev), ('After it', nxt)) if q)
    body = f'''<div{' class="hero"' if art else ''}><div><p class="kicker">Latte art pattern</p>
<h1>How to pour a latte art {esc(lname)}</h1>
<p class="lead">{esc(p['blurb'])}</p>
<p>In Pour Score the {esc(lname)} sits in the <strong>{p['tier']}</strong> tier.</p></div>
{img}</div>
<h2>Steps</h2>
<ol class="steps">{''.join(f'<li>{s}</li>' for s in steps)}</ol>
<h2>If it goes wrong</h2>
<p>{esc(p['fix'])}</p>
{CTA.format(root=root)}
<h2>More latte art patterns</h2>
<ul class="plist">{more}<li><a href="../">All nine latte art patterns, in learning order</a></li></ul>'''
    return title, desc, body, crumbs(('Home', ''), ('Latte art patterns', HUB), (p['name'], f'{HUB}{slug(p["key"])}/'))


def hub_page(pats, order):
    """(title, description, body, json-ld) for latte-art-patterns/ (root ../)."""
    rows = ''
    for tier, keys in order:
        items = ''.join(
            f'<li><strong>{esc(pats[k]["name"])}</strong>: {esc(lc(pats[k]["blurb"]))}</li>' if k in NO_PAGE
            else f'<li><a href="{slug(k)}/">{esc(pats[k]["name"])}</a>, {esc(lc(pats[k]["tagline"]))}</li>' for k in keys)
        rows += f'<h2>{tier}</h2>\n<ul class="plist">{items}</ul>\n'
    body = f'''<p class="kicker">Pour Score</p>
<h1>Latte art patterns, from monk's head to swan</h1>
<p class="lead">Nine coffee art patterns, grouped by the tier Pour Score teaches them in. Each page gives the steps and the fix for the most common fault.</p>
{rows}<h2>How the patterns fit together</h2>
<p>The monk's head is a heart without the tail, and every other pattern is built on it. Add a pull-through and you have a heart. Add a wiggle and you have a rosetta. Push dollops into each other and you have a tulip. Learn them in that order and each new pattern adds only one new movement.</p>
<p>New to all of this? Read <a href="../{LEARN}">latte art for beginners</a> or the <a href="../{BARISTA}">home barista guide</a> first.</p>
{CTA.format(root='../')}'''
    desc = "Nine coffee art patterns in learning order, from monk's head and heart to rosetta, tulip and swan. Steps and the fix for each common fault."
    return ('Latte Art Patterns: Heart, Rosetta, Tulip, Swan | Pour Score', desc, body,
            crumbs(('Home', ''), ('Latte art patterns', HUB)))


def faq():
    """(question, answer html) pairs. Every answer comes from the app or its approved store description."""
    h, p = '../' + HUB, lambda k: f'../{HUB}{slug(k)}/'
    return [
        ('Can you learn latte art at home?',
         "Yes, if you have an espresso machine, a milk jug and a cup. Start with the milk, then pour a monk's head, then a heart, "
         "and add one new pattern at a time. Pour Score is built for this: it guides each pour step by step and gives you a short drill to practise each day."),
        ('What do I need to start?',
         "An espresso machine, a milk jug, a cup and a phone you can prop up. The size of your jug and cup changes how much room you have for a pattern, "
         "so Pour Score asks about your coffee station once and fits the guide to it. Jug and cup sizes are in the <a href=\"../" + BARISTA + "\">home barista guide</a>."),
        ('Which latte art pattern should I learn first?',
         f"Start with the <a href=\"{p('dot')}\">monk's head</a>. It is a heart without the tail: one drop, no wiggle, and the shape every other pattern is built on. "
         f"The <a href=\"{p('heart')}\">heart</a> comes next, then the <a href=\"{p('tulip')}\">tulip</a>. The <a href=\"{p('rosetta')}\">rosetta</a> sits at the Confident tier. "
         f"See <a href=\"{h}\">all nine patterns</a> in the order Pour Score teaches them."),
        ('How do I practise latte art without wasting milk?',
         "For latte art practice that costs no milk, rehearse the movement dry. In Pour Score's dry rehearsal a trace scrolls down the screen and you mirror it with an empty jug, "
         "so you can practise the rocking and the pull-through before you steam any milk. Rehearse in the evening, pour in the morning."),
        ('What should steamed milk look like for latte art?',
         "Good milk behaves like a liquid. If the pour feels like you are pushing a foamy substance around, the texture is wrong and no amount of wrist will save the pattern. "
         "Thicker milk needs a wider wiggle and more flow, and thinner milk needs gentler, steadier movement. "
         "Pour Score's Milk First chapters cover stretching, texture and swirling, with fixes for beige milk, big bubbles and thin foam."),
        ('How does the live tilt reading work?',
         "Your phone knows its own angle. Rest it against the jug or the cup and Pour Score shows the angle live in degrees, turning green when you are in range for that phase of the pour. "
         "A jug height rail shows when to pull away and when to get close."),
        ('What is the difference between latte art and coffee art?',
         "In everyday use the two terms mean the same thing: patterns made with steamed milk on an espresso drink, such as a heart, a tulip or a rosetta. "
         "Pour Score teaches poured patterns first and finishes with etched designs such as a bear, a kitten or a seahorse."),
        ('How do the five tiers work?',
         "Pour Score has five tiers: Beginner, Home Pourer, Confident, Café Ready and Barista. Each one is earned from real pours, so you cannot skip ahead "
         "and you cannot be ranked against anyone. Your tier moves when your pours do."),
        ('Is Pour Score available now?',
         "Pour Score is in early access. <a href=\"../#start\">Leave your email on the home page</a> and we will invite you to try it before launch, "
         "and tell you when it is on the App Store and Google Play."),
    ]


def learn_page():
    """(title, description, body, json-ld) for learn-latte-art/ (root ../)."""
    qs = faq()
    body = ('<p class="kicker">Pour Score</p>\n<h1>Latte art for beginners: learn it at home</h1>\n'
            '<p class="lead">Answers for new home baristas, from the first pour to the first rosetta.</p>\n'
            + ''.join(f'<h2>{esc(q)}</h2>\n<p>{a}</p>\n' for q, a in qs) + CTA.format(root='../'))
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qs]}
    desc = 'Can you learn latte art at home? What you need, which pattern to pour first, how to practise without wasting milk, and how Pour Score coaches each pour.'
    return 'Latte Art for Beginners: How to Learn at Home | Pour Score', desc, body, [ld, crumbs(('Home', ''), ('Learn latte art at home', LEARN))]


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


def load_milk():
    """Jugs, drinks, cups and steaming steps from the app's milk.ts (the data behind its Station and Milk Math screens)."""
    t = MILK_TS.read_text()
    g = lambda m, *ix: next(m.group(i) for i in ix if m.group(i) is not None).replace("\\'", "'").replace('\u2013', ' to ')
    jugs = [(g(m, 1, 2), g(m, 4, 5)) for m in re.finditer(r"\{ name: " + _Q + r", cap: (\d+), note: " + _Q, t.split('export type Drink')[0])]
    drinks = [(g(m, 1, 2), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)), g(m, 7, 8))
              for m in re.finditer(r"\{ name: " + _Q + r", cup: (\d+), esp: (\d+), milk: \[(\d+), (\d+)\], build: " + _Q, t)]
    cups = [(g(m, 1, 2), int(m.group(3)), g(m, 4, 5)) for m in re.finditer(r"\{ name: " + _Q + r", oz: (\d+), note: " + _Q, t)]
    steps = [(g(m, 5, 6), g(m, 7, 8)) for m in re.finditer(r"kicker: " + _Q + r",\s+meta: " + _Q + r",\s+title: " + _Q + r",\s+body:\s+" + _Q, t)]
    return jugs, drinks, cups, steps


def barista_page():
    """(title, description, body, json-ld) for home-barista/ (root ../)."""
    jugs, drinks, cups, steps = load_milk()
    table = lambda head, rows: ('<div class="table"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
                                + ''.join('<tr>' + ''.join(f'<td>{esc(str(c))}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')
    ml = lambda oz: round(oz * 29.5735 / 5) * 5
    p = lambda k: f'../{HUB}{slug(k)}/'
    body = f'''<p class="kicker">Pour Score</p>
<h1>Home barista guide: milk, jugs and your first latte art</h1>
<p class="lead">What a home barista needs before the first pour: how much milk each drink takes, which jug and cup to use, and how to steam the milk. The sizes and steps are the ones Pour Score's coach uses.</p>
<h2>How much milk for each drink</h2>
<p>Starting points for each drink. Adjust to your own cup.</p>
{table(('Drink', 'Cup', 'Espresso', 'Milk', 'How it is built'), [(n, f'{c}{NB}ml', f'{e}{NB}ml', f'{lo} to {hi}{NB}ml', b) for n, c, e, lo, hi, b in drinks])}
<h2>Which milk jug</h2>
{table(('Jug', 'Best for'), jugs)}
<h2>Which cup</h2>
<p>The cup sets how much room you have for a pattern.</p>
{table(('Cup', 'Size', 'What it means for your pour'), [(n, f'{oz}{NB}oz, about {ml(oz)}{NB}ml', note) for n, oz, note in cups])}
<h2>Steaming milk in two steps</h2>
<ol class="steps">{''.join(f'<li><strong>{esc(t)}.</strong> {esc(b)}</li>' for t, b in steps[:2])}</ol>
<p><strong>{esc(steps[2][0])}.</strong> {esc(steps[2][1])}</p>
<p><strong>{esc(steps[3][0])}.</strong> {esc(steps[3][1])}</p>
<h2>Then pour your first pattern</h2>
<p>Once the milk behaves like a liquid, start with the <a href="{p('dot')}">monk's head</a>, then the <a href="{p('heart')}">heart</a>. See <a href="../{HUB}">all nine latte art patterns</a>, or read <a href="../{LEARN}">latte art for beginners</a> for the questions new home baristas ask.</p>
{CTA.format(root='../')}'''
    desc = 'A home barista guide to how much milk each drink takes, which jug and cup to use, how to steam milk, and which latte art pattern to pour first.'
    return 'Home Barista Guide: Milk, Jugs and Latte Art | Pour Score', desc, body, crumbs(('Home', ''), ('Home barista guide', BARISTA))
