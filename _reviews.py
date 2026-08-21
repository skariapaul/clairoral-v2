"""The review block for a product page.

Reviews are quoted from the product's own Amazon.ae listing. There is no
"Verified Customer" badge on purpose: Amazon marks none of these as a Verified
Purchase, so showing one would be inventing a trust signal. The source line
says where they came from instead - true, and more use to a reader anyway.
"""
import html
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
REVIEWS = json.load(open(os.path.join(_HERE, '_reviews.json'), encoding='utf-8'))

STAR = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>'
        '</svg>')


def _esc(s):
    return html.escape(s, quote=True)


def reviews_block(product_id):
    rows = REVIEWS.get(product_id, [])
    if not rows:
        return ''

    cards = []
    for r in rows:
        cards.append(
            '      <li class="review">\n'
            '        <p class="review-head">'
            '<span class="review-name">' + _esc(r['name']) + '</span>'
            '<span class="review-stars" role="img" aria-label="Rated 5 out of 5">'
            + STAR * 5 + '</span></p>\n'
            '        <p class="review-source">Reviewed on Amazon.ae</p>\n'
            '        <p class="review-title">' + _esc(r['title']) + '</p>\n'
            '        <p class="review-body">' + _esc(r['body']) + '</p>\n'
            '      </li>')

    return ('\n<section class="reviews section-shell" id="reviews">\n'
            '  <h2 class="reviews-head">What people say</h2>\n'
            '  <ul class="review-grid">\n' + '\n'.join(cards) + '\n  </ul>\n'
            '  <p class="reviews-note">Reviews collected on Amazon.ae, '
            'where this product is also sold.</p>\n'
            '</section>\n')
