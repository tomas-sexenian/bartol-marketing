/* =================================================================
   BARTOL MARKETING — main.js
   ================================================================= */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Theme toggle ---------- */
  var themeToggle = doc.getElementById('theme-toggle');
  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem('bartol-theme', theme); } catch (e) {}
    var meta = doc.querySelector('meta[name="theme-color"]');
    if (themeToggle) themeToggle.setAttribute('aria-pressed', theme === 'light');
  }
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      setTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });
  }

  /* ---------- Header scroll state ---------- */
  var header = doc.getElementById('site-header');
  function onScroll() {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 24);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Mobile nav ---------- */
  var menuToggle = doc.getElementById('menu-toggle');
  var nav = doc.getElementById('primary-nav');
  function closeMenu() {
    if (!nav) return;
    nav.classList.remove('is-open');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', 'Abrir menú');
    }
  }
  if (menuToggle && nav) {
    menuToggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuToggle.setAttribute('aria-expanded', String(open));
      menuToggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
  }

  /* ---------- Services accordion ---------- */
  doc.querySelectorAll('.service').forEach(function (service) {
    var row = service.querySelector('.service__row');
    if (!row) return;
    row.addEventListener('click', function () {
      var open = service.classList.toggle('is-open');
      row.setAttribute('aria-expanded', String(open));
    });
  });

  /* ---------- Carousels ---------- */
  doc.querySelectorAll('.carousel').forEach(function (carousel) {
    var slides = Array.prototype.slice.call(carousel.querySelectorAll('.carousel__slide'));
    if (slides.length === 0) return;
    var prev = carousel.querySelector('.carousel__btn--prev');
    var next = carousel.querySelector('.carousel__btn--next');
    var dotsWrap = carousel.querySelector('.carousel__dots');
    var index = 0;
    var timer = null;
    var interval = parseInt(carousel.getAttribute('data-interval'), 10) || 5200;

    // Build dots
    var dots = [];
    if (dotsWrap && slides.length > 1) {
      slides.forEach(function (_, i) {
        var b = doc.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', 'Ir a la imagen ' + (i + 1));
        b.addEventListener('click', function () { go(i); restart(); });
        dotsWrap.appendChild(b);
        dots.push(b);
      });
    }

    function go(i) {
      slides[index].classList.remove('is-active');
      if (dots[index]) dots[index].classList.remove('is-active');
      index = (i + slides.length) % slides.length;
      slides[index].classList.add('is-active');
      if (dots[index]) dots[index].classList.add('is-active');
    }
    function nextSlide() { go(index + 1); }
    function start() {
      if (prefersReduced || slides.length < 2) return;
      timer = window.setInterval(nextSlide, interval);
    }
    function stop() { if (timer) { window.clearInterval(timer); timer = null; } }
    function restart() { stop(); start(); }

    if (dots[0]) dots[0].classList.add('is-active');
    if (next) next.addEventListener('click', function () { go(index + 1); restart(); });
    if (prev) prev.addEventListener('click', function () { go(index - 1); restart(); });
    if (slides.length < 2) {
      if (next) next.style.display = 'none';
      if (prev) prev.style.display = 'none';
    }
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    carousel.addEventListener('focusin', stop);
    carousel.addEventListener('focusout', start);
    start();
  });

  /* ---------- Scroll reveal ---------- */
  var reveals = doc.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !prefersReduced) {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Active nav link on scroll ---------- */
  var sections = doc.querySelectorAll('main section[id]');
  var navLinks = {};
  doc.querySelectorAll('.nav__list a[href^="#"]').forEach(function (a) {
    navLinks[a.getAttribute('href').slice(1)] = a;
  });
  if ('IntersectionObserver' in window && sections.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = navLinks[entry.target.id];
        if (!link) return;
        if (entry.isIntersecting) {
          Object.keys(navLinks).forEach(function (k) { navLinks[k].classList.remove('is-active'); });
          link.classList.add('is-active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---------- Contact form -> WhatsApp / email (with fallbacks) ---------- */
  var form = doc.getElementById('contact-form');
  var status = doc.getElementById('form-status');
  var fallback = doc.getElementById('form-fallback');
  var emailBtn = doc.getElementById('send-email');
  var WA_NUMBER = '59892711562';
  var EMAIL = 'bartol.marketing@gmail.com';

  function getData() {
    return {
      name: (doc.getElementById('cf-name') || {}).value || '',
      email: (doc.getElementById('cf-email') || {}).value || '',
      service: (doc.getElementById('cf-service') || {}).value || '',
      message: (doc.getElementById('cf-message') || {}).value || ''
    };
  }
  function validate(d) {
    var ok = true;
    var nameEl = doc.getElementById('cf-name');
    var serviceEl = doc.getElementById('cf-service');
    [nameEl, serviceEl].forEach(function (el) { if (el) el.classList.remove('is-invalid'); });
    if (!d.name.trim()) { if (nameEl) nameEl.classList.add('is-invalid'); ok = false; }
    if (!d.service) { if (serviceEl) serviceEl.classList.add('is-invalid'); ok = false; }
    return ok;
  }
  function buildMessage(d) {
    var lines = ['Hola Bartol Marketing,', ''];
    lines.push('Nombre / empresa: ' + d.name);
    if (d.email.trim()) lines.push('Email: ' + d.email);
    if (d.service) lines.push('Servicio: ' + d.service);
    if (d.message.trim()) lines.push('Mensaje: ' + d.message);
    return lines.join('\n');
  }
  function flash(msg) { if (status) status.textContent = msg || ''; }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = doc.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', '');
        ta.style.position = 'absolute'; ta.style.left = '-9999px';
        doc.body.appendChild(ta); ta.select();
        var ok = doc.execCommand('copy');
        doc.body.removeChild(ta);
        ok ? resolve() : reject();
      } catch (e) { reject(e); }
    });
  }

  // Build fallback UI with safe DOM methods (no innerHTML -> no XSS from user input).
  function clearFallback() {
    if (!fallback) return;
    while (fallback.firstChild) fallback.removeChild(fallback.firstChild);
    fallback.hidden = true;
  }
  function el(tag, text, attrs) {
    var node = doc.createElement(tag);
    if (text) node.textContent = text;
    if (attrs) Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    return node;
  }
  function showFallback(nodes) {
    if (!fallback) return;
    clearFallback();
    var p = doc.createElement('p');
    nodes.forEach(function (n) { p.appendChild(typeof n === 'string' ? doc.createTextNode(n) : n); });
    fallback.appendChild(p);
    fallback.hidden = false;
  }

  // Detect whether opening a protocol actually took the user away from the page.
  function watchLeave(onStay, ms) {
    var left = false;
    function mark() { left = true; }
    window.addEventListener('blur', mark, { once: true });
    function vc() { if (doc.hidden) { left = true; doc.removeEventListener('visibilitychange', vc); } }
    doc.addEventListener('visibilitychange', vc);
    setTimeout(function () {
      window.removeEventListener('blur', mark);
      doc.removeEventListener('visibilitychange', vc);
      if (!left) onStay();
    }, ms || 1400);
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFallback();
      var d = getData();
      if (!validate(d)) { flash('Completá tu nombre y el servicio que buscás.'); return; }
      var msg = buildMessage(d);
      var url = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(msg);
      // window.open must run synchronously inside the click gesture (avoids popup blocking).
      var win = window.open(url, '_blank', 'noopener');
      var blocked = !win || win.closed || typeof win.closed === 'undefined';
      copyText(msg)['catch'](function () {}).then(function () {
        if (blocked) {
          flash('');
          showFallback([
            'No pudimos abrir WhatsApp automáticamente. ',
            el('a', 'Abrir WhatsApp', { href: url, target: '_blank', rel: 'noopener' }),
            ' (copiamos tu mensaje) o escribinos a ',
            el('a', EMAIL, { href: 'mailto:' + EMAIL }), '.'
          ]);
        } else {
          flash('Te abrimos WhatsApp con tu mensaje.');
        }
      });
    });
  }

  if (emailBtn) {
    emailBtn.addEventListener('click', function () {
      clearFallback();
      var d = getData();
      if (!validate(d)) { flash('Completá tu nombre y el servicio que buscás.'); return; }
      var msg = buildMessage(d);
      var subject = 'Consulta web — ' + (d.service || 'Bartol Marketing');
      var url = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) +
                '&body=' + encodeURIComponent(msg);
      // Copy first so the user always keeps the message, then try to open the mail client.
      copyText(msg)['catch'](function () {}).then(function () {
        flash('Abriendo tu correo…');
        var a = doc.createElement('a');
        a.href = url; a.style.display = 'none';
        doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
        var waUrl = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(msg);
        watchLeave(function () {
          flash('');
          showFallback([
            'No pudimos abrir tu correo. Copiamos tu mensaje: escribinos a ',
            el('a', EMAIL, { href: 'mailto:' + EMAIL }),
            ' o por ',
            el('a', 'WhatsApp', { href: waUrl, target: '_blank', rel: 'noopener' }),
            ' y pegalo.'
          ]);
        }, 1400);
      });
    });
  }

  /* ---------- Footer year ---------- */
  var yearEl = doc.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

})();
