/* Brand Vision v2: hero video, counters, reveal on scroll */
(function () {
  'use strict';

  // Keep the hero exactly as tall as the screen minus the header
  var hdr = document.querySelector('.coral-site-header');
  var setHdr = function () { if (hdr) document.documentElement.style.setProperty('--hdr', hdr.offsetHeight + 'px'); };
  setHdr();
  window.addEventListener('resize', setHdr);

  // Hero: 2 videos and 2 photos cycling seamlessly
  var heroMedia = document.querySelector('.mv-hero-media');
  if (heroMedia) {
    var slides = [].slice.call(heroMedia.querySelectorAll('.mv-hero-video, .mv-hero-still'));
    var videos = [].slice.call(heroMedia.querySelectorAll('.mv-hero-video'));
    var stills = [].slice.call(heroMedia.querySelectorAll('.mv-hero-still'));
    if (slides.length > 0) {
      var conn = navigator.connection || {};
      var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches || conn.saveData || /2g/.test(conn.effectiveType || '');
      if (!calm) {
        var idx = 0, timer = null, initialized = false;
        var hideAll = function () {
          slides.forEach(function (el) { el.classList.remove('on'); });
        };
        var next = function () {
          idx = (idx + 1) % slides.length;
          show();
        };
        var show = function () {
          clearTimeout(timer);
          var el = slides[idx];
          videos.forEach(function (v) {
            if (v !== el) {
              try { v.pause(); } catch (e) {}
            }
          });
          hideAll();
          el.classList.add('on');
          if (el.tagName === 'VIDEO') {
            if (!el.src && el.dataset.src) {
              el.src = el.dataset.src;
              el.load();
            }
            try { el.currentTime = 0; } catch (e) {}
            var p = el.play();
            // Video display duration: naturally ends at ~10s or safety timer at 9500ms
            timer = setTimeout(next, 9500);
            if (p && typeof p.then === 'function') {
              p.catch(function () {
                clearTimeout(timer);
                var unlock = function () {
                  el.play();
                  window.removeEventListener('pointerdown', unlock);
                  window.removeEventListener('scroll', unlock);
                };
                window.addEventListener('pointerdown', unlock, { once: true, passive: true });
                window.addEventListener('scroll', unlock, { once: true, passive: true });
                timer = setTimeout(next, 5000);
              });
            }
          } else {
            // High-resolution still photo: display for 5.5 seconds
            timer = setTimeout(next, 5500);
          }
        };

        videos.forEach(function (v) {
          v.addEventListener('ended', function () {
            if (slides[idx] === v) {
              clearTimeout(timer);
              next();
            }
          });
        });

        var init = function () {
          if (initialized) return;
          initialized = true;
          stills.forEach(function (el) {
            if (el.dataset.srcset) el.srcset = el.dataset.srcset;
            if (el.dataset.src) el.src = el.dataset.src;
            el.sizes = '100vw';
          });
          videos.forEach(function (v, i) {
            if (i > 0 && !v.src && v.dataset.src) {
              v.src = v.dataset.src;
              v.preload = 'metadata';
            }
          });
          show();
        };

        var primaryVideo = videos[0];
        if (primaryVideo) {
          if (!primaryVideo.src && primaryVideo.dataset.src) {
            primaryVideo.src = primaryVideo.dataset.src;
          }
          if (primaryVideo.readyState >= 2) {
            init();
          } else {
            primaryVideo.addEventListener('loadeddata', init, { once: true });
            primaryVideo.addEventListener('canplay', init, { once: true });
            setTimeout(init, 350);
            primaryVideo.load();
          }
        } else {
          init();
        }
      }
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
