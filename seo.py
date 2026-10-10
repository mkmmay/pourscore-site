"""SEO pages built from the app's own data: the patterns guide and the learn-latte-art guide.

Two pages on purpose, one per search intent, with no overlap: /latte-art-patterns/ answers "what are the patterns and how do
I pour each one", /learn-latte-art/ answers "how do I start at home". Steps, fixes, tiers and milk sizes are read from
LatteLearn/src/data/patterns.ts and milk.ts at build time, so the site never drifts from the app. Copy rules are in
Marketing/0_Brand_Book.md: no AI scoring claim, no prices, no reviews, no em dashes, never call Pour Score a course.
"""
import html
import re
from pathlib import Path

HERE = Path(__file__).parent
TS = HERE.parent / 'LatteLearn' / 'src' / 'data' / 'patterns.ts'
MILK_TS = TS.parent / 'milk.ts'
BASE = 'https://pourscoreapp.com/'
HUB = 'latte-art-patterns/'
LEARN = 'learn-latte-art/'
NB = ' '  # keeps '100 ml' on one line in narrow tables
LEVELS = {'beginner': 'Beginner', 'home_pourer': 'Home Pourer', 'confident': 'Confident', 'cafe_ready': 'Café Ready', 'barista': 'Barista'}
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


CTA = '''<div class="card"><h2>Practise it with Pour Score</h2>
<p>Pour Score draws the path across your cup in time with the pour and shows your jug angle live. Rehearse the movement with an empty jug first, then pour. Join the early access list to try it before launch.</p>
<a class="pbtn" href="../#start">Get early access</a></div>'''


def patterns_page(pats, order):
    """(title, description, body, json-ld) for latte-art-patterns/ (root ../). One page, one section per pattern."""
    jump = ' &middot; '.join(f'<a href="#{slug(k)}">{esc(pats[k]["name"])}</a>' for _, ks in order for k in ks)
    sections = ''
    for tier, keys in order:
        sections += f'<h2>{tier}</h2>\n'
        for k in keys:
            p, name = pats[k], esc(pats[k]['name'])
            heading = name if k == 'etched' else f'How to pour a latte art {name.lower()}'
            steps = f"<li><strong>Lay the base.</strong> Fill the cup to about {p['canvas']}% first.</li>"
            steps += ''.join(f'<li><strong>{esc(lab.capitalize())}.</strong> {esc(cue)}</li>' for lab, cue in p['phases'])
            art = (HERE / 'patterns' / f'{k}.png').exists()  # Monk's Head and Etched Animals have no illustration yet
            img = f'<img src="../patterns/{k}.png" width="480" height="480" alt="The {name} latte art pattern" loading="lazy">' if art else ''
            sections += (f'<div class="pat"><div><h3 id="{slug(k)}">{heading}</h3><p>{esc(p["blurb"])}</p>'
                         f'<ol class="steps">{steps}</ol><p><strong>If it goes wrong.</strong> {esc(p["fix"])}</p></div>{img}</div>\n')
    body = f'''<p class="kicker">Pour Score</p>
<h1>Latte art patterns, from monk's head to swan</h1>
<p class="lead">Nine coffee art patterns, grouped by the tier Pour Score teaches them in. Each one has the steps and the fix for its most common fault.</p>
<p>The monk's head is a heart without the tail, and every other pattern is built on it. Add a pull-through and you have a heart. Add a wiggle and you have a rosetta. Push dollops into each other and you have a tulip. Learn them in that order and each new pattern adds only one new movement.</p>
<p class="jump">Jump to: {jump}</p>
<h2>Start every pattern with the base</h2>
<p>Swirl the crema away first, tilt the cup a little and start low in the middle. Rise 2 to 3 cm and move gently side to side until the cup is as full as the pattern needs, a figure given in each section below. Stay off the edges, or foam rides up the wall and shows white.</p>
{sections}<p>New to all of this? Read <a href="../{LEARN}">learn latte art at home</a> first.</p>
{CTA}'''
    desc = "Nine coffee art patterns in learning order, from monk's head and heart to rosetta, tulip and swan. Steps and the fix for each common fault."
    return ('Latte Art Patterns: Heart, Rosetta, Tulip, Swan | Pour Score', desc, body, crumbs(('Home', ''), ('Latte art patterns', HUB)))


def faq():
    """(question, answer html) pairs. Every answer comes from the app or its approved store description."""
    return [
        ('Can you learn latte art at home?',
         "Yes, if you have an espresso machine, a milk jug and a cup. Start with the milk, then pour a monk's head, then a heart, "
         "and add one new pattern at a time. Pour Score is built for this: it guides each pour step by step and gives you a short drill to practise each day."),
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
    """(title, description, body, json-ld) for learn-latte-art/ (root ../). The one beginner guide: kit, milk, first pattern, practice, questions."""
    jugs, drinks, cups, steps = load_milk()
    ml = lambda oz: round(oz * 29.5735 / 5) * 5
    pat = lambda k: f'../{HUB}#{slug(k)}'
    drink_rows = [(n, f'{c}{NB}ml', f'{e}{NB}ml', f'{lo} to {hi}{NB}ml', b) for n, c, e, lo, hi, b in drinks]
    cup_rows = [(n, f'{oz}{NB}oz, about {ml(oz)}{NB}ml', note) for n, oz, note in cups]
    steam = ''.join(f'<li><strong>{esc(t)}.</strong> {esc(b)}</li>' for t, b in steps[:2])
    qs = faq()
    questions = ''.join(f'<h3>{esc(q)}</h3>\n<p>{a}</p>\n' for q, a in qs)
    body = f'''<p class="kicker">Pour Score</p>
<h1>Learn latte art at home: a guide for the home barista</h1>
<p class="lead">Latte art for beginners, in the order that works: the kit, the milk, the first pattern, then practice. The sizes and steps are the ones Pour Score's coach uses.</p>
<h2>What a home barista needs to start</h2>
<p>An espresso machine, a milk jug, a cup and a phone you can prop up. The size of your jug and cup changes how much room you have for a pattern, so Pour Score asks about your coffee station once and fits the guide to it.</p>
<h3>How much milk for each drink</h3>
<p>Starting points for each drink. Adjust to your own cup.</p>
{table(('Drink', 'Cup', 'Espresso', 'Milk', 'How it is built'), drink_rows)}
<h3>Which milk jug</h3>
{table(('Jug', 'Best for'), jugs)}
<h3>Which cup</h3>
<p>The cup sets how much room you have for a pattern.</p>
{table(('Cup', 'Size', 'What it means for your pour'), cup_rows)}
<h2>Steam the milk first</h2>
<ol class="steps">{steam}</ol>
<p><strong>{esc(steps[2][0])}.</strong> {esc(steps[2][1])}</p>
<p><strong>{esc(steps[3][0])}.</strong> {esc(steps[3][1])} Pour Score's Milk First chapters cover stretching, texture and swirling, with fixes for beige milk, big bubbles and thin foam.</p>
<h2>Which latte art pattern to learn first</h2>
<p>Start with the <a href="{pat('dot')}">monk's head</a>. It is a heart without the tail: one drop, no wiggle, and the shape every other pattern is built on. The <a href="{pat('heart')}">heart</a> comes next, then the <a href="{pat('tulip')}">tulip</a>. The <a href="{pat('rosetta')}">rosetta</a> sits at the Confident tier. See <a href="../{HUB}">all nine latte art patterns</a> with the steps for each.</p>
<h2>Practise without wasting milk</h2>
<p>For latte art practice that costs no milk, rehearse the movement dry. In Pour Score's dry rehearsal a trace scrolls down the screen and you mirror it with an empty jug, so you can practise the rocking and the pull-through before you steam any milk. Rehearse in the evening, pour in the morning.</p>
<h2>Common questions</h2>
{questions}{CTA}'''
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qs]}
    desc = 'Learn latte art at home: what a home barista needs, how much milk each drink takes, which pattern to pour first, and how to practise without wasting milk.'
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
