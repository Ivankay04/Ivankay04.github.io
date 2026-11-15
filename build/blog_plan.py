#!/usr/bin/env python3
# Генерирует «Блог — план публикаций 2026-27.xlsx». Запуск: python3 blog_plan.py <папка>
import sys, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
L = 'Риддер и ВКО'; K = 'Весь Казахстан'; I = 'Иностранцы'; C = 'Китай'
T = [
 ('RU', L, 'Ратрак-туры в Риддере: как проходит день и кому подойдёт', 'ратрак риддер, кэтскиинг казахстан', 'Зима'),
 ('EN', I, 'Cat-skiing in Kazakhstan: the Western Altai near Ridder', 'cat skiing kazakhstan', 'Зима'),
 ('RU', K, 'Куда поехать зимой в Казахстане: Восточный Казахстан вместо Алматы', 'куда поехать зимой казахстан', 'Зима'),
 ('EN', I, 'East Kazakhstan itinerary: 7 days from Ust-Kamenogorsk to Zaisan', 'east kazakhstan itinerary', 'Маршрут'),
 ('RU', L, 'Снегоходные туры в ВКО: маршруты, одежда, безопасность', 'снегоходные туры усть-каменогорск, риддер', 'Зима'),
 ('ZH', C, '东哈萨克斯坦 7 日线路：从厄斯克门到斋桑 (перевод статьи №4)', '东哈萨克斯坦 旅游 线路', 'Маршрут'),
 ('RU', K, 'Новогодние каникулы в Риддере: чем заняться за 3 дня', 'риддер новый год, отдых риддер зимой', 'Зима'),
 ('EN', I, 'How to get to East Kazakhstan: flights, border crossings, transfers', 'how to get to ust-kamenogorsk', 'Логистика'),
 ('RU', L, 'Фрирайд и скитур под Риддером: где катаются и когда снег', 'фрирайд риддер, скитур казахстан', 'Зима'),
 ('EN', I, 'Katon-Karagay National Park: permits, roads and where to stay', 'katon-karagay national park', 'Регион'),
 ('ZH', C, '中国游客如何前往东哈萨克斯坦：免签、口岸与付款', '哈萨克斯坦 免签 吉木乃口岸', 'Логистика'),
 ('RU', K, 'Катон-Карагай своим ходом или с гидом: сравнение по деньгам и времени', 'катон-карагай как добраться', 'Регион'),
 ('EN', I, 'Mount Belukha from the Kazakh side: what you can actually see', 'belukha kazakhstan', 'Регион'),
 ('RU', L, 'Зимний Риддер: где жить и что посмотреть гостям из Усть-Каменогорска', 'риддер зимой, где остановиться в риддере', 'Зима'),
 ('EN', I, 'Lake Markakol and the Old Austrian Road', 'lake markakol, austrian road kazakhstan', 'Регион'),
 ('RU', K, 'Сколько стоит путешествие по Восточному Казахстану в 2027 году', 'туры восточный казахстан цены', 'Цены'),
 ('ZH', C, '哈萨克斯坦一侧的阿尔泰山：卡通-卡拉盖与别卢哈峰 (перевод №10 и №13)', '哈萨克斯坦 阿尔泰 别卢哈峰', 'Регион'),
 ('EN', I, 'Best time to visit the Kazakh Altai, month by month', 'best time to visit east kazakhstan', 'Планирование'),
 ('RU', L, 'Радоновое озеро в 2027: когда открывается дорога и что нового (обновление статьи №1 в поиске)', 'радоновое озеро риддер', 'Маршрут'),
 ('RU', K, 'Маркаколь и Староавстрийская дорога: маршрут на 3 дня', 'маркаколь как добраться, австрийская дорога', 'Маршрут'),
 ('EN', I, 'Kiin-Kerish: the clay canyons near Zaisan', 'kiin-kerish', 'Регион'),
 ('RU', K, 'Корпоративный выезд в горы ВКО: форматы на 1–3 дня', 'корпоратив усть-каменогорск, тимбилдинг вко', 'B2B'),
 ('EN', I, 'Where to stay in East Kazakhstan: lodges, cabins and guesthouses on the route', 'where to stay katon-karagay', 'Планирование'),
 ('ZH', C, '基因-克里什彩色峡谷与斋桑 (перевод №21)', '斋桑 彩色峡谷', 'Регион'),
 ('RU', L, 'Рыбалка на хариуса в ВКО: реки, сезон, правила', 'рыбалка вко хариус, рыбалка уба', 'Рыбалка'),
 ('EN', I, 'Fishing for grayling in East Kazakhstan', 'fishing kazakhstan grayling', 'Рыбалка'),
 ('RU', K, 'Рахмановские ключи и озеро Язёвое: что нужно знать до поездки', 'рахмановские ключи, озеро язевое', 'Регион'),
 ('EN', I, 'Kazakhstan, Kyrgyzstan or Mongolia for an overland trip — where East Kazakhstan fits', 'kazakhstan vs kyrgyzstan travel', 'Сравнение'),
 ('RU', L, 'Майские праздники в ВКО: куда уже можно проехать', 'куда поехать на майские вко', 'Сезон'),
 ('ZH', C, '东哈萨克斯坦住宿指南 (перевод №23)', '东哈萨克斯坦 住宿', 'Планирование'),
 ('EN', I, 'Is East Kazakhstan safe? Roads, weather, connection', 'is kazakhstan safe for tourists', 'Планирование'),
 ('RU', K, 'Из Алматы и Астаны в Восточный Казахстан: перелёты, поезда, логистика', 'алматы усть-каменогорск как добраться', 'Логистика'),
 ('RU', L, 'Однодневные джип-туры из Риддера: сезон 2027, цены и расписание', 'джип туры риддер, джип туры усть-каменогорск', 'Цены'),
 ('EN', I, 'Private tour or group tour in Kazakhstan: cost and what is included', 'private tour kazakhstan', 'Цены'),
 ('RU', K, 'Что взять в горы Алтая летом (обновление существующей статьи)', 'что взять в горы', 'Планирование'),
 ('ZH', C, '东哈萨克斯坦旅行费用与预订流程', '哈萨克斯坦 旅游 费用', 'Цены'),
 ('EN', I, 'Horse riding and maral farms in Katon-Karagay', 'horse riding kazakhstan altai', 'Активности'),
 ('RU', L, 'Малоульбинское водохранилище: SUP, лагерь, дорога', 'малоульбинское водохранилище', 'Маршрут'),
 ('EN', I, 'East Kazakhstan in 3 days and in 5 days: two shorter routes', 'east kazakhstan 3 days', 'Маршрут'),
 ('RU', K, 'Итоги сезона 2026: сколько гостей и откуда к нам приехали', 'asferia adventure отзывы', 'О компании'),
]
wb = Workbook(); ws = wb.active; ws.title = 'План'
ws.append(['№', 'Дата', 'День', 'Язык', 'Аудитория', 'Тема (рабочий заголовок)', 'Поисковый запрос', 'Рубрика', 'Статус'])
d = datetime.date(2026, 11, 24); days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
fills = {'RU': 'F5EFE6', 'EN': 'E4D2BC', 'ZH': 'D9E2DA'}
for i, (lang, aud, title, q, cat) in enumerate(T):
    ws.append([i + 1, d, days[d.weekday()], lang, aud, title, q, cat, 'идея'])
    for c in ws[ws.max_row]: c.fill = PatternFill('solid', fgColor=fills[lang]); c.alignment = Alignment(vertical='top', wrap_text=True)
    ws.cell(ws.max_row, 2).number_format = 'DD.MM.YYYY'
    d += datetime.timedelta(days=3 if d.weekday() == 1 else 4)
for c in ws[1]: c.font = Font(bold=True, color='F5EFE6'); c.fill = PatternFill('solid', fgColor='1F1F1F')
for i, w in enumerate([5, 12, 6, 7, 18, 70, 40, 15, 10]): ws.column_dimensions[get_column_letter(i + 1)].width = w
ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
s = wb.create_sheet('Сводка')
s.append(['Язык', 'Статей', 'Аудитория']);
for lang, aud in (('RU', 'Риддер/ВКО и весь Казахстан'), ('EN', 'Иностранцы, AI-чаты, Google'), ('ZH', 'Китай: переводы лучших EN-статей')):
    s.append([lang, f'=COUNTIF(План!D:D,"{lang}")', aud])
s.append([]); s.append(['Ритм', '2 статьи в неделю: вторник и пятница'])
s.append(['Статусы', 'идея → в работе → готово → опубликовано'])
for c in s[1]: c.font = Font(bold=True)
s.column_dimensions['A'].width = 12; s.column_dimensions['B'].width = 44; s.column_dimensions['C'].width = 44
wb.save(sys.argv[1] + '/Блог — план публикаций 2026-27.xlsx'); print('rows', len(T), 'last', d)
