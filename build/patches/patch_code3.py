#!/usr/bin/env python3
# Правка build.py: подключает блог (статьи, списки, заглушки), последние статьи на главной.
import os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, '..', 'build.py')
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

for lang, fr, bl in (('ru', "'freeride.html'", "'blog.html'"), ('en', "'en/freeride.html'", "'blog-en.html'"),
                     ('zh', "'zh/freeride.html'", "'blog/zh/index.html'"), ('kk', "'kk/freeride.html'", "'blog.html'")):
    rep(f"'freeride': {fr}}}", f"'freeride': {fr}, 'blog': {bl}}}")
rep("    bl = c['blog']", "    bl = dict(c['blog'], cards=latest_cards(lang) or c['blog']['cards'])")
i = s.index('def main():')
s = s[:i] + open(os.path.join(D, 'blog_engine.py'), encoding='utf-8').read() + '\n' + s[i:]
rep("    sm = os.path.join(ROOT, 'sitemap.xml')", "    urls += build_blog()\n    sm = os.path.join(ROOT, 'sitemap.xml')")
open(p, 'w', encoding='utf-8').write(s)
print('build.py patched (3)')
