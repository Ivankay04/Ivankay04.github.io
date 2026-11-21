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

