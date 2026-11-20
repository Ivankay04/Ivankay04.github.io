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
    imgs = ['assets/v2/winter-catski.jpg', 'assets/v2/winter-snowmobile.jpg', 'assets/v2/freeride-card.jpg']
    cards = ''
    for (pill, title, desc, page), img in zip(b['cards'], imgs):
        cards += f'''<a href="{R}{P[page]}" class="tour-card"><div class="m-ph"><span>{b["soon"]}</span></div><div class="card-bg" style="background-image:url('{R}{img}')"></div><div class="scrim"></div><div class="corners"><span class="pill price">{pill}</span></div><div class="tour-info"><h3>{title}</h3><div class="desc long">{desc}</div></div></a>'''
    return f'<section class="section" id="winter"><div class="container">{sec_head(b)}<div class="cards eq3 reveal-stagger">{cards}</div><div style="margin-top:28px;"><a href="{R}{P["winter"]}" class="btn btn--ghost">{b["more"]} <span class="arrow">→</span></a></div></div></section>\n'

def freeride(c, lang, R):
    f = c['freeride']
    o = hero(f['hero'], 'freeride', R, short=True)
    cards = ''
    for x, key in zip(f['cards'], ('cat', 'sled')):
        items = ''.join(f'<li>{i}</li>' for i in x['items'])
        pr = FREERIDE_PRICE.get(key)
        pstr = price(c, pr) if pr else f['price_request']
        cards += f'''<article class="season"><div class="m-ph"><span>{f["media"]["photo_soon"]}</span></div><div class="card-bg" style="background-image:url('{R}assets/v2/freeride-{key}.jpg')"></div><div class="scrim"></div><div class="when"><span class="pill">{x["pill"]}</span><span class="pill">{x["meta"]}</span></div><h3>{x["title"]}</h3><ul>{items}</ul><div class="w-price"><b>{pstr}</b><span>{x["price_note"]}</span></div><a href="#booking" class="btn btn--tan">{f["cta"]} <span class="arrow">→</span></a></article>'''
    o += f'<section class="section" id="programs"><div class="container">{sec_head(f["intro"])}<div class="seasons reveal-stagger">{cards}</div></div></section>\n'
    wk = f['week']
    days = ''.join(f'<div class="day"><div class="d-num">{n}</div><h4>{t}</h4><p>{p}</p></div>' for n, t, p in wk['steps'])
    days += f'<div class="day sum"><div class="big">{wk["sum"][0]}</div><div class="small">{wk["sum"][1]}</div><p>{wk["sum"][2]}</p></div>'
    o += f'<section class="section tight" id="week"><div class="container">{sec_head(wk)}<div class="route-grid three reveal-stagger">{days}</div><div class="route-note">{wk["note"]}</div></div></section>\n'
    sf = f['safety']
    o += f'<section class="section" id="safety" style="padding-top:40px;"><div class="container">{sec_head(sf)}{feats(sf["items"])}</div></section>\n'
    sc = f['school']
    rows = ''.join(f'<div class="row"><h3>{t}</h3><p>{d}</p><div class="pr">{pr}</div></div>' for t, d, pr in sc['rows'])
    o += f'<section class="section" id="school" style="padding-top:40px;"><div class="container">{sec_head(sc)}<div class="rows reveal">{rows}</div><p class="note-line">{sc["note"]}</p></div></section>\n'
    o += media_block(f['media'], R, 'freeride', f'{R}{HERO["freeride"]}')
    q = f['faq']; qs = ''.join(f'<details><summary>{x}</summary><p>{y}</p></details>' for x, y in q['items'])
    o += f'<section class="section" id="faq" style="padding-top:40px;"><div class="container">{sec_head(q)}<div class="faq reveal">{qs}</div></div></section>\n'
    return o

