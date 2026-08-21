"""Generate one page per product from the range page's own cards.

The chrome - sprite, announcement, header, footer, enquiry modal, zoom overlay -
is lifted straight out of range.html so these pages cannot drift from it, with
paths made root-relative because they live two directories down.
"""
import json, re, html, os, unicodedata

src = open('range.html', encoding='utf-8').read()
lines = src.split('\n')


def block(a, b):                       # 1-indexed, inclusive
    return '\n'.join(lines[a - 1:b])


def find(pattern, start=0):
    for i in range(start, len(lines)):
        if re.match(pattern, lines[i]):
            return i + 1
    raise SystemExit('not found: ' + pattern)


i_sprite = find(r'<svg width="0"')
i_sprite_end = find(r'</svg>', i_sprite)
i_ann = find(r'<div class="announcement">')
i_ann_end = i_ann + 3
i_head = find(r'<header class="site-header">')
i_head_end = find(r'</header>', i_head)
i_foot = find(r'<footer class="site-footer">')
i_foot_end = find(r'</footer>', i_foot)
i_modal = find(r'<div class="modal-backdrop"')
i_modal_end = find(r'^</div>$', i_modal)
i_zoom = find(r'<div class="zoom-backdrop"')
i_zoom_end = find(r'^</div>$', i_zoom)

SPRITE = block(i_sprite, i_sprite_end)
ANNOUNCE = block(i_ann, i_ann_end)
HEADER = block(i_head, i_head_end)
FOOTER = block(i_foot, i_foot_end)
MODAL = block(i_modal, i_modal_end)
ZOOM = block(i_zoom, i_zoom_end)


def rootify(s):
    """Make a chrome block work from /products/<slug>/."""
    s = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="/' + (m.group(1) or '') + '"', s)
    s = s.replace('href="range.html', 'href="/range.html')
    s = re.sub(r'(src|href)="(official|favicon|apple-touch)', r'\1="/\2', s)
    s = s.replace(' aria-current="page"', '')
    return s


SPRITE, ANNOUNCE, HEADER, FOOTER, MODAL, ZOOM = [
    rootify(x) for x in (SPRITE, ANNOUNCE, HEADER, FOOTER, MODAL, ZOOM)]

CATEGORY = {'devices': 'Devices', 'whitening': 'Whitening', 'toothpaste': 'Toothpaste',
            'brushes': 'Toothbrushes', 'floss': 'Floss & interdental',
            'tongue': 'Tongue care', 'ortho': 'Orthodontic'}

# Longer copy the site already carries for four products; reused, not reinvented.
LEDE = {
    'cr310': 'Two pumps on the brush, thirty seconds to blend. V34 purple pigments cancel '
             'yellow tones on contact, so the difference shows from the first try.',
    'cr320': 'Nano-hydroxyapatite — a mineral the body already recognises — with '
             'theobromine and xylitol, in a pump that gives you the same dose every time.',
    'cr409': 'Up to 40,000 vibrations a minute across five modes, with a timer that paces '
             'you through two minutes. One charge lasts up to 45 days.',
    'cr503': 'For the gaps a brush cannot reach. Five modes and eight pressure levels, '
             'cordless and rechargeable — and far easier to live with if you wear braces.',
}


def slug(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()


def esc(s):
    return html.escape(s, quote=True)


products = json.load(open('_products.json', encoding='utf-8'))
for p in products:
    p['slug'] = slug(p['name'])
    p['sku'] = p['code'].replace(' / ', '').replace(' ', '')
    p['url'] = '/products/' + p['slug'] + '/'
    p['cat_label'] = CATEGORY[p['category']]
    p['lede'] = LEDE.get(p['id'], p['desc'])
json.dump(products, open('_products.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


# Written out by hand, not scraped. The catalogue's notes field is an internal
# ops log: batch numbers, repricing strategy, a buyer's username, a stale price
# and instructions to staff about which claims to avoid. None of that belongs on
# a public page, and no keyword filter is worth trusting with the job.
SPECS = {
    'cr409': ['40,000 vibrations a minute', 'Five modes', 'Smart timer',
              'Rechargeable, up to 45 days per charge'],
    'cr503': ['Five modes', 'Eight pressure levels', 'Cordless and rechargeable'],
    'cr310': ['Purple V34 colour corrector', 'Peroxide-free'],
    'cr311': ['Peroxide-free PAP formula', 'Seven applications'],
    'cr320': ['Nano-hydroxyapatite and theobromine', 'With xylitol', 'Breezy mint',
              '60 g pump dispenser'],
    'cr325': ['Daily fluoride', 'With xylitol', 'Icy peach', '60 g pump dispenser'],
    'cr210': ['Stainless steel', 'Anti-slip handle'],
    'cr220': ['Pure copper'],
    'cr090': ['50 picks per pouch'],
    'cr228': ['25 picks per box'],
    'cr124': ['Two-piece set for braces wearers'],
}


def specs_list(p):
    parts = SPECS.get(p['id'], [])
    if not parts:
        return ''
    items = '\n'.join('        <li>' + esc(x) + '</li>' for x in parts)
    return '      <ul class="product-specs">\n' + items + '\n      </ul>\n'


def gallery(p):
    shots = [p['img']] + p['more']
    if len(shots) < 2:
        return ''
    thumbs = '\n'.join(
        '        <li><img src="/' + s + '" alt="" loading="lazy" width="300" height="290"></li>'
        for s in shots[1:])
    return '      <ul class="product-more">\n' + thumbs + '\n      </ul>\n'


def related(p, all_products):
    sibs = [q for q in all_products if q['category'] == p['category'] and q['id'] != p['id']][:3]
    if not sibs:
        return ''
    tint = 'visual-violet' if p['category'] == 'whitening' else 'visual-mint'
    cards = '\n'.join(
        '      <a class="related-card" href="' + q['url'] + '">\n'
        '        <span class="related-media ' + tint + '"><img src="/' + q['img'] +
        '" alt="" loading="lazy" width="300" height="290"></span>\n'
        '        <span class="related-name">' + esc(q['name']) + '</span>\n'
        '      </a>' for q in sibs)
    return ('\n<section class="related section-shell">\n'
            '  <h2 class="related-head">More ' + p['cat_label'].lower() + '</h2>\n'
            '  <div class="related-grid">\n' + cards + '\n  </div>\n</section>\n')


TPL = open('_template.html', encoding='utf-8').read()
VERSION = re.search(r'style\.css\?v=(\d+)', src).group(1)
os.makedirs('products', exist_ok=True)

for p in products:
    title = p['name'] + ' ' + p['sku'] + ' — Clair' if p['sku'].startswith('CR') else p['name'] + ' — Clair'
    if len(title) > 60:
        title = p['name'] + ' — Clair'

    descr = p['lede']
    if len(descr) < 70 and SPECS.get(p['id']):
        descr = descr.rstrip('.') + '. ' + ', '.join(SPECS[p['id']]) + '.'
    descr = re.sub(r'\s+', ' ', descr).strip()
    if len(descr) > 158:
        descr = descr[:155].rsplit(' ', 1)[0] + '…'

    jsonld = json.dumps({
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Product', 'name': p['name'], 'sku': p['sku'],
             'description': re.sub(r'\s+', ' ', p['lede']),
             'image': 'https://clairoral.com/' + p['img'],
             'brand': {'@type': 'Brand', 'name': 'Clair Oral Care'},
             'category': p['cat_label'],
             'url': 'https://clairoral.com' + p['url']},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': 'https://clairoral.com/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'All products',
                 'item': 'https://clairoral.com/range.html'},
                {'@type': 'ListItem', 'position': 3, 'name': p['name']},
            ]},
        ]}, ensure_ascii=False, indent=2)

    subject = ('Clair enquiry — ' + p['name']).replace(' ', '%20').replace('—', '%E2%80%94').replace('+', '%2B')

    page = TPL.format(
        title=esc(title), descr=esc(descr), ogtitle=esc(p['name'] + ' — Clair Oral Care'),
        url=p['url'], img=p['img'], v=VERSION, jsonld=jsonld,
        sprite=SPRITE, announce=ANNOUNCE, header=HEADER, footer=FOOTER, modal=MODAL, zoom=ZOOM,
        name=esc(p['name']), alt=esc(p['alt']), code=esc(p['code']), cat_label=p['cat_label'],
        cat=p['category'], cat_lower=p['cat_label'].lower(), lede=esc(p['lede']),
        specs=specs_list(p), gallery=gallery(p), related=related(p, products),
        tint='visual-violet' if p['category'] == 'whitening' else 'visual-mint',
        subject=subject)

    d = os.path.join('products', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='').write(page)

print('generated', len(products), 'pages')
for p in products:
    print('  %-42s %s' % (p['url'], p['name']))


# range.html links to itself with bare fragments. Copied onto a product page those
# point at anchors that are not there, so spell them out: a category becomes the
# filtered range page, a product becomes its own page.
import glob
fixed = 0
for f in glob.glob('products/*/index.html'):
    t = open(f, encoding='utf-8').read()
    before = t
    for q in products:
        t = t.replace('href="#' + q['id'] + '"', 'href="' + q['url'] + '"')
    for cat in CATEGORY:
        t = t.replace('href="#' + cat + '"', 'href="/range.html#' + cat + '"')
    if t != before:
        open(f, 'w', encoding='utf-8', newline='').write(t)
        fixed += 1
print('ribbon links spelled out on', fixed, 'pages')
