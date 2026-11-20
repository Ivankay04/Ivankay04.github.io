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

