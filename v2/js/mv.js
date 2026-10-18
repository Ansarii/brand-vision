/* Brand Vision v2: hero video, counters, reveal on scroll */
(function () {
  'use strict';

  // Keep the hero exactly as tall as the screen minus the header
  var hdr = document.querySelector('.coral-site-header');
  var setHdr = function () { if (hdr) document.documentElement.style.setProperty('--hdr', hdr.offsetHeight + 'px'); };
  setHdr();
  window.addEventListener('resize', setHdr);

  // Hero: one video, then two photos, fading from one to the next
  var video = document.querySelector('.mv-hero-video');
  var stills = [].slice.call(document.querySelectorAll('.mv-hero-still'));
  if (video) {
    var conn = navigator.connection || {};
    var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches || conn.saveData || /2g/.test(conn.effectiveType || '');
    if (!calm) {
      var slides = [video].concat(stills), idx = 0, timer = null;
      var hideAll = function () { slides.forEach(function (el) { el.classList.remove('on'); }); };
      var next = function () { idx = (idx + 1) % slides.length; show(); };
      var show = function () {
        clearTimeout(timer);
        hideAll();
        var el = slides[idx];
        if (el === video) {
          video.currentTime = 0;
          video.play().then(function () { video.classList.add('on'); }).catch(function () { timer = setTimeout(next, 4000); });
        } else {
          video.pause();
          el.classList.add('on');
          timer = setTimeout(next, 5500);
        }
      };
      video.addEventListener('ended', next);
      video.src = video.dataset.src;
      video.load();
      video.addEventListener('canplay', function first() {
        video.removeEventListener('canplay', first);
        // Load the photos only once the video is ready
        stills.forEach(function (el) { el.srcset = el.dataset.srcset; el.src = el.dataset.src; el.sizes = '100vw'; });
        show();
      });
    }
  }

  // Count-up stats
  var nums = document.querySelectorAll('[data-count]');
  var cio = 'IntersectionObserver' in window && new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      var el = e.target, end = parseFloat(el.dataset.count), suf = el.dataset.suffix || '', t0 = performance.now();
      (function tick(t) {
        var p = Math.min((t - t0) / 1200, 1), val = end * (1 - Math.pow(1 - p, 3));
        el.textContent = (end % 1 ? val.toFixed(1) : Math.round(val)) + suf;
        if (p < 1) requestAnimationFrame(tick);
      })(t0);
    });
  }, { threshold: 0.6 });
  if (cio) nums.forEach(function (n) { cio.observe(n); });

  // Phone section nav: highlight the section being read and keep its link in view
  var subnav = document.querySelector('.mv-subnav');
  if (subnav) {
    var links = [].slice.call(subnav.querySelectorAll('a'));
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var order = ['top', 'portfolio', 'inventory', 'clients', 'live-footage', 'journey', 'locations', 'day-night', 'preview', 'about', 'contact'];
    var sectionMap = {
      'top': 'top',
      'portfolio': 'portfolio',
      'inventory': 'portfolio',
      'clients': 'clients',
      'live-footage': 'portfolio',
      'journey': 'portfolio',
      'locations': 'portfolio',
      'day-night': 'portfolio',
      'preview': 'portfolio',
      'about': 'about',
      'contact': 'contact'
    };
    var current = null;
    var mark = function () {
      var stickyH = (hdr ? hdr.offsetHeight : 56) + (subnav.offsetHeight || 42);
      var triggerY = stickyH + 40;
      var cur = 'top';
      order.forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        var r = el.getBoundingClientRect();
        if (r.top <= triggerY && r.bottom > triggerY) cur = id;
      });
      var navTarget = sectionMap[cur] || cur;
      if (navTarget === current) return;
      current = navTarget;
      links.forEach(function (l) { l.classList.remove('on'); });
      if (byId[navTarget]) byId[navTarget].classList.add('on');
      syncHeader();
    };
    // Header links (desktop) use the same rule, so both navs always agree
    var headerLinks = [].slice.call(document.querySelectorAll('.coral-nav-link'));
    var syncHeader = function () {
      headerLinks.forEach(function (a) {
        a.classList.toggle('active', !!current && a.getAttribute('href') === '#' + current);
      });
    };
    window.addEventListener('scroll', mark, { passive: true });
    mark();
  }

  // Phones: reveal the chat bubble only after the first screen has been scrolled past
  var onScrollChat = function () { document.body.classList.toggle('mv-scrolled', window.scrollY > window.innerHeight * 0.7); };
  window.addEventListener('scroll', onScrollChat, { passive: true });
  onScrollChat();

})();
