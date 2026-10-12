"""Weekly tips: posts/*.md become /tips/ (the index) and /tips/<slug>/ (one page per post). Not in the header nav on purpose:
reached from the footer, the guides and Instagram and TikTok. Drafts live in ../Marketing/Blog/drafts/ and only reach posts/
after the owner's yes (see .claude/skills/blog-department/SKILL.md).

Post format: `key: value` lines (title, description, date YYYY-MM-DD, art = a patterns/ image name), a line `---`, then markdown.
"""
import re
from datetime import date
from pathlib import Path

import markdown
from seo import BASE, CTA, crumbs, esc, head

HERE = Path(__file__).parent
HUB = 'tips/'
NEEDED = ('title', 'description', 'date')


def load():
    """Published posts, newest first. A post missing a field fails the build rather than going out half-made."""
    posts = []
    for f in (HERE / 'posts').glob('*.md'):
        top, sep, body = f.read_text().partition('\n---\n')
        meta = dict(re.match(r'(\w+):\s*(.*)', l).groups() for l in top.splitlines() if l.strip())
        assert sep and all(k in meta for k in NEEDED), f'{f.name}: needs {NEEDED} then a --- line'
        posts.append({**meta, 'slug': f.stem, 'body': body.strip(), 'art': meta.get('art', 'heart')})
    return sorted(posts, key=lambda p: p['date'], reverse=True)


def nice(d):
    y, m, dd = map(int, d.split('-'))
    return f'{dd} {date(y, m, dd).strftime("%B")} {y}'


TIP_CTA = CTA.replace('../', '../../').replace(
    "Practise it with Pour Score</h2>\n<p>Pour Score draws the path across your cup in time with the pour and shows your jug angle live. "
    "Rehearse the movement with an empty jug first, then pour. Join the early access list to try it before launch.</p>",
    "Want a tip like this each week?</h2>\n<p>Join the early access list on the home page. We will invite you to try Pour Score before it "
    "launches, send a weekly latte art tip, and tell you when it is on the App Store and Google Play.</p>")
assert 'each week' in TIP_CTA


def post_page(p):
    url = f'{HUB}{p["slug"]}/'
    words = len(p['body'].split())
    meta = f'<p class="ml">{nice(p["date"])} &middot; {max(1, round(words / 200))} min read</p>'
    body = (f'{head("Pour Score &middot; Tips", esc(p["title"]), esc(p["description"]), p["art"], "../../")}\n{meta}\n{markdown.markdown(p["body"])}\n{TIP_CTA}')
    ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': p['title'], 'description': p['description'],
           'datePublished': p['date'], 'dateModified': p.get('updated', p['date']), 'inLanguage': 'en-GB', 'image': BASE + 'og.png',
           'mainEntityOfPage': BASE + url, 'author': {'@type': 'Organization', 'name': 'Pour Score', 'url': BASE},
           'publisher': {'@type': 'Organization', 'name': 'Pour Score', 'logo': {'@type': 'ImageObject', 'url': BASE + 'apple-touch-icon.png'}}},
          crumbs(('Home', ''), ('Tips', HUB), (p['title'], url))]
    return f'{p["title"]} | Pour Score', p['description'], body, ld


def index_page(posts):
    items = ''.join(f'<h2><a href="{p["slug"]}/">{esc(p["title"])}</a></h2>\n<p class="ml">{nice(p["date"])}</p>\n<p>{esc(p["description"])}</p>\n'
                    for p in posts)
    lead = 'One short, practical latte art tip each week for the home barista, from milk texture to the first pour.'
    body = f'{head("Pour Score &middot; Tips", "Latte art tips for the home barista", lead, "tulip", "../")}\n{items}{CTA}'
    return ('Latte Art Tips for the Home Barista | Pour Score', 'Short, practical latte art tips for the home barista: milk texture, pouring and what to fix next.',
            body, crumbs(('Home', ''), ('Tips', HUB)))
