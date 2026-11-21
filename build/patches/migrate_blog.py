#!/usr/bin/env python3
# Одноразово: переносит старые статьи в build/blog/, раскладывает картинки блога по папкам статей, убирает лишние файлы.
import os, re, glob, shutil, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.chdir(ROOT)
TODAY = datetime.date.today().isoformat()

def strip_tags(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()

moves = {}  # старый путь -> новый путь (от корня сайта)
# Русские папки — по имени статьи
for old, new in (('katon-karagay', 'katon-karagayskiy-natsionalnyy-park'), ('tury-vko', 'tury-po-vko-2026'), ('chto-vzyat', 'chto-vzyat-v-dzhip-tur-vko')):
    for f in glob.glob(f'assets/blog/{old}/*'):
        moves[f] = f'assets/blog/{new}/' + os.path.basename(f)

# Английские картинки — в папку той статьи, где они используются
en_files = glob.glob('assets/blog/en/*.jpg')
for f in en_files:
    users = [a for a in glob.glob('blog/en/*.html') if os.path.basename(f) in open(a, encoding='utf-8').read()]
    if len(users) == 1:
        slug = os.path.splitext(os.path.basename(users[0]))[0]
        moves[f] = f'assets/blog/en/{slug}/' + os.path.basename(f)

def fix_paths(s):
    for a, b in moves.items(): s = s.replace(a, b)
    return s

os.makedirs('build/blog/ru', exist_ok=True); os.makedirs('build/blog/en', exist_ok=True)
for path in sorted(glob.glob('blog/*.html') + glob.glob('blog/en/*.html')):
    lang = 'en' if '/en/' in path else 'ru'
    s = open(path, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
    title = re.split(r'\s+[|—]\s+Asferia', title)[0].strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    h1 = strip_tags(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))
    date = re.search(r'"datePublished"\s*:\s*"([\d-]+)', s).group(1)[:10]
    m = re.search(r'<header.*?</header>', s, re.S); head_html = m.group(0) if m else ''
    tag = re.search(r'class="eyebrow"[^>]*>(.*?)</div>', head_html, re.S)
    tag = strip_tags(tag.group(1)) if tag else ''
    hero = None
    mb = re.search(r'class="article-hero-bg"[^>]*style="([^"]*)"', s)
    if mb:
        mu = re.search(r"url\(['\"]?([^'\")]+)", mb.group(1).replace('&#39;', "'").replace('&quot;', '"'))
        hero = mu.group(1) if mu else None
    if not hero:
        mm = re.search(r'<figure class="article-cover"[^>]*>\s*<img[^>]*src="([^"]+)"', s)
        hero = mm.group(1) if mm else None
    if not hero:
        mm = re.search(r"\.article-hero-bg\s*{[^}]*url\(['\"]?([^'\")]+)", s)
        hero = mm.group(1) if mm else None
    i = s.find('<article'); j = s.rfind('</article>')
    body = s[s.find('>', i) + 1:j]
    if not hero:
        mm = re.search(r'<img[^>]*src="([^"]+)"', body); hero = mm.group(1) if mm else 'assets/photo-website-hero3.jpg'
    hero = re.sub(r'^(\.\./)+', '', hero)
    lds = [x for x in re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S) if 'BreadcrumbList' not in x or 'Article' in x]
    body = fix_paths(body).replace('#tours"', '#seasons"')
    slug = os.path.splitext(os.path.basename(path))[0]
    fm = f'---\ntitle: {h1}\nseo_title: {title}\ndescription: {desc}\ndate: {date}\ntag: {tag}\nhero: {fix_paths(hero)}\ncta: none\nlegacy: yes\n---\n'
    open(f'build/blog/{lang}/{slug}.html', 'w', encoding='utf-8').write(fm + body.strip() + '\n<!--LD-->\n' + fix_paths('\n'.join(lds)) + '\n')
    print('перенесена', path, '| hero:', hero, '| tag:', tag)

# Перенос файлов и правка ссылок в остальных файлах сайта
for a, b in moves.items():
    os.makedirs(os.path.dirname(b), exist_ok=True); shutil.move(a, b); print('файл', a, '->', b)
for f in glob.glob('build/content/*.json') + glob.glob('tury/*.html'):
    s = open(f, encoding='utf-8').read(); t = fix_paths(s)
    if t != s: open(f, 'w', encoding='utf-8').write(t); print('ссылки поправлены:', f)

# Лишние файлы в корне assets — в _to_delete, если на них нигде нет ссылок
src = ''.join(open(f, encoding='utf-8', errors='ignore').read() for f in glob.glob('**/*.html', recursive=True) + glob.glob('build/**/*.*', recursive=True) + glob.glob('css/*.css') if os.path.isfile(f))
for f in ('assets/tury-vkohero.jpg', 'assets/ury-vkomalouba.jpg', 'assets/team-and-partners.jpg'):
    if os.path.exists(f) and os.path.basename(f) not in src:
        os.makedirs('assets/_to_delete', exist_ok=True); shutil.move(f, 'assets/_to_delete/' + os.path.basename(f)); print('в _to_delete:', f)
    elif os.path.exists(f): print('оставлен (используется):', f)
