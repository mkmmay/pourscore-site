"""Reusable HTML pieces for the landing and features pages (phone mockups, cards, store badge)."""
import random

APPLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.5 2.1-3.6-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.15-2.9.9-3.7.9s-1.9-.85-3.2-.8c-1.6 0-3.1.95-4 2.4-1.7 3-.45 7.3 1.2 9.7.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8s1.9.8 3.2.8 2.1-1.2 2.9-2.3c.9-1.3 1.3-2.6 1.3-2.7 0 0-2.4-.9-2.4-3.7zM14.1 5.5c.65-.8 1.1-1.9 1-3-1 0-2.1.65-2.8 1.4-.6.7-1.15 1.8-1 2.9 1.1.1 2.2-.55 2.8-1.3z"/></svg>'

PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 20.5v-17c0-.59.34-1.11.84-1.35L13.69 12l-9.85 9.85c-.5-.25-.84-.76-.84-1.35zm13.81-5.38L6.05 21.34l8.49-8.49 2.27 2.27zm3.35-4.31c.34.27.59.69.59 1.19s-.22.9-.57 1.18l-2.29 1.32-2.5-2.5 2.5-2.5 2.27 1.31zM6.05 2.66l10.76 6.22-2.27 2.27-8.49-8.49z"/></svg>'

# Paste the store links here at launch; every badge and header button on the site switches from "Coming soon" to a live link.
APP_STORE_URL = ''
PLAY_URL = ''
_STORES = [(APPLE, 'App Store', APP_STORE_URL, 'Download on the', 'Coming soon on the'),
           (PLAY, 'Google Play', PLAY_URL, 'Get it on', 'Coming soon on')]


def _badge(icon, name, url, live, soon):
    label = live if url else soon
    tag, href = ('a', f' href="{url}"') if url else ('span', '')
    return f'<{tag} class="store"{href} aria-label="{label} {name}">{icon}<span><small>{label}</small><b>{name}</b></span></{tag}>'


STORE = '<div class="stores">' + ''.join(_badge(*s) for s in _STORES) + '</div>'


def header_stores(root):
    """Compact store buttons for the header; until the links exist they jump to the download section."""
    return ''.join(f'<a class="hs" href="{url or root + "#start"}" aria-label="{name}">{icon}<span>{name}</span></a>'
                   for icon, name, url, _, _ in _STORES)


def phone(inner):
    return f'<div class="sb"><span>9:41</span><span>5G</span></div>{inner}'


def row_img(n, name, sub, tag, green):
    return (f'<div class="row"><img src="patterns/{n}.png" alt="">'
            f'<span><b>{name}</b><i>{sub}</i></span><span class="tag{" g" if green else ""}">{tag}</span></div>')


PH_LIST = phone('<span class="mono">Patterns</span><h3>Pick a pour</h3>' + ''.join(
    row_img(*r) for r in [('heart', 'Heart', '3 chapters', 'Start here', 1), ('tulip', 'Tulip', 'Stacked petals', 'Tier 2', 0),
                          ('rosetta', 'Rosetta', 'Wiggle and pull', 'Tier 3', 0), ('swan', 'Swan', 'The showpiece', 'Tier 5', 0)]
) + '<div class="btn-m">Start guided pour</div>')

PH_POUR = phone('''<span class="mono">Heart &middot; chapter 2 of 3</span><h3>Pull through</h3>
<div class="disc"><svg viewBox="0 0 200 200"><path class="trail" d="M100 150 C 60 130, 55 80, 100 62 C 145 80, 140 130, 100 150" fill="none" stroke="#FFF6EC" stroke-width="9" stroke-linecap="round"/><circle cx="100" cy="150" r="6" fill="#E4572E"/></svg></div>
<div class="readout"><div><span class="mono">Tilt</span><br><big>28&deg;</big></div><div style="text-align:right"><span class="mono">Jug height</span><br><b style="font-size:15px;color:var(--ink)">Close</b></div></div>
<div class="bar"><i style="width:68%"></i></div><div class="mono" style="margin-top:6px">68% of the pattern</div>''')

PH_TILT = phone('''<span class="mono">Live tilt</span><h3>Hold steady</h3>
<svg viewBox="0 0 200 120" style="width:100%;margin-top:12px"><path d="M20 110 A80 80 0 0 1 180 110" fill="none" stroke="#2a211c" stroke-width="14" stroke-linecap="round"/><path d="M20 110 A80 80 0 0 1 120 38" fill="none" stroke="#7FB069" stroke-width="14" stroke-linecap="round"/><text x="100" y="100" text-anchor="middle" font-family="Archivo" font-weight="600" font-size="40" fill="#F4ECE4">28&deg;</text></svg>
<div class="row"><span><b>In range</b><i>Target 25 to 35&deg;</i></span><span class="tag g tag-r">Good</span></div>
<div class="row"><span><b>Jug height</b><i>Stay close to the surface</i></span><span class="tag tag-r">Close</span></div>''')

PH_TRACE = phone('''<span class="mono">Dry rehearsal</span><h3>Mirror the trace</h3>
<svg viewBox="0 0 200 250" style="width:100%;margin-top:10px"><path d="M100 0 C 140 20, 60 40, 140 60 S 60 100, 140 120 S 100 150, 100 170 L100 245" fill="none" stroke="#E4572E" stroke-width="5" stroke-linecap="round" stroke-dasharray="6 8" opacity=".6"/><path d="M100 0 C 140 20, 60 40, 140 60 S 60 100, 140 120" fill="none" stroke="#FFF6EC" stroke-width="5" stroke-linecap="round"/><circle cx="140" cy="120" r="8" fill="#E4572E"/></svg>
<div class="btn-m">Nice. Try it for real?</div>''')

PH_MILK = phone('<span class="mono">Chapter 0</span><h3>Milk first</h3>' + ''.join(
    f'<div class="row"><span class="tag{" g" if d else ""}">{n}</span><span><b>{s}</b><i>{x}</i></span></div>'
    for n, s, x, d in [('1', 'Stretch', 'Add air until it feels warm', 1), ('2', 'Texture', 'Glossy, like wet paint', 1),
                       ('3', 'Swirl', 'Keep it moving until you pour', 0), ('4', 'Fix it', 'Beige, bubbly or thin?', 0)]))

_rnd = random.Random(7)
_heat = ''.join(f'<i class="{_rnd.choice(["", "l1", "l2", "l3", "l3"])}" style="--i:{n}"></i>' for n in range(56))
PH_PROG = phone(f'''<span class="mono">Progress</span><h3>Confident</h3>
<div class="bar"><i style="width:72%"></i></div><div class="mono" style="margin-top:5px">72% to Café Ready</div>
<div class="heat">{_heat}</div>
<div class="row"><span><b>9 day streak</b><i>Poured today</i></span><span class="tag g tag-r">Best</span></div>
<div class="row"><span><b>41 pours logged</b><i>Private by default</i></span></div>''')

_CARDS = [
    ('guided', 'Guided pours', 'A path draws across the cup in time with the pour, hands free.', '<path d="M4 18c4-10 12-10 16 0M12 4v6"/>'),
    ('tilt', 'Live tilt', 'See your cup angle in degrees, green when you are in range.', '<path d="M4 18a8 8 0 0 1 16 0M12 18l4-6"/>'),
    ('rehearsal', 'Dry rehearsal', 'Practise the motion with an empty jug and a scrolling trace.', '<path d="M3 12c3-6 5 6 8 0s5 6 8 0"/>'),
    ('milk', 'Milk first', 'Stretching and texture, explained plainly with fixes for faults.', '<path d="M8 3h8l-1 5 2 4v9H7v-9l2-4z"/>'),
    ('progress', 'Progress and streaks', 'Log pours, keep your flame lit and unlock five tiers.', '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>'),
    ('patterns', 'Pattern library', 'Nine patterns from a first heart to a swan.', '<circle cx="12" cy="12" r="9"/><path d="M12 7v10M7 12h10"/>'),
]
CARDS = ''.join(
    f'<a class="fcard rv" href="features/#{k}"><span class="ic"><svg viewBox="0 0 24 24">{ic}</svg></span><h3>{h}</h3><p>{p}</p><span class="more">Learn more &rarr;</span></a>'
    for k, h, p, ic in _CARDS)

GALLERY = ''.join(f'<div><img src="patterns/{n}.png" alt="">{label}</div>' for n, label in [
    ('heart', 'Heart'), ('rosetta', 'Rosetta'), ('tulip', 'Tulip'), ('swan', 'Swan'),
    ('stacked_tulip', 'Stacked Tulip'), ('stacked_rosetta', 'Stacked Rosetta'), ('stacked_heart', 'Rippled Heart')])

SUBS = {'{store}': STORE, '{store_dark}': STORE, '{ph_list}': PH_LIST, '{ph_pour}': PH_POUR, '{ph_tilt}': PH_TILT,
        '{ph_trace}': PH_TRACE, '{ph_milk}': PH_MILK, '{ph_prog}': PH_PROG, '{cards}': CARDS, '{gallery}': GALLERY}
