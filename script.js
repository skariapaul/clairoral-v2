/* Clair Oral Care — progressive enhancement only.
   Every product card and every link works with this file absent; nothing here
   creates content, it only filters, toggles and decorates. */
(function () {
  'use strict';

  /* --- Sticky header state ------------------------------------------------ */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('site-header-scrolled', window.scrollY > 12);
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --- Mobile menu -------------------------------------------------------- */
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    nav.id = nav.id || 'primary-nav';
    toggle.setAttribute('aria-controls', nav.id);

    var setMenu = function (open) {
      nav.classList.toggle('main-nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };

    toggle.addEventListener('click', function () {
      setMenu(!nav.classList.contains('main-nav-open'));
    });

    // Tapping a destination should close the menu behind it.
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });

    addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('main-nav-open')) {
        setMenu(false);
        toggle.focus();
      }
    });
  }

  /* --- Range filter -------------------------------------------------------
     Cards stay in the DOM; only their `hidden` attribute changes, so the full
     catalogue remains readable to crawlers and to anyone without JS.
     ------------------------------------------------------------------------ */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.category-row [data-filter]'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.product-card[data-category]'));
  var counter = document.querySelector('[data-range-count]');
  var total = cards.length;

  if (tabs.length && cards.length) {
    var apply = function (filter, label) {
      var shown = 0;
      cards.forEach(function (card) {
        var match = filter === 'all' || card.dataset.category === filter;
        card.hidden = !match;
        if (match) shown++;
      });

      tabs.forEach(function (tab) {
        var active = tab.dataset.filter === filter;
        tab.classList.toggle('category-active', active);
        tab.setAttribute('aria-selected', String(active));
      });

      if (counter) {
        counter.textContent = filter === 'all'
          ? 'Showing all ' + total + ' products'
          : 'Showing ' + shown + ' of ' + total + ' products — ' + label;
      }
    };

    // The count badge lives in a nested <span>; strip it for the label.
    var labelOf = function (tab) {
      var span = tab.querySelector('span');
      return tab.textContent.replace(span ? span.textContent : '', '').trim();
    };

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        apply(tab.dataset.filter, labelOf(tab));
      });
    });

    // Links elsewhere on the site point here with a category in the hash
    // (range.html#whitening), so honour it on load and on hash change.
    var applyHash = function () {
      var wanted = location.hash.replace('#', '');
      if (!wanted) return;
      var tab = tabs.filter(function (t) { return t.dataset.filter === wanted; })[0];
      if (tab) { apply(tab.dataset.filter, labelOf(tab)); return; }

      // The nav ribbon also links to single products (range.html#cr310). A card
      // the current filter has hidden cannot be scrolled to, so clear the filter
      // and go to it ourselves - the browser already gave up on a hidden target.
      var card = document.getElementById(wanted);
      if (card && card.classList.contains('product-card')) {
        apply('all', 'All products');
        card.scrollIntoView();
      }
    };
    applyHash();
    addEventListener('hashchange', applyHash);

    // Left/right arrows move between filters, per the tablist pattern.
    document.querySelector('.category-row').addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var i = tabs.indexOf(document.activeElement);
      if (i === -1) return;
      e.preventDefault();
      var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      next.focus();
      next.click();
    });
  }

  /* --- Reveal on scroll ---------------------------------------------------
     The original ran every reveal on page load, so anything below the fold had
     already finished animating by the time it was scrolled to. Deferring to an
     observer means each block animates when it actually arrives.
     ------------------------------------------------------------------------ */
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  var reveal = function (el) { el.classList.add('is-revealed'); };
  var inView = function (el) {
    var r = el.getBoundingClientRect();
    return r.top < (innerHeight || 0) && r.bottom > 0;
  };

  // Anything already on screen reveals synchronously. Content must never be
  // left at opacity 0 waiting on a callback that may not run — a throttled or
  // never-composited tab would otherwise render an empty hero.
  reveals.forEach(function (el) { if (inView(el)) reveal(el); });

  var pending = reveals.filter(function (el) { return !el.classList.contains('is-revealed'); });

  if (pending.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        reveal(entry.target);
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });

    pending.forEach(function (el) { io.observe(el); });
  } else {
    pending.forEach(reveal);
  }

  // Failsafe: whatever state the observer is in, nothing stays hidden past load.
  addEventListener('load', function () {
    reveals.forEach(function (el) { if (inView(el)) reveal(el); });
  });
})();
