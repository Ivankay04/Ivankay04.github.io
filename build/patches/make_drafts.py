#!/usr/bin/env python3
# Создаёт черновики будущих статей (с датами публикации и списком фото для заглушек). Существующие файлы не трогает.
import os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')
D = [
 ('ru', 'chem-zanyatsya-v-riddere-zimoy', '2026-11-24', 'Чем заняться в Риддере зимой: 10 идей на выходные', 'Зима', 'winter', '',
  ['hero.jpg | Риддер зимой: город и горы в снегу', '01.jpg | Ратрак или снегоходы в горах', '02.jpg | Баня или база отдыха зимой', '03.jpg | Зимняя дорога в горах, внедорожник']),
 ('en', 'cat-skiing-kazakhstan', '2026-11-27', 'Cat skiing in Kazakhstan: what a day on a snowcat looks like', 'Freeride', 'freeride', '',
  ['hero.jpg | Ратрак на хребте с райдерами', '01.jpg | Райдеры выходят из ратрака наверху', '02.jpg | Спуск по целине между деревьями']),
 ('ru', 'novyy-god-v-riddere', '2026-12-01', 'Новый год в Риддере: программа на 2–3 дня', 'Зима', 'winter', '',
  ['hero.jpg | Новогодний вечер на базе: огни, снег', '01.jpg | Выезд на ратраке в праздники', '02.jpg | Гости у гриля или костра в горах']),
 ('en', 'snowmobile-freeride-ridder', '2026-12-04', 'Snowmobile freeride in Ridder: drop-offs, groups and prices', 'Freeride', 'freeride', '',
  ['hero.jpg | Снегоход с райдерами в лесу', '01.jpg | Райдеры с рюкзаками у снегохода', '02.jpg | Спуск по склону после заброски']),
 ('ru', 'kuda-poehat-zimoy-v-kazakhstane', '2026-12-08', 'Куда поехать зимой в Казахстане, кроме Алматы', 'Зима', 'winter', '',
  ['hero.jpg | Зимние горы Западного Алтая, широкий план', '01.jpg | Ратрак на хребте', '02.jpg | Фрирайдер на спуске по целине', '03.jpg | Риддер зимой']),
 ('zh', 'east-kazakhstan-winter', '2026-12-11', '东哈萨克斯坦的冬天：雪地履带车、雪地摩托与野雪滑雪', '冬季', 'winter', 'img_dir: assets/blog/en/east-kazakhstan-in-winter\nalt_en: east-kazakhstan-in-winter', []),
 ('ru', 'frirayd-v-kazakhstane-almaty-ili-ridder', '2026-12-15', 'Фрирайд в Казахстане: Алматы или Риддер', 'Фрирайд', 'freeride', '',
  ['hero.jpg | Фрирайдер на спуске по целине под Риддером', '01.jpg | Заброска ратраком с райдерами', '02.jpg | Снегоход с райдерами на подъёме']),
 ('en', 'katon-karagay-national-park-guide', '2026-12-18', 'Katon-Karagay National Park: permits, roads and where to stay', 'Region', 'summer', 'hero: assets/pilot/stop-katon-karagay.webp', []),
 ('ru', 'skolko-stoit-otdyh-v-vko-2027', '2026-12-22', 'Сколько стоит отдых в Восточном Казахстане в 2027 году', 'Цены', 'home', '',
  ['hero.jpg | Внедорожник на летнем маршруте в горах', '01.jpg | Ратрак или снегоходы зимой', '02.jpg | Гости за обедом на природе']),
 ('zh', 'china-to-east-kazakhstan', '2026-12-25', '中国游客如何前往东哈萨克斯坦：免签、口岸与付款', '出行', 'home', '',
  ['hero.jpg | Дорога у Зайсана / степь и горы на пути от границы', '01.jpg | Встреча гостей у внедорожника']),
]
for lang, slug, date, title, tag, cta, extra, photos in D:
    f = os.path.join(B, lang, slug + '.md')
    if os.path.exists(f): continue
    os.makedirs(os.path.dirname(f), exist_ok=True)
    ph = ''.join(f'photo: {p}\n' for p in photos)
    ex = (extra + '\n') if extra else ''
    open(f, 'w', encoding='utf-8').write(f'---\ntitle: {title}\ndescription: {title}\ndate: {date}\ntag: {tag}\ncta: {cta}\ndraft: yes\n{ex}{ph}---\nЧерновик — текст будет добавлен.\n')
    print('черновик', lang, slug)
