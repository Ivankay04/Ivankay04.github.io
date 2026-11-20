#!/usr/bin/env python3
# Одноразовая правка build.py: зимний режим главной, страница фрирайда, видео в шапке.
import os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build.py')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:70])
    s = s.replace(a, b)

# Пути
for lang, w, fr in (('ru', "'zima.html'", "'freeride.html'"), ('en', "'en/winter.html'", "'en/freeride.html'"),
                    ('zh', "'zh/winter.html'", "'zh/freeride.html'"), ('kk', "'kk/winter.html'", "'kk/freeride.html'")):
    rep(f"'winter': {w}}}", f"'winter': {w}, 'freeride': {fr}}}")

# Настройки сезона и цен
i = s.index('STOPS = [')
s = s[:i] + '''# ===== Сезон главной: 'winter' — с ноября по март, 'summer' — с апреля. Поменять и пересобрать.
SEASON_MODE = 'winter'
# ===== Цены фрирайда, ₸ за человека в день. 0 — на сайте «цена по запросу».
FREERIDE_PRICE = {'cat': 0, 'sled': 0}
def _slot(path, fallback):
    return path if os.path.exists(os.path.join(ROOT, path)) else fallback
HERO['freeride'] = _slot('assets/v2/freeride-hero.jpg', 'assets/v2/winter-catski.jpg')
if SEASON_MODE == 'winter':
    HERO['home'] = 'assets/pilot/season-winter.jpg'
''' + s[i:]

# Видео в шапке: assets/v2/hero-<page>.mp4 (home, winter, freeride)
rep('''<div class="hero-bg" id="heroBg" style="background-image:url('{R}{HERO[page]}')"></div>''',
    '''<div class="hero-bg" id="heroBg" style="background-image:url('{R}{HERO[page]}')">{hero_video(page, R)}</div>''')
i = s.index('def hero(')
s = s[:i] + '''def hero_video(page, R):
    v = f'assets/v2/hero-{page}.mp4'
    if not os.path.exists(os.path.join(ROOT, v)): return ''
    return f'<video autoplay muted loop playsinline preload="metadata" poster="{R}{HERO[page]}"><source src="{R}{v}" type="video/mp4"></video>'

''' + s[i:]

# Меню и подвал
rep('''{n["winter"]}</a><a href="{home}#journey">''', '''{n["winter"]}</a><a href="{R}{P["freeride"]}">{n["freeride"]}</a><a href="{home}#journey">''')
rep('''<li><a href="{R}{P["winter"]}">{n["winter"]}</a></li>''', '''<li><a href="{R}{P["winter"]}">{n["winter"]}</a></li><li><a href="{R}{P["freeride"]}">{n["freeride"]}</a></li>''')

# Микроразметка FAQ на странице фрирайда
rep("    return f'''<!DOCTYPE html>", '''    if page == 'freeride':
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', a)}} for q, a in c['freeride']['faq']['items']]}, ensure_ascii=False) + '</script>\\n'
    return f\'\'\'<!DOCTYPE html>''')

# Главная: зимний режим
rep("o = hero(dict(c['hero'], cta2_href='#seasons'), 'home', R)",
    "W = SEASON_MODE == 'winter' and 'winter_home' in c\n    o = hero(dict(c['winter_home']['hero'] if W else c['hero'], cta2_href='#winter' if W else '#seasons'), 'home', R)")
k = s.index("    o += f'<section class=\"section\" id=\"seasons\">")
e = s.index('\n', k)
line = s[k:e]
s = s[:k] + "    if W:\n        o += winter_block(c, lang, R)\n    else:\n    " + line + s[e:]
rep("    j = c['journey']; cls =", "    j = dict(c['journey'], **c['winter_home'].get('journey', {})) if W else c['journey']; cls =")

# Зимняя страница: переход к фрирайду
rep('''<div class="seasons reveal-stagger">{cards}</div></div></section>\\n\'
    # Видео и фото''', '''<div class="seasons reveal-stagger">{cards}</div></div></section>\\n\'
    fr = w.get('freeride_cta')
    if fr:
        o += f'<section class="section tight" style="padding-top:0;"><div class="container"><div class="stop-cta fr-cta reveal"><div><div class="eyebrow">{fr["eyebrow"]}</div><h3>{fr["h3"]}</h3><p>{fr["p"]}</p></div><a href="{R}{PATHS[lang]["freeride"]}" class="btn btn--tan">{fr["btn"]} <span class="arrow">→</span></a></div></div></section>\\n'
    # Видео и фото''')

# Новые функции
i = s.index('BODY = {')
s = s[:i] + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freeride_fn.py'), encoding='utf-8').read() + s[i:]
rep("BODY = {'home': home, 'summer': summer, 'winter': winter}", "BODY = {'home': home, 'summer': summer, 'winter': winter, 'freeride': freeride}")
rep("for page in ('home', 'summer', 'winter'):", "for page in ('home', 'summer', 'winter', 'freeride'):")
open(p, 'w', encoding='utf-8').write(s)
print('build.py patched')
