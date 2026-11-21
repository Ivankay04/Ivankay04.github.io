#!/usr/bin/env python3
# Обновляет две старые статьи: зимний раздел, новый заголовок, дата обновления.
import os, re, datetime
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog', 'ru')
T = datetime.date.today().isoformat()

WINTER_TURY = '''<h2>Зимой: ратрак, снегоходы и фрирайд</h2>
<p>С 10 декабря под Риддером работают зимние программы. Маршрут у выездов на ратраке и снегоходах один: подъём 10–15 км на перевал высотой около 2000 м, обзорные площадки, обед на гриле и горячий чай наверху. Около 4 часов в горах, 5–6 часов весь выезд из Риддера.</p>
<ul>
<li><strong>Ратрак</strong> — до 12 гостей в тёплом салоне, от 60 000 ₸ за человека в группе 10–12. Лыжи не нужны. <a href="ratrak-ridder.html">Подробнее о ратраке</a>.</li>
<li><strong>Снегоходы</strong> — 2–6 гостей, по двое на снегоходе, управляют наши гиды. От 80 000 ₸ за человека в группе 4–6. <a href="snegohody-ridder.html">Подробнее о снегоходах</a>.</li>
<li><strong>Фрирайд</strong> — для тех, кто катается: заброска на снегоходе или ратраке, туры на 3 дня катания и 4 ночи от 370 000 ₸. <a href="../freeride.html">Туры и цены</a>.</li>
</ul>
<p>Все зимние программы и бронирование — на странице <a href="../zima.html">«Зима»</a>.</p>
'''
WINTER_USK = '''<h2>Зимние выходные: декабрь — март</h2>
<p>Зимой из Усть-Каменогорска удобно ехать в Риддер на полдня в горы. Мы забираем гостей в Риддере, а из Усть-Каменогорска организуем трансфер по запросу.</p>
<ul>
<li><strong>Ратрак</strong> — подъём на перевал около 2000 м в тёплом салоне, до 12 гостей, обед наверху. От 60 000 ₸ за человека. <a href="ratrak-ridder.html">Как проходит выезд</a>.</li>
<li><strong>Снегоходы</strong> — тот же маршрут быстрее и динамичнее, 2–6 гостей. От 80 000 ₸ за человека. <a href="snegohody-ridder.html">Как проходит выезд</a>.</li>
</ul>
<p>Сезон — с 10 декабря. Новогодние даты разбирают первыми. Подробности — на странице <a href="../zima.html">«Зима»</a>.</p>
'''

def update(slug, section, where, new_title=None):
    f = os.path.join(B, slug + '.html'); s = open(f, encoding='utf-8').read()
    if section.split('\n')[0] in s: print('уже обновлена', slug); return
    head, rest = s.split('\n---\n', 1)
    body, ld = rest.split('<!--LD-->', 1)
    i = -1
    for w in where:
        i = body.find(w)
        if i >= 0: break
    body = body[:i] + section + body[i:] if i >= 0 else body + section
    if new_title: head = re.sub(r'\ntitle: .*', '\ntitle: ' + new_title, head)
    head += f'\nupdated: {T}'
    ld = re.sub(r'"dateModified"\s*:\s*"[^"]*"', f'"dateModified": "{T}"', ld)
    open(f, 'w', encoding='utf-8').write(head + '\n---\n' + body + '<!--LD-->' + ld); print('обновлена', slug)

update('tury-po-vko-2026', WINTER_TURY, ['<h2'], 'Туры по Восточному Казахстану: лето 2026 и зима 2026/27')
update('kuda-poehat-na-vykhodnye-iz-usk', WINTER_USK, ['<div class="faq', '<div class="cta-box', '<h2>Частые'])
