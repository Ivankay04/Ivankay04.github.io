#!/usr/bin/env python3
# Сборка страниц Asferia v2. Тексты: build/content/<lang>.json. Запуск: python3 build/build.py
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://asferia.kz/'
LANGS = ['ru', 'en', 'zh', 'kk']
PATHS = {'ru': {'home': 'index.html', 'summer': 'leto.html', 'winter': 'zima.html', 'freeride': 'freeride.html', 'blog': 'blog.html'},
         'en': {'home': 'en.html', 'summer': 'en/summer.html', 'winter': 'en/winter.html', 'freeride': 'en/freeride.html', 'blog': 'blog-en.html'},
         'zh': {'home': 'zh/index.html', 'summer': 'zh/summer.html', 'winter': 'zh/winter.html', 'freeride': 'zh/freeride.html', 'blog': 'blog/zh/index.html'},
         'kk': {'home': 'kk/index.html', 'summer': 'kk/summer.html', 'winter': 'kk/winter.html', 'freeride': 'kk/freeride.html', 'blog': 'blog.html'}}
LABEL = {'ru': 'RU', 'en': 'EN', 'zh': '中文', 'kk': 'ҚАЗ'}
HTML_LANG = {'ru': 'ru', 'en': 'en', 'zh': 'zh-Hans', 'kk': 'kk'}
TOURS = {'ru': {'radon': 'tury/radonovoe-ozero.html', 'zvezdny': 'tury/pereval-zvezdny.html', 'bogd': 'tury/ustye-bogdaniha.html',
                'malo': 'tury/maloulbinskoe.html', 'uba': 'tury/ubinsky-vodopad.html', 'katon': 'tury/katon-karagay.html'},
         'en': {'radon': 'tury/radon-lake.html', 'zvezdny': 'tury/zvezdny-pass.html', 'bogd': 'tury/bogdanikha-river-mouth.html',
                'malo': 'tury/maloulba-reservoir.html', 'uba': 'tury/ubinsky-waterfall.html', 'katon': 'tury/katon-karagay-expedition.html'}}
TOURS['zh'] = TOURS['en']; TOURS['kk'] = TOURS['ru']
# Картинки. Слоты assets/v2/* заменяются файлом с тем же именем — пересборка не нужна.
HERO = {'home': 'assets/pilot/hero-road.webp', 'summer': 'assets/pilot/season-summer.webp', 'winter': 'assets/pilot/season-winter.jpg'}
# ===== Сезон главной: 'winter' — с ноября по март, 'summer' — с апреля. Поменять и пересобрать.
SEASON_MODE = 'winter'
# ===== Цены фрирайда, ₸ за человека в день. 0 — на сайте «цена по запросу».
FREERIDE_PRICE = {'cat': 0, 'sled': 0}
def _slot(path, fallback):
    return path if os.path.exists(os.path.join(ROOT, path)) else fallback
HERO['freeride'] = _slot('assets/v2/freeride-hero.jpg', 'assets/v2/winter-catski.jpg')
if SEASON_MODE == 'winter':
    HERO['home'] = 'assets/pilot/season-winter.jpg'
STOPS = ['assets/pilot/stop-katon-karagay.webp', 'assets/pilot/stop-yazevoye.webp', 'assets/photo-radonlake.jpg', 'assets/pilot/stop-markakol.webp', 'assets/photo-maloulba.jpg']
STAYS = [('bearlog-hotel.webp', 'Bear Log'), ('altai-resort.webp', 'Altai Resort'), ('stay-aituma-markakol.webp', 'Aituma'),
         ('stay-alasha-katon-karagay.jpg', 'Alasha'), ('teremok-rahman.webp', 'Teremok'), ('camp.jpg', '')]
DAY = [('radon', 'assets/photo-radonlake.jpg', 35000), ('zvezdny', 'assets/photo-zvezdny.jpg', 30000), ('bogd', 'assets/photo-bogdaniha.jpg', 40000),
       (None, 'assets/v2/day-cherepanovsky.jpg', 30000), (None, 'assets/v2/day-prohodnoy.jpg', 25000)]
MULTI = [('malo', 60000), ('uba', 65000), ('katon', 160000), (None, 0)]
ACT = [60000, 80000, 20000, 20000, 50000, 50000, 0, 0]
WINTER_SLOTS = ['assets/v2/winter-catski.jpg', 'assets/v2/winter-snowmobile.jpg']
TEAM = [('photo-ivandirector.jpg', 'center top'), ('photo-gidalexandr.jpg', 'center 10%'), ('photo-gidvladislav.jpg', 'center 15%'), ('photo-admin-sofia.jpg', 'center 5%')]
LEGAL = {'ru': 'ИП Кайгородов · ИИН 040204551300 · Юр. адрес: г. Риддер, проспект Независимости, д. 27, кв/офис 2 · Факт. адрес: г. Риддер, 3-й мкр, д. 9 (кафе «Милано») · АО «Kaspi Bank», БИК CASPKZKA, ИИК KZ40722S000042445158, Кбе 19 · Тел.: +7 777 065 02 60 · ivan.kaygorodov.2000@mail.ru · СНР (упрощённая декларация), не плательщик НДС',
         'en': 'IE Kaigorodov · IIN 040204551300 · Registered address: 27 Nezavisimosti Ave., office 2, Ridder, Kazakhstan · Office: 3rd microdistrict, 9, Ridder · Kaspi Bank JSC, BIC CASPKZKA, IBAN KZ40722S000042445158, Kbe 19 · Tel.: +7 777 065 02 60 · ivan.kaygorodov.2000@mail.ru · Simplified tax regime, not a VAT payer'}
METRIKA = open(os.path.join(ROOT, 'build/metrika.html'), encoding='utf-8').read()

def canon(lang, page):
    p = PATHS[lang][page]
    p = '' if p == 'index.html' else (p[:-10] if p.endswith('/index.html') else p)
    return BASE + p

def price(c, n):
    if not n: return c['on_request']
    return c['price_fmt'].format(f'{n:,}'.replace(',', c['thousands']))

def sec_head(h, cls=''):
    sub = f'<div class="sub">{h["sub"]}</div>' if h.get('sub') else ''
    return f'<div class="section-head reveal {cls}"><div class="eyebrow">{h["eyebrow"]}</div><h2>{h["h2"]}</h2>{sub}</div>'

def head(c, lang, page, R):
    m = c['meta'][page]
    alts = ''.join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{canon(l, page)}">\n' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{canon("en", page)}">\n'
    fam = {'zh': '', 'kk': 'family=Inter:wght@400;500;600;700&family=Oswald:wght@700'}.get(lang, 'family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400')
    fonts = f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?{fam}&display=swap" rel="stylesheet">\n' if fam else ''
    ld = ''
    if page == 'home':
        org = {"@context": "https://schema.org", "@type": "TravelAgency", "@id": BASE + "#organization", "name": "Asferia Adventure",
               "url": canon(lang, 'home'), "logo": BASE + "assets/favicon/favicon-192.png", "image": BASE + "assets/photo-website-hero3.jpg",
               "description": m['desc'], "telephone": "+77770650260", "email": "asferia@mail.ru", "foundingDate": "2023",
               "address": {"@type": "PostalAddress", "addressLocality": "Ridder", "addressRegion": "East Kazakhstan", "addressCountry": "KZ"},
               "geo": {"@type": "GeoCoordinates", "latitude": 50.353, "longitude": 83.507},
               "areaServed": [{"@type": "AdministrativeArea", "name": "East Kazakhstan Region"}, {"@type": "TouristAttraction", "name": "Katon-Karagay National Park"},
                              {"@type": "Place", "name": "Altai Mountains"}, {"@type": "Place", "name": "Lake Markakol"}],
               "knowsLanguage": ["ru", "en", "kk"], "sameAs": ["https://www.instagram.com/asferia_adventure/", "https://t.me/asferiakazakhstan"]}
        faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', a)}} for q, a in c['faq']['items']]}
        ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (org, faq))
    if page == 'freeride':
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', a)}} for q, a in c['freeride']['faq']['items']]}, ensure_ascii=False) + '</script>\n'
    if page in ('winter', 'freeride'):
        ld += trips_ld(c, lang, page)
    return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{m["title"]}</title>
<meta name="description" content="{m["desc"]}">
<link rel="canonical" href="{canon(lang, page)}">
{alts}<meta name="geo.region" content="KZ-VOS">
<meta name="geo.placename" content="Ridder, East Kazakhstan">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Asferia Adventure">
<meta property="og:title" content="{m["title"]}">
<meta property="og:description" content="{m["desc"]}">
<meta property="og:url" content="{canon(lang, page)}">
<meta property="og:image" content="{BASE}{HERO[page]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/x-icon" href="{R}assets/favicon/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="{R}assets/favicon/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="{R}assets/favicon/favicon-180.png">
<meta name="theme-color" content="#1F1F1F">
<link rel="preload" as="image" href="{R}{HERO[page]}">
{ld}{fonts}<link rel="stylesheet" href="{R}css/site.css">
</head>
<body>
{METRIKA}
'''

def nav(c, lang, page, R):
    P = PATHS[lang]; n = c['nav']; home = R + P['home']
    langs = ''.join(f'<a href="{R}{PATHS[l][page]}" class="lang{" on" if l == lang else ""}" hreflang="{HTML_LANG[l]}">{LABEL[l]}</a>' for l in LANGS)
    return f'''<nav class="nav" id="nav"><div class="container nav-row">
<a href="{home}" class="logo">ASFERIA<span>·</span>ADVENTURE</a>
<div class="nav-links" id="navLinks">
<a href="{R}{P["summer"]}">{n["summer"]}</a><a href="{R}{P["winter"]}">{n["winter"]}</a><a href="{R}{P["freeride"]}">{n["freeride"]}</a><a href="{home}#journey">{n["journey"]}</a><a href="{home}#about">{n["about"]}</a><a href="{R}{c["blog_url"]}">{n["blog"]}</a><a href="#contact">{n["contact"]}</a>
<span class="langs">{langs}</span>
</div>
<button class="nav-toggle" aria-label="Menu" onclick="document.getElementById('navLinks').classList.toggle('open')">☰</button>
</div></nav>
'''

def hero_video(page, R):
    v = f'assets/v2/hero-{page}.mp4'
    if not os.path.exists(os.path.join(ROOT, v)): return ''
    return f'<video autoplay muted loop playsinline preload="metadata" poster="{R}{HERO[page]}"><source src="{R}{v}" type="video/mp4"></video>'

def hero(h, page, R, short=False):
    lines = '<br>'.join(f'<span class="accent">{x[1:]}</span>' if x.startswith('*') else x for x in h['h1'])
    facts = ''.join(f'<div><b>{b}</b> {t}</div>' for b, t in h['facts'])
    ctas = f'<div class="ctas reveal"><a href="#booking" class="btn btn--tan">{h["cta1"]} <span class="arrow">→</span></a>' + (f'<a href="{h["cta2_href"]}" class="btn btn--ghost">{h["cta2"]}</a>' if h.get('cta2') else '') + '</div>'
    return f'''<section class="hero{" hero--short" if short else ""}" id="top">
<div class="hero-bg" id="heroBg" style="background-image:url('{R}{HERO[page]}')">{hero_video(page, R)}</div>
<div class="container hero-content">
<div class="eyebrow reveal">{h["eyebrow"]}</div>
<h1 class="reveal hero-long" id="heroHeadline">{lines}</h1>
<p class="sub reveal">{h["sub"]}</p>
{ctas}
<div class="hero-facts reveal">{facts}</div>
</div></section>
'''

def card(R, img, pill, title, desc, href=None, cls='', pillcls=''):
    tag = 'a' if href else 'article'
    hr = f' href="{R}{href}"' if href else ''
    return f'''<{tag}{hr} class="tour-card {cls}"><div class="slot">{img}</div><div class="card-bg" style="background-image:url('{R}{img}')"></div><div class="scrim"></div>
<div class="corners"><span class="pill {pillcls}">{pill}</span></div><div class="tour-info"><h3>{title}</h3><div class="desc long">{desc}</div></div></{tag}>
'''

def booking(c, lang, page):
    f = c['form']
    opts = ''.join(f'<option>{o}</option>' for o in f['options'][page])
    ppl = ''.join(f'<option>{o}</option>' for o in ['1', '2', '3', '4', '5–8', '9–12', '12+'])
    ben = ''.join(f'<li>{b}</li>' for b in f['benefits'])
    intl = lang in ('en', 'zh')
    return f'''<section class="booking" id="booking"><div class="booking-bg"></div><div class="container"><div class="booking-grid">
<div class="reveal reveal-l"><div class="eyebrow">{f["eyebrow"]}</div><h2>{f["h2"]}</h2><p class="lede">{f["lede"]}</p><ul class="benefits">{ben}</ul></div>
<div class="booking-form reveal reveal-r"><div class="form-eyebrow">{f["feyebrow"]}</div><h3>{f["fh3"]}</h3>
<form id="bookingForm" data-tag="{lang} · {page}" data-sending="{f["sending"]}" data-sent="{f["sent"]}" data-sentmsg="{f["sent_msg"]}" data-err="{f["err"]}">
<div class="field"><label>{f["name"]}</label><input type="text" id="f-name" required></div>
<div class="field"><label>Email</label><input type="email" id="f-email" placeholder="you@email.com"{" required" if intl else ""}></div>
<div class="field"><label>{f["phone"]}</label><input type="text" id="f-phone"{"" if intl else " required"}></div>
<div class="field"><label>{f["what"]}</label><select id="f-tour" required><option value="">{f["select"]}</option>{opts}</select></div>
<div class="field"><label>{f["people"]}</label><select id="f-people"><option value="">{f["select"]}</option>{ppl}</select></div>
<div class="field"><label>{f["dates"]}</label><input type="text" id="f-date" placeholder="{f["dates_ph"]}"></div>
<button type="submit" id="f-btn" class="btn btn--tan">{f["send"]} <span class="arrow">→</span></button>
<div id="f-status" style="margin-top:12px;font-size:13px;color:var(--tan);display:none;"></div>
<div class="note">{f["note"]}</div></form></div></div></div></section>
'''

def contact_footer(c, lang, R):
    k = c['contact']; ft = c['footer']; P = PATHS[lang]; n = c['nav']
    ch = ''.join(f'<a class="contact-channel" href="{u}"><div class="ico">{i}</div><div><div class="ch-label">{l}</div></div></a>' for i, l, u in k['channels'])
    return f'''<section class="contact" id="contact"><div class="container">
{sec_head(k)}
<div class="contact-grid"><div class="contact-card reveal reveal-l"><div class="photo"></div><div><span class="who-tag">{k["tag"]}</span>
<h3 class="who-name" style="margin-top:12px;">{k["name"]}</h3><div class="who-role">{k["role"]}</div>
<p style="color:rgba(245,239,230,0.78);font-size:14px;margin:0;">{k["quote"]}</p></div></div>
<div class="contact-channels reveal reveal-r">{ch}</div></div></div></section>
<footer class="footer"><div class="container"><div class="footer-grid">
<div><div class="logo">ASFERIA<span>·</span>ADVENTURE</div><div class="tag">{ft["tag"]}</div></div>
<div><h5>{ft["nav"]}</h5><ul><li><a href="{R}{P["summer"]}">{n["summer"]}</a></li><li><a href="{R}{P["winter"]}">{n["winter"]}</a></li><li><a href="{R}{P["freeride"]}">{n["freeride"]}</a></li><li><a href="{R}{P["home"]}#journey">{n["journey"]}</a></li><li><a href="{R}{c["blog_url"]}">{n["blog"]}</a></li><li><a href="{R}{P["home"]}#about">{n["about"]}</a></li></ul></div>
<div><h5>{ft["contact"]}</h5><ul><li><a href="https://wa.me/77770650260">+7 777 065 02 60</a></li><li><a href="mailto:asferia@mail.ru">asferia@mail.ru</a></li></ul></div>
<div><h5>{ft["social"]}</h5><ul><li><a href="https://www.instagram.com/asferia_adventure/">Instagram</a></li><li><a href="https://t.me/asferiakazakhstan">Telegram</a></li><li><a href="https://wa.me/77770650260">WhatsApp</a></li></ul></div>
</div><div class="footer-bottom"><div>{ft["copy"]}</div><div class="made">{ft["place"]}</div></div><div class="legal">{LEGAL["ru" if lang in ("ru", "kk") else "en"]}</div></div></footer>
<div class="lightbox" id="lightbox"><button class="lightbox-close">✕</button><img id="lightbox-img" src="" alt=""></div>
<script src="{R}js/site.js" defer></script>
</body></html>
'''

def feats(items):
    return '<div class="features-grid three reveal-stagger">' + ''.join(f'<div class="feature"><span class="num">{i + 1:02d}</span><h3>{t}</h3><p>{p}</p></div>' for i, (t, p) in enumerate(items)) + '</div>'

def home(c, lang, R):
    P = PATHS[lang]; W = SEASON_MODE == 'winter' and 'winter_home' in c
    o = hero(dict(c['winter_home']['hero'] if W else c['hero'], cta2_href='#winter' if W else '#seasons'), 'home', R)
    st = ''
    for n, l, d in c['stats']:
        num = f'<span class="counter" data-to="{n}">0</span>' if n.isdigit() and len(n) < 4 else f'<span class="num-text">{n}</span>'
        st += f'<div class="stat"><div class="num">{num}</div><div class="label">{l}</div><div class="detail">{d}</div></div>'
    o += f'<section class="stats"><div class="container"><div class="stats-grid reveal-stagger">{st}</div></div></section>\n'
    s = c['seasons']
    def season(x, page, btn):
        when = ''.join(f'<span class="pill">{w}</span>' for w in x['when'])
        fine = f'<p class="fine">{x["fine"]}</p>' if x.get('fine') else ''
        items = ''.join(f'<li>{i}</li>' for i in x['items'])
        return f'''<article class="season"><div class="card-bg" style="background-image:url('{R}{HERO[page]}')"></div><div class="scrim"></div><div class="when">{when}</div><h3>{x["title"]}</h3><ul>{items}</ul>{fine}<a href="{R}{P[page]}" class="btn {btn}">{x["cta"]} <span class="arrow">→</span></a></article>'''
    o += f'<section class="section" id="seasons"><div class="container">{sec_head(s)}<div class="seasons reveal-stagger">{season(s["summer"], "summer", "btn--tan")}{season(s["winter"], "winter", "btn--ghost")}</div></div></section>\n'
    if W:
        o += winter_block(c, lang, R)
    j = dict(c['journey'], **c['winter_home'].get('journey', {})) if W else c['journey']; cls = ['s-a', 's-b', 's-c', 's-d', 's-e']
    stops = ''.join(card(R, STOPS[i], p, t, d, cls=cls[i]) for i, (p, t, d) in enumerate(j['stops']))
    k = j['cta']; pills = ''.join(f'<span>{x}</span>' for x in k['pills'])
    stops += f'<div class="stop-cta s-cta"><div class="eyebrow">{k["eyebrow"]}</div><h3>{k["h3"]}</h3><div class="day-pills">{pills}</div><p>{k["p"]}</p><div class="ctas"><a href="#booking" class="btn btn--tan">{k["btn"]} <span class="arrow">→</span></a></div><div class="price-line">{k["price"]}</div></div>'
    o += f'<section class="section" id="journey" style="padding-top:40px;"><div class="container">{sec_head(j)}<div class="stops reveal-stagger">{stops}</div></div></section>\n'
    r = c['route']
    days = ''.join(f'<div class="day"><div class="d-num">{r["dayword"].format(i + 1)}</div><h4>{t}</h4><p>{p}</p></div>' for i, (t, p) in enumerate(r['days']))
    days += f'<div class="day sum"><div class="big">{r["sum"][0]}</div><div class="small">{r["sum"][1]}</div><p>{r["sum"][2]}</p></div>'
    o += f'<section class="section tight" id="example"><div class="container">{sec_head(r)}<div class="route-grid reveal-stagger">{days}</div><div class="route-note">{r["note"]}</div></div></section>\n'
    b = c['band']
    o += f'<section class="band"><div class="band-bg"></div><div class="container"><div class="eyebrow reveal">{b["eyebrow"]}</div><h2 class="reveal">{b["h2"]}</h2></div></section>\n'
    v = c['services']; stays = ''
    for (f, n), cap in zip(STAYS, v['stays']):
        ttl = n or cap.split(',')[0]; rest = cap if n else ','.join(cap.split(',')[1:]).strip()
        stays += f'<figure class="stay"><img src="{R}assets/pilot/{f}" alt="{ttl} — {cap}" loading="lazy"><figcaption><b>{ttl}</b>{rest}</figcaption></figure>'
    o += f'<section class="section" id="services"><div class="container">{sec_head(v)}{feats(v["items"])}<p class="arrange-foot reveal">{v["foot"]}</p><div class="stay-head reveal"><div><div class="eyebrow">{v["stay_eyebrow"]}</div><h3>{v["stay_h3"]}</h3></div><p>{v["stay_p"]}</p></div><div class="stay-grid reveal-stagger">{stays}</div></div></section>\n'
    h = c['how']; steps = ''.join(f'<div class="step"><div class="s-num">{i + 1:02d}</div><h3>{t}</h3><p>{p}</p></div>' for i, (t, p) in enumerate(h['steps']))
    o += f'<section class="section" id="how" style="padding-top:40px;"><div class="container">{sec_head(h)}<div class="steps reveal-stagger">{steps}</div></div></section>\n'
    g = c['gallery']; gc = ['g-tall', '', '', 'g-tall', 'g-wide', '', 'g-wide', '']
    gi = ''.join(f'<div class="g-item {gc[i]}"><img src="{R}assets/photo-gallery-{i + 1:02d}.jpg" alt="{g["alt"]} {i + 1}" loading="lazy"></div>' for i in range(8))
    o += f'<section class="section" id="gallery"><div class="container">{sec_head(g)}<div class="gallery reveal-stagger">{gi}</div></div></section>\n'
    a = c['about']; ps = ''.join(f'<p>{p}</p>' for p in a['ps']); team = ''
    for (im, pos), (nm, role, since) in zip(TEAM, a['team']):
        team += f'''<div class="member"><div class="photo-ring"><div class="photo" style="background-image:url('{R}assets/{im}');background-size:cover;background-position:{pos};"></div></div><h4>{nm}</h4><div class="role">{role}</div><div class="since">{since}</div></div>'''
    o += f'''<section class="section" id="about"><div class="container"><div class="about-grid"><div class="about-text reveal reveal-l"><div class="eyebrow">{a["eyebrow"]}</div><h2>{a["h2"]}</h2>{ps}
<div class="signature"><div class="ava" style="background-image:url('{R}assets/photo-ivandirector.jpg');background-size:cover;background-position:center;"></div><div class="who"><b>{a["founder"][0]}</b><span>{a["founder"][1]}</span></div></div></div>
<div class="about-photo reveal reveal-r"><img src="{R}assets/photo-team.jpg" alt="Asferia Adventure" loading="lazy"><div class="photo-tag"><b>{a["tag"][0]}</b>{a["tag"][1]}</div></div></div>
<div class="team-grid reveal-stagger" style="margin-top:80px;">{team}</div></div></section>
'''
    q = c['faq']; qs = ''.join(f'<details><summary>{x}</summary><p>{y}</p></details>' for x, y in q['items'])
    o += f'<section class="section" id="faq" style="padding-top:40px;"><div class="container">{sec_head(q)}<div class="faq reveal">{qs}</div></div></section>\n'
    bl = dict(c['blog'], cards=latest_cards(lang) or c['blog']['cards'])
    cards = ''.join(f'<a class="jcard" href="{R}{u}"><div class="im"><img src="{R}{im}" alt="{t}" loading="lazy"></div><div class="tx"><div class="tg">{tg}</div><div class="tt">{t}</div><div class="rd">{bl["read"]} →</div></div></a>' for u, im, tg, t in bl['cards'])
    o += f'<section class="section" id="journal" style="background:#161616;border-top:1px solid rgba(245,239,230,0.06);"><div class="container">{sec_head(bl)}<div class="journal-grid reveal-stagger">{cards}</div><div style="text-align:center;margin-top:40px;"><a href="{R}{c["blog_url"]}" class="btn btn--ghost">{bl["all"]} <span class="arrow">→</span></a></div></div></section>\n'
    return o

def summer(c, lang, R):
    s = c['summer']; P = PATHS[lang]; T = TOURS[lang]
    o = hero(s['hero'], 'summer', R, short=True)
    t = s['tailor']
    o += f'<section class="section" id="tailor"><div class="container"><div class="split">{sec_head(t)}<div class="stop-cta reveal"><div class="eyebrow">{t["box_eyebrow"]}</div><h3>{t["box_h3"]}</h3><p>{t["box_p"]}</p><div class="ctas"><a href="{R}{P["home"]}#journey" class="btn btn--tan">{t["btn"]} <span class="arrow">→</span></a></div><div class="price-line">{t["price"]}</div></div></div></div></section>\n'
    d = s['day']
    cards = ''.join(card(R, img, price(c, pr), tt, ds, href=T[k] if k else None, pillcls='price') for (k, img, pr), (tt, ds) in zip(DAY, d['cards']))
    o += f'<section class="section" id="day" style="padding-top:40px;"><div class="container">{sec_head(d)}<div class="cards reveal-stagger">{cards}</div><p class="note-line">{d["note"]}</p></div></section>\n'
    def rows(x, prices, keys=None):
        out = ''
        for i, (tt, ds) in enumerate(x['rows']):
            k = keys[i] if keys else None
            ttl = f'<a href="{R}{T[k]}">{tt} →</a>' if k else tt
            out += f'<div class="row"><h3>{ttl}</h3><p>{ds}</p><div class="pr">{price(c, prices[i])}</div></div>'
        return f'<div class="rows reveal">{out}</div>'
    m = s['multi']
    o += f'<section class="section" id="multi" style="padding-top:40px;"><div class="container">{sec_head(m)}{rows(m, [p for _, p in MULTI], [k for k, _ in MULTI])}</div></section>\n'
    a = s['act']
    o += f'<section class="section" id="activities" style="padding-top:40px;"><div class="container">{sec_head(a)}{rows(a, ACT)}<p class="note-line">{a["note"]}</p></div></section>\n'
    return o

def winter(c, lang, R):
    w = c['winter']
    o = hero(w['hero'], 'winter', R, short=True)
    # Две программы
    cards = ''
    for x, img in zip(w['cards'], WINTER_SLOTS):
        items = ''.join(f'<li>{i}</li>' for i in x['items'])
        extra = f'<p class="fine">{x["extra"]}</p>' if x.get('extra') else ''
        cards += f'''<article class="season"><div class="card-bg" style="background-image:url('{R}{img}')"></div><div class="scrim"></div><div class="when"><span class="pill">{x["pill"]}</span><span class="pill">{x["meta"]}</span></div><h3>{x["title"]}</h3><ul>{items}</ul><div class="w-price"><b>{x["price"]}</b><span>{x["price_note"]}</span></div>{extra}<a href="#booking" class="btn btn--tan">{w["cta"]} <span class="arrow">→</span></a></article>'''
    o += f'<section class="section" id="programs"><div class="container">{sec_head(w["intro"])}<div class="seasons reveal-stagger">{cards}</div></div></section>\n'
    fr = w.get('freeride_cta')
    if fr:
        o += f'<section class="section tight" style="padding-top:0;"><div class="container"><div class="stop-cta fr-cta reveal"><div><div class="eyebrow">{fr["eyebrow"]}</div><h3>{fr["h3"]}</h3><p>{fr["p"]}</p></div><a href="{R}{PATHS[lang]["freeride"]}" class="btn btn--tan">{fr["btn"]} <span class="arrow">→</span></a></div></div></section>\n'
    # Видео и фото. Клип: положить assets/v2/winter-clip.mp4 и пересобрать. Фото: assets/v2/winter-01…06.jpg, пересборка не нужна.
    m = w['media']
    poster = f"{R}{HERO['winter']}"
    if os.path.exists(os.path.join(ROOT, 'assets/v2/winter-clip.mp4')):
        video = f'<div class="media-video reveal"><video controls playsinline preload="metadata" poster="{poster}"><source src="{R}assets/v2/winter-clip.mp4" type="video/mp4"></video></div>'
    else:
        video = f'''<div class="media-video soon reveal"><div class="card-bg" style="background-image:url('{poster}')"></div><div class="scrim"></div><div class="play"></div><div class="media-label">{m["video_soon"]}</div></div>'''
    tiles = ''.join(f'''<div class="m-tile"><div class="m-ph"><span>{m["photo_soon"]}</span></div><div class="card-bg" style="background-image:url('{R}assets/v2/winter-{i:02d}.jpg')"></div></div>''' for i in range(1, 7))
    o += f'<section class="section" id="media" style="padding-top:40px;"><div class="container">{sec_head(m)}{video}<div class="media-grid reveal-stagger">{tiles}</div></div></section>\n'
    # Как проходит выезд
    r = w['route']
    days = ''.join(f'<div class="day"><div class="d-num">{n}</div><h4>{t}</h4><p>{p}</p></div>' for n, t, p in r['steps'])
    days += f'<div class="day sum"><div class="big">{r["sum"][0]}</div><div class="small">{r["sum"][1]}</div><p>{r["sum"][2]}</p></div>'
    o += f'<section class="section tight" id="route"><div class="container">{sec_head(r)}<div class="route-grid three reveal-stagger">{days}</div></div></section>\n'
    # Цена и что входит
    p = w['pricing']
    inc = ''.join(f'<li>{i}</li>' for i in p['inc'])
    o += f'<section class="section" id="pricing" style="padding-top:40px;"><div class="container"><div class="split">{sec_head(p)}<div class="stop-cta reveal"><div class="eyebrow">{p["inc_title"]}</div><ul class="inc">{inc}</ul><div class="price-line">{p["extra"]}</div></div></div></div></section>\n'
    # Короткие плашки
    notes = ''.join(f'<div class="note-card"><h4>{t}</h4><p>{d}</p></div>' for t, d in w['notes'])
    o += f'<section class="section" id="notes" style="padding-top:0;"><div class="container"><div class="notes reveal-stagger">{notes}</div></div></section>\n'
    return o

def media_block(m, R, prefix, poster, sid='media'):
    # Клип: assets/v2/<prefix>-clip.mp4 (нужна пересборка). Фото: assets/v2/<prefix>-01…06.jpg (встают сами).
    if os.path.exists(os.path.join(ROOT, f'assets/v2/{prefix}-clip.mp4')):
        video = f'<div class="media-video reveal"><video controls playsinline preload="metadata" poster="{poster}"><source src="{R}assets/v2/{prefix}-clip.mp4" type="video/mp4"></video></div>'
    else:
        video = f'''<div class="media-video soon reveal"><div class="card-bg" style="background-image:url('{poster}')"></div><div class="scrim"></div><div class="play"></div><div class="media-label">{m["video_soon"]}</div></div>'''
    tiles = ''.join(f'''<div class="m-tile"><div class="m-ph"><span>{m["photo_soon"]}</span></div><div class="card-bg" style="background-image:url('{R}assets/v2/{prefix}-{i:02d}.jpg')"></div></div>''' for i in range(1, 7))
    return f'<section class="section" id="{sid}" style="padding-top:40px;"><div class="container">{sec_head(m)}{video}<div class="media-grid reveal-stagger">{tiles}</div></div></section>\n'

def winter_block(c, lang, R):
    b = c['winter_home']['block']; P = PATHS[lang]
    imgs = ['assets/v2/winter-catski.jpg', 'assets/v2/winter-snowmobile.jpg', _slot('assets/v2/freeride-card.jpg', 'assets/pilot/season-winter.jpg')]
    cards = ''
    for (pill, title, desc, page), img in zip(b['cards'], imgs):
        cards += f'''<a href="{R}{P[page]}" class="tour-card"><div class="m-ph"><span>{b["soon"]}</span></div><div class="card-bg" style="background-image:url('{R}{img}')"></div><div class="scrim"></div><div class="corners"><span class="pill price">{pill}</span></div><div class="tour-info"><h3>{title}</h3><div class="desc long">{desc}</div></div></a>'''
    return f'<section class="section" id="winter"><div class="container">{sec_head(b)}<div class="cards eq3 reveal-stagger">{cards}</div><div style="margin-top:28px;"><a href="{R}{P["winter"]}" class="btn btn--ghost">{b["more"]} <span class="arrow">→</span></a></div></div></section>\n'

def freeride(c, lang, R):
    f = c['freeride']
    o = hero(f['hero'], 'freeride', R, short=True)
    # Два вида заброски (по программам партнёра)
    cards = ''
    for x, key in zip(f['cards'], ('sled', 'cat')):
        items = ''.join(f'<li>{i}</li>' for i in x['items'])
        img = _slot(f'assets/v2/freeride-{key}.jpg', {'cat': 'assets/v2/winter-catski.jpg', 'sled': 'assets/v2/winter-snowmobile.jpg'}[key])
        cards += f'''<article class="season"><div class="card-bg" style="background-image:url('{R}{img}')"></div><div class="scrim"></div><div class="when"><span class="pill">{x["pill"]}</span><span class="pill">{x["meta"]}</span></div><h3>{x["title"]}</h3><ul>{items}</ul><div class="w-price"><b>{x["price"]}</b><span>{x["price_note"]}</span></div><a href="#packages" class="btn btn--tan">{f["cta_tours"]} <span class="arrow">→</span></a></article>'''
    o += f'<section class="section" id="programs"><div class="container">{sec_head(f["intro"])}<div class="seasons reveal-stagger">{cards}</div></div></section>\n'
    # Туры «всё включено»
    pk = f['packages']; boxes = ''
    for b in pk['tours']:
        inc = ''.join(f'<li>{i}</li>' for i in b['inc'])
        rows = ''.join(f'<div class="pk-row"><span>{n}</span><b>{p}</b></div>' for n, p in b['prices'])
        boxes += f'<div class="pk reveal"><div class="eyebrow">{b["eyebrow"]}</div><h3>{b["title"]}</h3><ul class="inc">{inc}</ul><div class="pk-meta">{b["meta"]}</div><div class="pk-prices">{rows}</div><a href="#booking" class="btn btn--tan">{f["cta"]} <span class="arrow">→</span></a></div>'
    o += f'<section class="section" id="packages" style="padding-top:40px;"><div class="container">{sec_head(pk)}<div class="pk-grid">{boxes}</div><p class="note-line">{pk["note"]}</p></div></section>\n'
    # Пример расписания
    sc = f['schedule']
    days = ''.join(f'<div class="day"><div class="d-num">{n}</div><h4>{t}</h4><p>{p}</p></div>' for n, t, p in sc['days'])
    o += f'<section class="section tight" id="schedule"><div class="container">{sec_head(sc)}<div class="route-grid three reveal-stagger">{days}</div><div class="route-note">{sc["note"]}</div></div></section>\n'
    wh = f['why']
    o += f'<section class="section" id="why" style="padding-top:40px;"><div class="container">{sec_head(wh)}{feats(wh["items"])}</div></section>\n'
    o += media_block(f['media'], R, 'freeride', f'{R}{HERO["freeride"]}')
    q = f['faq']; qs = ''.join(f'<details><summary>{x}</summary><p>{y}</p></details>' for x, y in q['items'])
    o += f'<section class="section" id="faq" style="padding-top:40px;"><div class="container">{sec_head(q)}<div class="faq reveal">{qs}</div></div></section>\n'
    return o

def trips_ld(c, lang, page):
    # Разметка TouristTrip с ценами — для поисковиков
    def num(s): return int(re.sub(r'\D', '', s) or 0)
    def txt(s): return re.sub(r'<[^>]+>', ' ', s).replace('  ', ' ').strip()
    url = canon(lang, page); out = []
    if page == 'winter':
        for x in c['winter']['cards']:
            out.append((txt(x['title']), txt(' '.join(x['items'])), num(x['price'])))
    if page == 'freeride':
        for b in c['freeride']['packages']['tours']:
            for n, p in b['prices']:
                out.append((f'{txt(b["eyebrow"])} — {txt(b["title"])} — {n}', txt('; '.join(b['inc'])), num(p)))
    items = [{"@context": "https://schema.org", "@type": "TouristTrip", "name": n, "description": d,
              "provider": {"@type": "TravelAgency", "name": "Asferia Adventure", "url": BASE},
              "offers": {"@type": "Offer", "price": p, "priceCurrency": "KZT", "url": url, "availability": "https://schema.org/InStock"}} for n, d, p in out if p]
    return ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in items)

BODY = {'home': home, 'summer': summer, 'winter': winter, 'freeride': freeride}

# ===================== БЛОГ =====================
# Статьи: build/blog/<ru|en|zh>/<slug>.md (новые) или .html (перенесённые старые).
# В шапке статьи: title, description, date (публикуется, когда date <= сегодня), tag, cta (winter|freeride|summer|home|none),
# draft: yes (не публиковать), photo: имя.jpg | что снять (для заглушек), alt_en / alt_ru / alt_zh: slug перевода.
import datetime, html as _html
from PIL import Image, ImageDraw, ImageFont

BLOG_DIR = os.path.join(ROOT, 'build', 'blog')
BLOG_URL = {'ru': 'blog/{}.html', 'en': 'blog/en/{}.html', 'zh': 'blog/zh/{}.html'}
BLOG_IMG = {'ru': 'assets/blog/{}', 'en': 'assets/blog/en/{}', 'zh': 'assets/blog/zh/{}'}
TODAY = datetime.date.today()
MONTHS = {'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'],
          'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}
_POSTS = None

def fmt_date(d, lang):
    if lang == 'zh': return f'{d.year}年{d.month}月{d.day}日'
    return f'{d.day} {MONTHS.get(lang, MONTHS["ru"])[d.month - 1]} {d.year}'

def parse_post(path, lang):
    s = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n(.*)', s, re.S)
    meta = {'photos': []}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':'); k = k.strip(); v = v.strip()
        if not k: continue
        if k == 'photo':
            n, _, d = v.partition('|'); meta['photos'].append((n.strip(), d.strip()))
        else: meta[k] = v
    body = m.group(2); ld = ''
    if '<!--LD-->' in body: body, ld = body.split('<!--LD-->', 1)
    slug = os.path.splitext(os.path.basename(path))[0]
    meta.update(slug=slug, lang=lang, body=body, ld=ld, fmt='html' if path.endswith('.html') else 'md',
                url=BLOG_URL[lang].format(slug), img_dir=meta.get('img_dir') or BLOG_IMG[lang].format(slug))
    meta['date_obj'] = datetime.date.fromisoformat(meta['date'])
    meta['hero'] = meta.get('hero') or 'hero.jpg'
    if meta['hero'].startswith('assets/'): meta['hero_path'] = meta['hero']
    else: meta['hero_path'] = meta['img_dir'] + '/' + meta['hero']
    meta['published'] = meta.get('draft') != 'yes' and meta['date_obj'] <= TODAY
    return meta

def get_posts():
    global _POSTS
    if _POSTS is None:
        _POSTS = []
        for lang in ('ru', 'en', 'zh'):
            d = os.path.join(BLOG_DIR, lang)
            if not os.path.isdir(d): continue
            for f in sorted(os.listdir(d)):
                if f.endswith(('.md', '.html')): _POSTS.append(parse_post(os.path.join(d, f), lang))
        _POSTS.sort(key=lambda p: p['date_obj'], reverse=True)
    return _POSTS

def latest_cards(lang, n=3):
    L = 'ru' if lang == 'kk' else lang
    ps = [p for p in get_posts() if p['published'] and p['lang'] == L][:n]
    if len(ps) < n and L == 'zh': ps += [p for p in get_posts() if p['published'] and p['lang'] == 'en'][:n - len(ps)]
    return [[p['url'], p['hero_path'], p.get('tag', ''), p['title']] for p in ps]

# ---------- заглушки ----------
def _font(size):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def make_placeholder(path, name, desc):
    W, H = 1600, 900
    im = Image.new('RGB', (W, H), (58, 62, 66)); d = ImageDraw.Draw(im)
    for x in range(-H, W, 60): d.line([(x, H), (x + H, 0)], fill=(64, 68, 72), width=18)
    d.rectangle([40, 40, W - 40, H - 40], outline=(201, 165, 126), width=3)
    d.text((90, 100), 'ЗАГЛУШКА · ЗАМЕНИТЬ ФОТО', font=_font(34), fill=(201, 165, 126))
    d.text((90, 160), name, font=_font(96), fill=(245, 239, 230))
    words, lines, cur = desc.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=_font(44)) > W - 200: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    for i, l in enumerate(lines[:7]): d.text((90, 320 + i * 62), l, font=_font(44), fill=(220, 214, 205))
    d.text((90, H - 120), 'Горизонтальное, от 1600 px по ширине. Положите фото с этим же именем.', font=_font(30), fill=(160, 160, 160))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, 'JPEG', quality=80)

def ensure_placeholders(p):
    made = 0
    for name, desc in p['photos']:
        f = os.path.join(ROOT, p['img_dir'], name)
        if not os.path.exists(f): make_placeholder(f, name, desc); made += 1
    if p['photos']:
        txt = os.path.join(ROOT, p['img_dir'], 'ЧТО-СЮДА.txt')
        open(txt, 'w', encoding='utf-8').write(f'Статья: {p["title"]}\nСтраница: {p["url"]}\n\n' + '\n'.join(f'{n} — {d}' for n, d in p['photos']) +
            '\n\nВсе фото горизонтальные, от 1600 px по ширине, JPEG. Замените файл с тем же именем — пересборка не нужна.\n')
    return made

# ---------- текст статьи ----------
def _inline(t, R):
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    def link(m):
        u = m.group(2)
        if u.startswith('/'): u = R + u[1:]
        return f'<a href="{u}">{m.group(1)}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, t)

def md_to_html(p, R):
    out, faq = [], []
    for block in re.split(r'\n\s*\n', p['body'].strip()):
        lines = block.strip().split('\n'); first = lines[0]
        if first.startswith('### '): out.append(f'<h3>{_inline(first[4:], R)}</h3>' + ''.join(f'<p>{_inline(l, R)}</p>' for l in lines[1:]))
        elif first.startswith('## '): out.append(f'<h2>{_inline(first[3:], R)}</h2>' + ''.join(f'<p>{_inline(l, R)}</p>' for l in lines[1:]))
        elif first.startswith('- '): out.append('<ul>' + ''.join(f'<li>{_inline(l[2:], R)}</li>' for l in lines) + '</ul>')
        elif first.startswith('%% '):
            cells = ''.join(f'<div class="fact-card"><div class="fc-label">{a.strip()}</div><div class="fc-value">{_inline(b.strip(), R)}</div></div>' for a, _, b in (l[3:].partition('|') for l in lines))
            out.append(f'<div class="fact-grid">{cells}</div>')
        elif first.startswith('!['):
            m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', first)
            src = m.group(2) if m.group(2).startswith('assets/') else p['img_dir'] + '/' + m.group(2)
            out.append(f'<figure class="article-photo"><img src="{R}{src}" alt="{_html.escape(m.group(1))}" loading="lazy"><figcaption>{m.group(1)}</figcaption></figure>')
        elif first.startswith('Q: '):
            q = first[3:]; a = ' '.join(l[3:] if l.startswith('A: ') else l for l in lines[1:])
            faq.append((q, a)); out.append(f'<details class="art-faq"><summary>{q}</summary><p>{_inline(a, R)}</p></details>')
        elif first.startswith('> '): out.append(f'<blockquote>{_inline(" ".join(l[2:] for l in lines), R)}</blockquote>')
        else: out.append(f'<p>{_inline(" ".join(lines), R)}</p>')
    return '\n'.join(out), faq

def read_minutes(text, lang):
    t = re.sub(r'<[^>]+>', ' ', text)
    n = len(re.sub(r'\s', '', t)) / 500 if lang == 'zh' else len(t.split()) / 180
    return max(2, round(n))

# ---------- страницы ----------
def blog_head(c, lang, p, R, title, desc, canon_url, image, alts, ld):
    hl = {'ru': 'ru', 'en': 'en', 'zh': 'zh-Hans'}
    alt_links = ''.join(f'<link rel="alternate" hreflang="{hl[l]}" href="{u}">\n' for l, u in alts)
    fam = '' if lang == 'zh' else '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">\n'
    return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(title)}</title>
<meta name="description" content="{_html.escape(desc)}">
<link rel="canonical" href="{canon_url}">
{alt_links}<meta name="geo.region" content="KZ-VOS">
<meta property="og:type" content="{"article" if p else "website"}">
<meta property="og:site_name" content="Asferia Adventure">
<meta property="og:title" content="{_html.escape(title)}">
<meta property="og:description" content="{_html.escape(desc)}">
<meta property="og:url" content="{canon_url}">
<meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/x-icon" href="{R}assets/favicon/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="{R}assets/favicon/favicon-180.png">
<meta name="theme-color" content="#1F1F1F">
{ld}{fam}<link rel="stylesheet" href="{R}css/site.css">
</head>
<body>
{METRIKA}
'''

def article_page(c, p, R):
    lang = p['lang']; ui = c['blogui']; P = PATHS[lang]
    if p['fmt'] == 'md': body, faq = md_to_html(p, R)
    else: body, faq = p['body'], []
    url = BASE + p['url']
    alts = [(lang, url)] + [(l, BASE + BLOG_URL[l].format(p['alt_' + l])) for l in ('ru', 'en', 'zh') if p.get('alt_' + l)]
    ld = p['ld']
    if p['fmt'] == 'md':
        art = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p['title'], "description": p['description'],
               "image": BASE + p['hero_path'], "datePublished": p['date'], "dateModified": p.get('updated', p['date']), "inLanguage": HTML_LANG[lang],
               "author": {"@type": "Organization", "name": "Asferia Adventure", "url": BASE},
               "publisher": {"@type": "Organization", "name": "Asferia Adventure", "logo": {"@type": "ImageObject", "url": BASE + "assets/favicon/favicon-512.png"}},
               "mainEntityOfPage": url}
        ld = f'<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>\n'
        if faq:
            ld += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', a)}} for q, a in faq]}, ensure_ascii=False) + '</script>\n'
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Asferia Adventure", "item": canon(lang, 'home')},
        {"@type": "ListItem", "position": 2, "name": ui['blog'], "item": canon(lang, 'blog')},
        {"@type": "ListItem", "position": 3, "name": p['title'], "item": url}]}
    ld += f'<script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>\n'
    o = blog_head(c, lang, p, R, p.get('seo_title', p['title']) + ' | Asferia Adventure', p['description'], url, p['hero_path'], alts, ld) + nav(c, lang, 'blog', R)
    mins = read_minutes(body, lang)
    o += f'''<header class="hero hero--short art-hero" id="top"><div class="hero-bg" id="heroBg" style="background-image:url('{R}{p["hero_path"]}')"></div>
<div class="container hero-content"><div class="crumbs reveal"><a href="{R}{P["home"]}">Asferia</a> / <a href="{R}{P["blog"]}">{ui["blog"]}</a></div>
<div class="eyebrow reveal">{p.get("tag", "")}</div><h1 class="reveal art-h1" id="heroHeadline">{p.get("h1", p["title"])}</h1>
<div class="art-meta reveal">{fmt_date(p["date_obj"], lang)} · {mins} {ui["min"]}</div></div></header>
<main class="section art-section"><div class="container"><article class="art">{body}</article>
'''
    cta = p.get('cta', 'home')
    if cta != 'none':
        k = ui['cta'][cta]
        o += f'<div class="stop-cta fr-cta art-cta"><div><div class="eyebrow">{k["eyebrow"]}</div><h3>{k["h3"]}</h3><p>{k["p"]}</p></div><a href="{R}{P[cta]}" class="btn btn--tan">{k["btn"]} <span class="arrow">→</span></a></div>'
    rel = [q for q in get_posts() if q['published'] and q['lang'] == lang and q['slug'] != p['slug']][:3]
    if rel:
        cards = ''.join(f'<a class="jcard" href="{R}{q["url"]}"><div class="im"><img src="{R}{q["hero_path"]}" alt="" loading="lazy"></div><div class="tx"><div class="tg">{q.get("tag", "")}</div><div class="tt">{q["title"]}</div><div class="rd">{ui["read"]} →</div></div></a>' for q in rel)
        o += f'<div class="art-related"><div class="eyebrow">{ui["related"]}</div><div class="journal-grid">{cards}</div></div>'
    o += '</div></main>\n'
    return o + contact_footer(c, lang, R)

def blog_index(c, lang, R, posts):
    ui = c['blogui']; P = PATHS[lang]
    alts = [(l, canon(l, 'blog')) for l in ('ru', 'en', 'zh')]
    ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Blog", "name": ui['index_title'], "url": canon(lang, 'blog'),
        "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": BASE + p['url'], "datePublished": p['date']} for p in posts[:20]]}, ensure_ascii=False) + '</script>\n'
    hero_img = posts[0]['hero_path'] if posts else HERO['home']
    o = blog_head(c, lang, None, R, ui['index_title'], ui['index_desc'], canon(lang, 'blog'), hero_img, alts, ld) + nav(c, lang, 'blog', R)
    o += f'''<header class="hero hero--short art-hero" id="top"><div class="hero-bg" id="heroBg" style="background-image:url('{R}{hero_img}')"></div>
<div class="container hero-content"><div class="eyebrow reveal">{ui["index_eyebrow"]}</div><h1 class="reveal art-h1" id="heroHeadline">{ui["index_h1"]}</h1><p class="sub reveal">{ui["index_sub"]}</p></div></header>
'''
    def grid(ps):
        return '<div class="journal-grid reveal-stagger">' + ''.join(f'<a class="jcard" href="{R}{p["url"]}"><div class="im"><img src="{R}{p["hero_path"]}" alt="" loading="lazy"></div><div class="tx"><div class="tg">{p.get("tag", "")} · {fmt_date(p["date_obj"], p["lang"])}</div><div class="tt">{p["title"]}</div><div class="rd">{ui["read"]} →</div></div></a>' for p in ps) + '</div>'
    o += f'<section class="section"><div class="container">{grid([p for p in posts if p["lang"] == lang])}'
    if lang == 'zh':
        o += f'<div class="art-related"><div class="eyebrow">{ui["en_articles"]}</div>{grid([p for p in posts if p["lang"] == "en"])}</div>'
    o += '</div></section>\n'
    return o + contact_footer(c, lang, R)

def build_blog():
    urls = []; posts = get_posts(); made = 0
    for p in posts: made += ensure_placeholders(p)
    pub = [p for p in posts if p['published']]
    C = {l: json.load(open(os.path.join(ROOT, 'build/content', l + '.json'), encoding='utf-8')) for l in ('ru', 'en', 'zh')}
    for p in pub:
        R = '../' * p['url'].count('/')
        open(os.path.join(ROOT, p['url']), 'w', encoding='utf-8').write(article_page(C[p['lang']], p, R)); urls.append(BASE + p['url'])
    for l in ('ru', 'en', 'zh'):
        path = PATHS[l]['blog']; R = '../' * path.count('/')
        os.makedirs(os.path.dirname(os.path.join(ROOT, path)) or ROOT, exist_ok=True)
        open(os.path.join(ROOT, path), 'w', encoding='utf-8').write(blog_index(C[l], l, R, pub)); urls.append(canon(l, 'blog'))
    print(f'blog: опубликовано {len(pub)}, ждут даты {len([p for p in posts if not p["published"]])}, новых заглушек {made}')
    plan = os.path.join(ROOT, 'build', 'blog', 'ПЛАН.txt')
    open(plan, 'w', encoding='utf-8').write('Дата        | Язык | Статус       | Статья\n' + '\n'.join(
        f'{p["date"]}  | {p["lang"]}   | {"опубликована" if p["published"] else ("черновик" if p.get("draft") == "yes" else "ждёт даты")} | {p["title"]}  ({p["url"]})'
        for p in sorted(posts, key=lambda p: p['date_obj'])) + '\n')
    return urls


def main():
    urls = []
    for lang in LANGS:
        c = json.load(open(os.path.join(ROOT, 'build/content', lang + '.json'), encoding='utf-8'))
        for page in ('home', 'summer', 'winter', 'freeride'):
            path = PATHS[lang][page]; R = '../' * path.count('/')
            out = head(c, lang, page, R) + nav(c, lang, page, R) + BODY[page](c, lang, R) + booking(c, lang, page) + contact_footer(c, lang, R)
            full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
            open(full, 'w', encoding='utf-8').write(out); urls.append(canon(lang, page)); print('ok', path, len(out))
    urls += build_blog()
    sm = os.path.join(ROOT, 'sitemap.xml'); x = open(sm, encoding='utf-8').read()
    add = ''.join(f'  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>\n' for u in urls if f'<loc>{u}</loc>' not in x)
    open(sm, 'w', encoding='utf-8').write(x.replace('</urlset>', add + '</urlset>'))

main()
