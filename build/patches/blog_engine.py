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

