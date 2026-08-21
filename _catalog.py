"""Read the product set straight out of range.html.

The cards on the range page are the catalogue as far as this site is concerned,
so the generator reads them rather than a side file that could fall out of step.
"""
import html
import re

CARD = re.compile(
    r'<article class="product-card" id="([^"]+)" data-category="([^"]+)">(.*?)</article>',
    re.S)


def _one(pattern, body, group=1, default=None):
    m = re.search(pattern, body, re.S)
    return html.unescape(m.group(group)) if m else default


def load_products(page_source):
    out = []
    for pid, cat, body in CARD.findall(page_source):
        more = re.search(r'data-zoom-more="([^"]*)"', body)
        out.append({
            'id': pid,
            'category': cat,
            'code': _one(r'product-card-top"><span>([^<]*)</span>', body),
            # The title is a link now, so allow for the anchor around it.
            'name': _one(r'<h3>(?:<a[^>]*>)?(.*?)(?:</a>)?</h3>', body),
            'desc': _one(r'</h3><p>(.*?)</p>', body),
            'img': re.search(r'class="official-product-image" src="([^"]+)"', body).group(1),
            'alt': _one(r'class="official-product-image"[^>]*alt="([^"]*)"', body, default=''),
            'more': more.group(1).split('|') if more else [],
        })
    return out
