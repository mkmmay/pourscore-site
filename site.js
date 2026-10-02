// Scroll reveal (all pages) + the hero cup that changes its latte art (home only).
(function () {
  var rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  // Split [data-words] headings into word spans; light them in reading order as they scroll up the screen.
  var groups = [];
  document.querySelectorAll('[data-words]').forEach(function (el) {
    var walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), texts = [], n;
    while ((n = walk.nextNode())) texts.push(n);
    texts.forEach(function (t) {
      var f = document.createDocumentFragment();
      t.textContent.split(/(\s+)/).forEach(function (s) {
        if (!s) return;
        if (/^\s+$/.test(s)) { f.appendChild(document.createTextNode(s)); return; }
        var w = document.createElement('span'); w.className = 'w'; w.textContent = s; f.appendChild(w);
      });
      t.parentNode.replaceChild(f, t);
    });
    groups.push([el, el.querySelectorAll('.w')]);
  });
  function light() {
    var vh = window.innerHeight;
    groups.forEach(function (g) {
      var p = (vh * 0.92 - g[0].getBoundingClientRect().top) / (vh * 0.45);
      var k = Math.round(Math.max(0, Math.min(1, p)) * g[1].length);
      g[1].forEach(function (w, i) { w.classList.toggle('lit', i < k); });
    });
  }
  if (groups.length) { addEventListener('scroll', light, { passive: true }); addEventListener('resize', light); light(); }

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Phone mockups: the streak grid fills and progress bars sweep in each time a phone scrolls into view.
  if ('IntersectionObserver' in window) {
    var po = new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.target.classList.toggle('go', e.isIntersecting); });
    }, { threshold: 0.35 });
    document.querySelectorAll('.phone').forEach(function (p) { po.observe(p); });
  } else document.querySelectorAll('.phone').forEach(function (p) { p.classList.add('go'); });

  // Tiers: the highlight climbs from Beginner to Barista (passed tiers keep a faint edge), holds, then repeats.
  var ladder = document.getElementById('ladder');
  if (ladder) {
    var rungs = ladder.querySelectorAll('.rung'), tcap = document.getElementById('tiercap'), step = 0, tick = null;
    var setTier = function (i) {
      rungs.forEach(function (r, j) { r.classList.toggle('on', j === i); r.classList.toggle('done', j < i); });
      if (tcap) tcap.innerHTML = '<span class="mono">' + rungs[i].querySelector('.mono').textContent + ' &middot; ' +
        rungs[i].querySelector('b').textContent + '</span>' + rungs[i].querySelector('p').textContent;
    };
    var climb = function () {
      step = (step + 1) % (rungs.length + 2); // the two extra steps hold on Barista
      if (step < rungs.length) setTier(step);
      tick = setTimeout(climb, 1000);
    };
    if (reduce || !('IntersectionObserver' in window)) setTier(rungs.length - 1);
    else {
      setTier(0);
      new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { if (!tick) tick = setTimeout(climb, 1300); }
        else { clearTimeout(tick); tick = null; }
      }, { threshold: 0.3 }).observe(ladder);
    }
  }

  var stage = document.getElementById('stage');
  if (!stage) return;
  var P = [
    ['heart', 'Heart', 'The first one everyone pours', '228,87,46'],
    ['rosetta', 'Rosetta', 'A leaf that rewards rhythm', '196,120,60'],
    ['tulip', 'Tulip', 'Stacked petals, steady hands', '184,86,110'],
    ['swan', 'Swan', 'The showpiece', '110,140,170'],
    ['stacked_tulip', 'Stacked Tulip', 'Tulip, turned up', '150,110,190'],
    ['stacked_rosetta', 'Stacked Rosetta', 'Rosetta for the confident', '120,160,100'],
    ['stacked_heart', 'Rippled Heart', 'Rings inside a heart', '228,87,46']
  ];
  var art = document.getElementById('art'), cup = document.getElementById('cup'), cap = document.getElementById('cap');
  var hero = document.querySelector('.hero2'), tiles = [], imgs = [], cur = -1, timer, user = false;
  P.forEach(function (p, i) {
    var im = new Image(); im.src = 'patterns/' + p[0] + '.png'; im.alt = ''; art.appendChild(im); imgs.push(im);
    var b = document.createElement('button'); b.className = 'tile'; b.type = 'button';
    b.setAttribute('aria-label', p[1]); b.setAttribute('aria-pressed', 'false');
    // arc over the top of the cup; radius 42 keeps the rotated, raised tiles inside the stage (tile is 16% wide)
    var a = (200 - (i * 220) / (P.length - 1)) * Math.PI / 180;
    b.style.left = (50 + 42 * Math.cos(a) - 8) + '%';
    b.style.top = (50 - 42 * Math.sin(a) - 8 + 8) + '%';
    b.style.setProperty('--r', ((i - 3) * 7) + 'deg');
    var ti = new Image(); ti.src = 'patterns/' + p[0] + '.png'; ti.alt = ''; b.appendChild(ti);
    b.addEventListener('click', function () { user = true; clearInterval(timer); show(i); });
    stage.appendChild(b); tiles.push(b);
  });
  function show(i) {
    if (i === cur) return;
    if (cur >= 0) { imgs[cur].classList.remove('on'); tiles[cur].setAttribute('aria-pressed', 'false'); }
    cur = i;
    imgs[i].classList.add('on'); tiles[i].setAttribute('aria-pressed', 'true');
    cup.style.transform = 'rotate(' + ((i % 2 ? 1 : -1) * (3 + i)) + 'deg) scale(1.02)';
    setTimeout(function () { cup.style.transform = ''; }, 500);
    cap.innerHTML = '<b>' + P[i][1] + '</b>' + P[i][2];
    hero.style.setProperty('--glow', 'rgba(' + P[i][3] + ',.24)');
  }
  show(0);
  if (!reduce)
    timer = setInterval(function () { if (!document.hidden) show((cur + 1) % P.length); }, 4200);
})();

// Early access form: posts to the waitlist edge function; ?s= shows the result of the email links.
(function () {
  var f = document.getElementById('early-access');
  if (!f) return;
  var API = 'https://brgzrpfjavmqajmaqdjc.supabase.co/functions/v1/waitlist';
  var msg = f.querySelector('.ea-msg');
  var say = function (t) { msg.textContent = t; };
  var status = { confirmed: 'You are on the list. We will email you when early access opens.',
    unsubscribed: 'You have been removed from the list.',
    invalid: 'That link has expired or was already used. Sign up again below.' };
  var s = new URLSearchParams(location.search).get('s');
  if (status[s]) say(status[s]);
  if (s === 'confirmed') {
    f.classList.add('done');
    f.querySelector('h3').textContent = 'You are on the list';
    say('Thanks for signing up. We will email you as soon as early access opens, and again when Pour Score is live.');
  }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f), btn = f.querySelector('button');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test((d.get('email') || '').trim())) return say('Please enter a valid email address.');
    if (!f.consent.checked) return say('Please tick the box to join the list.');
    btn.disabled = true; say('Sending...');
    fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: d.get('email'), consent: true, website: d.get('website') }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        if (r.ok) { f.reset(); say('Nearly done. We have sent you an email. Click the link in it to confirm and you are on the list.'); }
        else say(r.j.error || 'Something went wrong. Please try again.');
      })
      .catch(function () { say('Something went wrong. Please try again.'); })
      .then(function () { btn.disabled = false; });
  });
})();
