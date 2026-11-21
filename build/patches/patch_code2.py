#!/usr/bin/env python3
# Правка build.py: фрирайд по программам партнёра, сезонный блок на главной, разметка цен, og:image по странице.
import os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, '..', 'build.py')
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

# Новая функция фрирайда + разметка поездок
i = s.index('def freeride(c, lang, R):'); j = s.index('BODY = {')
s = s[:i] + open(os.path.join(D, 'freeride_fn2.py'), encoding='utf-8').read() + s[j:]

# Главная: сначала блок «Лето / Зима», затем (в зимнем режиме) три зимние карточки
rep("    if W:\n        o += winter_block(c, lang, R)\n    else:\n        o += f'<section class=\"section\" id=\"seasons\">",
    "    o += f'<section class=\"section\" id=\"seasons\">")
k = s.index("    o += f'<section class=\"section\" id=\"seasons\">"); e = s.index('\n', k)
s = s[:e + 1] + "    if W:\n        o += winter_block(c, lang, R)\n" + s[e + 1:]

# og:image — картинка самой страницы
rep('<meta property="og:image" content="{BASE}assets/photo-website-hero3.jpg">', '<meta property="og:image" content="{BASE}{HERO[page]}">')

# Разметка TouristTrip на зимней странице и фрирайде
rep("    return f'''<!DOCTYPE html>", "    if page in ('winter', 'freeride'):\n        ld += trips_ld(c, lang, page)\n    return f'''<!DOCTYPE html>")
open(p, 'w', encoding='utf-8').write(s)
print('build.py patched (2)')
