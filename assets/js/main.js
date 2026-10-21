/* ==========================================================================
   Brand Vision - Human-Centric Interactive Engine (2026)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initCoralHeroSlider();
  initCoralNav();
  initCatalogFilters();
  initDayNightToggle();
  initLocationDirectory();
  initAdVisualizer();
  initModernContactForm();
  initLightbox();
  initSmoothScroll();
  initScrollExperience();
  initAIChatSupport();
  initDocViewer();
  initAutoplayVideos();
});

/* --------------------------------------------------------------------------
   Scroll experience: compact header, progress bar, reveal-on-scroll, counters
   -------------------------------------------------------------------------- */
function initScrollExperience() {
  const header = document.querySelector('.coral-site-header, .site-header');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Progress bar element inside the header
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  header && header.appendChild(bar);
  const needsJsProgress = !CSS.supports('animation-timeline: scroll()');

  let ticking = false;
  let cachedMax = 0;
  const updateMax = () => {
    cachedMax = document.documentElement.scrollHeight - window.innerHeight;
  };
  window.addEventListener('resize', updateMax, { passive: true });
  updateMax();

  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      header && header.classList.toggle('is-scrolled', y > 40);
      if (needsJsProgress && cachedMax > 0) {
        bar.style.setProperty('--progress', (y / cachedMax).toFixed(4));
      }
      ticking = false;
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Performance: Pause infinite marquees when not in viewport
  const clientsSection = document.getElementById('clients') || document.querySelector('.trust-showcase-section');
  if (clientsSection && 'IntersectionObserver' in window) {
    const marqueeObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const tracks = clientsSection.querySelectorAll('.trust-marquee-track');
        tracks.forEach(track => {
          track.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused';
        });
      });
    }, { threshold: 0.05 });
    marqueeObserver.observe(clientsSection);
  }

  // Mark elements to reveal; stagger siblings in the same group
  const groups = [
    ['.section-header', 'up'],
    ['.catalog-nav', 'up'],
    ['.catalog-card', 'up'],
    ['.journey-card', 'up'],
    ['.location-item-card', 'left'],
    ['.location-preview-box', 'right'],
    ['.night-showcase-box', 'zoom'],
    ['.mockup-tool-box', 'zoom'],
    ['.testimonial-card-item', 'up'],
    ['.about-media', 'left'],
    ['.about-copy', 'right'],
    ['.about-points li', 'up'],
    ['#contact .section-header + div', 'up'],
    ['.footer-top-grid > div', 'up']
  ];

  if (reduceMotion || !('IntersectionObserver' in window)) return;

  groups.forEach(([selector, type]) => {
    document.querySelectorAll(selector).forEach(el => {
      const siblings = [...el.parentElement.children].filter(c => c.matches(selector));
      el.dataset.reveal = type;
      el.style.setProperty('--i', Math.min(siblings.indexOf(el), 5));
    });
  });

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      el.classList.add('is-visible');
      revealObserver.unobserve(el);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });

  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el));

  // Count-up for hero numbers
  const counterObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      counterObserver.unobserve(entry.target);
      const node = [...entry.target.childNodes].find(n => n.nodeType === 3 && /\d/.test(n.textContent));
      if (!node) return;
      const match = node.textContent.match(/([\d.]+)(\D*)/);
      const target = parseFloat(match[1]);
      const suffix = match[2];
      const decimals = (match[1].split('.')[1] || '').length;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        node.textContent = target.toFixed(decimals) + suffix;
        return;
      }
      const start = performance.now();
      const duration = 600;
      const step = now => {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        node.textContent = (target * eased).toFixed(decimals) + suffix;
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.2 });

  document.querySelectorAll('.coral-stat-val, .stat-value').forEach(el => counterObserver.observe(el));
}

/* --------------------------------------------------------------------------
   Coral Media Benchmark - Fullscreen Hero Slider Engine
   -------------------------------------------------------------------------- */
function initCoralHeroSlider() {
  const slides = document.querySelectorAll('.coral-slide');
  const pageNums = document.querySelectorAll('.coral-page-num, .coral-progress-bar');
  const prevBtn = document.getElementById('coral-prev');
  const nextBtn = document.getElementById('coral-next');
  const slider = document.querySelector('.coral-hero-slider');

  if (!slides.length) return;

  let current = 0;
  let autoplayTimer = null;
  const slideCount = slides.length;

  function showSlide(index) {
    current = (index + slideCount) % slideCount;

    slides.forEach((slide, i) => {
      const isActive = (i === current);
      slide.classList.toggle('active', isActive);
      const slideVid = slide.querySelector('video');
      if (slideVid) {
        if (isActive) {
          slideVid.muted = true;
          slideVid.currentTime = 0;
          const p = slideVid.play();
          if (p !== undefined) {
            p.catch(() => {});
          }
        } else {
          slideVid.pause();
        }
      }
    });

    pageNums.forEach((btn, i) => {
      btn.classList.toggle('active', i === current);
    });
  }

  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      showSlide(current + 1);
    }, 8200);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  // Event handlers
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      showSlide(current - 1);
      startAutoplay();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      showSlide(current + 1);
      startAutoplay();
    });
  }

  pageNums.forEach((btn, i) => {
    btn.addEventListener('click', () => {
      showSlide(i);
      startAutoplay();
    });
  });

  let heroInView = true;

  if (slider) {
    slider.addEventListener('mouseenter', stopAutoplay);
    slider.addEventListener('mouseleave', () => { if (heroInView) startAutoplay(); });

    // Performance: freeze the slider and its video while the hero is scrolled out of view
    if ('IntersectionObserver' in window) {
      const heroObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          heroInView = entry.isIntersecting;
          const activeVid = slides[current] ? slides[current].querySelector('video') : null;
          if (heroInView) {
            if (activeVid && activeVid.paused) {
              const p = activeVid.play();
              if (p !== undefined) p.catch(() => {});
            }
            startAutoplay();
          } else {
            stopAutoplay();
            if (activeVid) activeVid.pause();
          }
        });
      }, { threshold: 0 });
      heroObserver.observe(slider);
    }

    // Touch support
    let startX = 0;
    slider.addEventListener('touchstart', e => {
      startX = e.touches[0].clientX;
    }, { passive: true });

    slider.addEventListener('touchend', e => {
      const diffX = e.changedTouches[0].clientX - startX;
      if (Math.abs(diffX) > 40) {
        if (diffX < 0) {
          showSlide(current + 1);
        } else {
          showSlide(current - 1);
        }
        startAutoplay();
      }
    }, { passive: true });
  }

  // Initial start
  showSlide(0);
  startAutoplay();
}

/* --------------------------------------------------------------------------
   Coral Media Benchmark - Luxury Navigation Drawer & Header Spy
   -------------------------------------------------------------------------- */
function initCoralNav() {
  const toggle = document.getElementById('coral-menu-toggle');
  const drawer = document.getElementById('coral-drawer-overlay');
  const closeBtn = document.getElementById('coral-drawer-close');
  const backdrop = document.getElementById('coral-drawer-backdrop');
  const drawerLinks = document.querySelectorAll('.coral-drawer-link, #drawer-logo-link');
  const navLinks = document.querySelectorAll('.coral-nav-link');

  let isToggling = false;
  function lockToggle() {
    isToggling = true;
    setTimeout(() => { isToggling = false; }, 300);
  }

  function openDrawer() {
    if (isToggling) return;
    if (drawer) {
      drawer.classList.add('active');
      drawer.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
    lockToggle();
  }

  function closeDrawer() {
    if (isToggling) return;
    if (drawer) {
      drawer.classList.remove('active');
      drawer.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
    lockToggle();
  }

  window.__bvCloseDrawer = closeDrawer;
  window.__bvOpenDrawer = openDrawer;

  // MutationObserver safeguard: guarantee toggle aria-expanded matches drawer active class at all times
  if (drawer && 'MutationObserver' in window) {
    const drawerObserver = new MutationObserver(() => {
      const isActive = drawer.classList.contains('active');
      if (toggle) {
        toggle.setAttribute('aria-expanded', isActive ? 'true' : 'false');
      }
      if (!isActive) {
        document.body.style.overflow = '';
      }
    });
    drawerObserver.observe(drawer, { attributes: true, attributeFilter: ['class'] });
  }

  if (toggle) {
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      if (drawer && drawer.classList.contains('active')) {
        closeDrawer();
      } else {
        openDrawer();
      }
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeDrawer();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeDrawer);
  }

  // Any link, button, or action inside the drawer must close the drawer cleanly
  if (drawer) {
    drawer.querySelectorAll('a, button:not(#coral-drawer-close)').forEach(el => {
      el.addEventListener('click', () => {
        closeDrawer();
      });
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer && drawer.classList.contains('active')) {
      closeDrawer();
    }
  });

  // Scroll spy for header nav links
  const byId = new Map();
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.startsWith('#')) {
      byId.set(href.slice(1), link);
    }
  });

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(l => l.classList.remove('active'));
      const activeLink = byId.get(entry.target.id);
      if (activeLink) activeLink.classList.add('active');
    });
  }, { rootMargin: '-45% 0px -50% 0px' });

  byId.forEach((_, id) => {
    const section = document.getElementById(id);
    if (section) observer.observe(section);
  });
}

/* --------------------------------------------------------------------------
   1. Filterable Media Inventory Catalog
   -------------------------------------------------------------------------- */
function initCatalogFilters() {
  const tabs = document.querySelectorAll('.catalog-tab');
  const cards = document.querySelectorAll('.catalog-card');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      tab.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });

      const filter = tab.getAttribute('data-filter');

      cards.forEach(card => {
        const cat = card.getAttribute('data-category');
        if (filter === 'all' || cat === filter) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 30);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(15px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
}

/* --------------------------------------------------------------------------
   2. Day vs Night Illumination Toggle
   -------------------------------------------------------------------------- */
function initDayNightToggle() {
  const stage = document.querySelector('.night-viewer-stage');
  const dayBtn = document.getElementById('btn-view-day');
  const nightBtn = document.getElementById('btn-view-night');
  const captionTitle = document.getElementById('caption-title');
  const captionDesc = document.getElementById('caption-desc');

  if (!stage || !dayBtn || !nightBtn) return;

  dayBtn.addEventListener('click', () => {
    dayBtn.classList.add('active');
    nightBtn.classList.remove('active');
    stage.classList.remove('show-night');
    if (captionTitle) captionTitle.textContent = 'Daytime Natural Sunlight View';
    if (captionDesc) captionDesc.textContent = 'High-resolution UV-treated vinyl graphics with architectural greenery framing for clear, vibrant visibility in direct sunlight.';
  });

  nightBtn.addEventListener('click', () => {
    nightBtn.classList.add('active');
    dayBtn.classList.remove('active');
    stage.classList.add('show-night');
    if (captionTitle) captionTitle.textContent = 'Nighttime 6500K LED Illumination';
    if (captionDesc) captionDesc.textContent = 'Equipped with custom edge-lit LED backlights and 3D halo-lit channel lettering, making your advertisement glow brightly throughout the night.';
  });
}

/* --------------------------------------------------------------------------
   3. Hyderabad Locations Directory & Interactive Preview
   -------------------------------------------------------------------------- */
const locationData = {
  rgia: {
    title: 'Rajiv Gandhi International Airport (RGIA)',
    subtitle: 'Departures Concourse, Boarding Gates & Baggage Reclaim',
    desc: 'Hyderabad’s gateway to the world. Our screens dominate the main passenger corridors, shopping areas, boarding gates (Gates 101-112), and luggage belts where travelers spend 25 to 45 minutes.',
    traffic: '2.8M+ Passengers / Month',
    dwell: '35 - 45 Minutes',
    photo: 'img/airport-concourse-sumadhura.webp'
  },
  kokapet: {
    title: 'The Golden Mile - Kokapet & Financial District',
    subtitle: 'High-Speed Arterial Expressways & Luxury Residential Corridors',
    desc: 'The fastest-growing luxury corridor in South India. Our curved arterial billboards (The Trilight, The Line) give your brand unmissable visibility in front of senior executives, tech leaders, and premium homebuyers.',
    traffic: '140,000+ Vehicles / Day',
    dwell: '500m Clear Sightline',
    photo: 'img/highway-curved-kokapet-panoramic.webp'
  },
  gandipet: {
    title: 'Osman Sagar Road - Gandipet IT Corridor',
    subtitle: 'Continuous Roadside Median Kiosks (GPS Monitored)',
    desc: 'Connects the Financial District to Gandipet’s luxury villas and top colleges. Our repetitive dual-sided lit kiosks ensure drivers see your message several times on their daily commute.',
    traffic: '85,000+ Vehicles / Day',
    dwell: 'Repetitive Commute',
    photo: 'img/median-kiosks-actfibernet.webp'
  },
  approach: {
    title: 'Airport Approach & Toll Gateway Curve',
    subtitle: 'Sequential 4-in-a-Row Mega Totems',
    desc: 'Four synchronized structures placed right after each other along the airport highway curve. Arriving and departing passengers experience a full story unfolding across multiple billboards.',
    traffic: '110,000+ Vehicles / Day',
    dwell: 'Synchronized Storytelling',
    photo: 'img/highway-sequential-atlantis.webp'
  }
};

function initLocationDirectory() {
  const cards = document.querySelectorAll('.location-item-card');
  const previewPhoto = document.getElementById('loc-preview-photo');
  const previewTitle = document.getElementById('loc-preview-title');
  const previewSubtitle = document.getElementById('loc-preview-subtitle');
  const previewDesc = document.getElementById('loc-preview-desc');
  const previewTraffic = document.getElementById('loc-preview-traffic');
  const previewDwell = document.getElementById('loc-preview-dwell');

  cards.forEach(card => {
    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      const locKey = card.getAttribute('data-location');
      const data = locationData[locKey];
      if (!data) return;

      if (previewPhoto && !previewPhoto.src.endsWith(data.photo)) {
        previewPhoto.classList.add('is-swapping');
        setTimeout(() => {
          previewPhoto.onload = () => previewPhoto.classList.remove('is-swapping');
          previewPhoto.src = data.photo;
          if (previewPhoto.complete) previewPhoto.classList.remove('is-swapping');
        }, 250);
      }
      if (previewTitle) previewTitle.textContent = data.title;
      if (previewSubtitle) previewSubtitle.textContent = data.subtitle;
      if (previewDesc) previewDesc.textContent = data.desc;
      if (previewTraffic) previewTraffic.textContent = data.traffic;
      if (previewDwell) previewDwell.textContent = data.dwell;
    });
  });
}

/* --------------------------------------------------------------------------
   4. Modern Custom Dropdowns & Brand Ad Visualizer
   -------------------------------------------------------------------------- */
function initAdVisualizer() {
  const canvas = document.getElementById('canvas-preview');
  const nameInput = document.getElementById('brand-name-input');
  const taglineInput = document.getElementById('brand-tagline-input');
  const locationInput = document.getElementById('brand-location-val');
  const styleInput = document.getElementById('brand-style-val');
  const downloadBtn = document.getElementById('btn-download-mockup');

  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Board faces are stored as FRACTIONS of the photo (0..1), so the coordinates stay
  // aligned no matter what resolution the photograph is exported at (fixes the 4K mismatch).
  const billboardSpots = {
    airport: {
      src: 'img/airport-concourse-sumadhura.webp',
      poly: [[0.188, 0.147], [0.826, 0.151], [0.826, 0.421], [0.188, 0.418]],
      surface: 'led'
    },
    highway: {
      src: 'img/trilight-kokapet-mercedes.webp',
      poly: [[0.24125, 0.19486], [0.63938, 0.19486], [0.63938, 0.44384], [0.24125, 0.44384]],
      surface: 'flood'
    },
    totem: {
      src: 'img/airport-gate-jackdaniels.webp',
      poly: [[0.39, 0.2089], [0.6425, 0.2089], [0.6425, 0.7911], [0.39, 0.7911]],
      surface: 'led'
    },
    unipole: {
      src: 'img/highway-sequential-atlantis.webp',
      poly: [[0.1242, 0.1433], [0.2820, 0.1433], [0.2820, 0.4694], [0.1242, 0.4694]],
      surface: 'flood'
    }
  };

  // Theme palettes: ONE panel colour, ONE brand colour, ONE accent. Strong contrast, no clutter.
  const boardThemes = {
    ivory:   { bg: ['#fbf8f1', '#efe8d8'], brand: '#111827', accent: '#c2410c', punch: '#374151' },
    luxury:  { bg: ['#0b0f1a', '#05070c'], brand: '#ffffff', accent: '#d4a537', punch: '#e7d6a4' },
    tech:    { bg: ['#04122a', '#082350'], brand: '#ffffff', accent: '#22d3ee', punch: '#bae6fd' },
    swiss:   { bg: ['#0a0a0a', '#141414'], brand: '#ffffff', accent: '#ffffff', punch: '#d4d4d4' },
    crimson: { bg: ['#3b0a1c', '#5c0f2b'], brand: '#ffffff', accent: '#fb7185', punch: '#fecdd3' }
  };

  const FONT_BRAND = '"Plus Jakarta Sans", "Inter", sans-serif';
  const MAX_CANVAS_W = 2400;

  let currentBgKey = (locationInput && locationInput.value) || 'airport';
  if (!billboardSpots[currentBgKey]) currentBgKey = 'airport';
  let currentThemeKey = (styleInput && styleInput.value) || 'ivory';
  if (!boardThemes[currentThemeKey]) currentThemeKey = 'ivory';

  // Preload real billboard images
  const bgImages = {};
  Object.keys(billboardSpots).forEach(key => {
    bgImages[key] = new Image();
    bgImages[key].onload = () => { if (key === currentBgKey) renderCanvas(); };
    bgImages[key].src = billboardSpots[key].src;
  });

  if (bgImages[currentBgKey].complete && bgImages[currentBgKey].naturalWidth > 0) {
    renderCanvas();
  }
  // Re-render once web fonts are ready so text metrics are exact
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => renderCanvas());
  }

  // Setup Modern Custom Dropdowns
  initModernDropdowns((type, val) => {
    if (type === 'location') {
      currentBgKey = billboardSpots[val] ? val : 'airport';
      if (locationInput) locationInput.value = currentBgKey;
      renderCanvas();
    } else if (type === 'style') {
      currentThemeKey = boardThemes[val] ? val : 'ivory';
      if (styleInput) styleInput.value = currentThemeKey;
      renderCanvas();
    }
  });

  // Live input typing listeners
  if (nameInput) nameInput.addEventListener('input', renderCanvas);
  if (taglineInput) taglineInput.addEventListener('input', renderCanvas);

  // Mockup PNG download handler
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      const brandClean = (nameInput && nameInput.value.trim().toLowerCase().replace(/[^a-z0-9]/g, '-')) || 'brand';
      const link = document.createElement('a');
      link.download = `brandvision-billboard-${brandClean}-${currentBgKey}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
  }

  // Greedy word wrap for the current ctx.font
  function wrapWords(text, maxW) {
    const words = text.split(/\s+/).filter(Boolean);
    const lines = [];
    let line = '';
    words.forEach(word => {
      const test = line ? line + ' ' + word : word;
      if (ctx.measureText(test).width <= maxW || !line) {
        line = test;
      } else {
        lines.push(line);
        line = word;
      }
    });
    if (line) lines.push(line);
    return lines;
  }

  // Largest font size (<= startSize) where the text wraps inside maxW x maxH within maxLines
  function fitText(text, maxW, maxH, startSize, weight, maxLines, lineHeight) {
    let size = Math.max(6, Math.floor(startSize));
    while (size > 6) {
      ctx.font = `${weight} ${size}px ${FONT_BRAND}`;
      const lines = wrapWords(text, maxW);
      const widest = Math.max.apply(null, lines.map(l => ctx.measureText(l).width));
      if (lines.length <= maxLines && widest <= maxW && lines.length * size * lineHeight <= maxH) {
        return { size: size, lines: lines, height: lines.length * size * lineHeight };
      }
      size -= 1;
    }
    ctx.font = `${weight} 6px ${FONT_BRAND}`;
    return { size: 6, lines: wrapWords(text, maxW), height: 6 * lineHeight };
  }

  function tracePoly(pts) {
    ctx.beginPath();
    pts.forEach((pt, i) => {
      if (i === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    });
    ctx.closePath();
  }

  // In-situ renderer: the new campaign REPLACES the existing creative on the board face
  function renderCanvas() {
    const spot = billboardSpots[currentBgKey] || billboardSpots.airport;
    const bgImg = bgImages[currentBgKey];
    const theme = boardThemes[currentThemeKey] || boardThemes.ivory;

    if (!bgImg || !bgImg.complete || bgImg.naturalWidth === 0) return;

    // Canvas keeps the photo's aspect ratio; capped for fast live typing on large 4K photos
    const scale = Math.min(1, MAX_CANVAS_W / bgImg.naturalWidth);
    canvas.width = Math.round(bgImg.naturalWidth * scale);
    canvas.height = Math.round(bgImg.naturalHeight * scale);
    const W = canvas.width;
    const H = canvas.height;

    // 1. Original photographic scene
    ctx.drawImage(bgImg, 0, 0, W, H);

    // 2. Board face polygon in pixels
    const pts = spot.poly.map(p => ({ x: p[0] * W, y: p[1] * H }));
    const minX = Math.min.apply(null, pts.map(p => p.x));
    const maxX = Math.max.apply(null, pts.map(p => p.x));
    const minY = Math.min.apply(null, pts.map(p => p.y));
    const maxY = Math.max.apply(null, pts.map(p => p.y));
    const bw = maxX - minX;
    const bh = maxY - minY;
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const unit = Math.min(bw, bh);

    ctx.save();
    tracePoly(pts);
    ctx.clip();

    // 3. Opaque ad panel: fully covers the previous advertisement (no overlapping text)
    const panel = ctx.createLinearGradient(minX, minY, maxX, maxY);
    panel.addColorStop(0, theme.bg[0]);
    panel.addColorStop(1, theme.bg[1]);
    ctx.fillStyle = panel;
    ctx.fillRect(minX - 4, minY - 4, bw + 8, bh + 8);

    // 4. Realistic surface treatment
    if (spot.surface === 'led') {
      const step = Math.max(2, Math.round(bh / 110));
      ctx.fillStyle = 'rgba(0, 0, 0, 0.07)';
      for (let y = minY; y < maxY; y += step) ctx.fillRect(minX, y, bw, 1);
      for (let x = minX; x < maxX; x += step) ctx.fillRect(x, minY, 1, bh);
    } else {
      const flood = ctx.createLinearGradient(cx, minY, cx, maxY);
      flood.addColorStop(0, 'rgba(255, 255, 235, 0.18)');
      flood.addColorStop(0.6, 'rgba(255, 255, 235, 0)');
      ctx.fillStyle = flood;
      ctx.fillRect(minX - 4, minY - 4, bw + 8, bh + 8);
    }

    // 5. Typography: brand name, accent rule, punchline. Two text colours only.
    const brandName = ((nameInput && nameInput.value.trim()) || 'YOUR BRAND').toUpperCase();
    const punchline = ((taglineInput && taglineInput.value.trim()) || 'EXPANDING ACROSS SOUTH INDIA').toUpperCase();

    const maxTextW = bw * 0.80;
    const brandStart = Math.min(bh * 0.34, bw * 0.22);
    const brandFit = fitText(brandName, maxTextW, bh * 0.40, brandStart, 800, 2, 1.06);

    const ruleW = Math.max(brandFit.size * 1.1, unit * 0.12);
    const ruleH = Math.max(2, unit * 0.014);
    const gap = Math.max(4, brandFit.size * 0.32);

    const punchStart = Math.max(8, brandFit.size * 0.40);
    const punchFit = fitText(punchline, maxTextW, bh * 0.24, punchStart, 600, 2, 1.25);

    const stackH = brandFit.height + gap + ruleH + gap + punchFit.height;
    let y = cy - stackH / 2;

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    ctx.font = `800 ${brandFit.size}px ${FONT_BRAND}`;
    ctx.fillStyle = theme.brand;
    brandFit.lines.forEach(line => {
      ctx.fillText(line, cx, y + (brandFit.size * 1.06) / 2);
      y += brandFit.size * 1.06;
    });

    y += gap;
    ctx.fillStyle = theme.accent;
    ctx.fillRect(cx - ruleW / 2, y, ruleW, ruleH);
    y += ruleH + gap;

    ctx.font = `600 ${punchFit.size}px ${FONT_BRAND}`;
    ctx.fillStyle = theme.punch;
    punchFit.lines.forEach(line => {
      ctx.fillText(line, cx, y + (punchFit.size * 1.25) / 2);
      y += punchFit.size * 1.25;
    });

    // 6. Soft glass sheen so the panel sits naturally inside the photograph
    const sheen = ctx.createLinearGradient(minX, minY, maxX, maxY);
    sheen.addColorStop(0, 'rgba(255, 255, 255, 0.10)');
    sheen.addColorStop(0.45, 'rgba(255, 255, 255, 0)');
    sheen.addColorStop(1, 'rgba(0, 0, 0, 0.06)');
    ctx.fillStyle = sheen;
    ctx.fillRect(minX - 4, minY - 4, bw + 8, bh + 8);

    ctx.restore();

    // 7. Hairline bezel hides any seam between the panel and the physical frame
    ctx.strokeStyle = 'rgba(15, 23, 42, 0.75)';
    ctx.lineWidth = Math.max(1.5, unit * 0.008);
    tracePoly(pts);
    ctx.stroke();
  }
}

/* --------------------------------------------------------------------------
   Modern Accessible Custom Dropdown Manager
   -------------------------------------------------------------------------- */
function initModernDropdowns(onSelectCallback) {
  const dropdowns = document.querySelectorAll('.custom-dropdown');
  if (!dropdowns.length) return;

  dropdowns.forEach(dropdown => {
    const trigger = dropdown.querySelector('.custom-dropdown-trigger');
    const menu = dropdown.querySelector('.custom-dropdown-menu');
    const items = dropdown.querySelectorAll('.custom-dropdown-item');
    const dropdownType = dropdown.getAttribute('data-dropdown');

    if (!trigger || !menu) return;

    // Toggle dropdown open/close
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains('is-open');

      // Close all other dropdowns
      dropdowns.forEach(d => {
        if (d !== dropdown) {
          d.classList.remove('is-open');
          const t = d.querySelector('.custom-dropdown-trigger');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });

      if (isOpen) {
        dropdown.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'false');
      } else {
        dropdown.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
      }
    });

    // Handle Item Selection
    items.forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        const value = item.getAttribute('data-value');
        const title = item.getAttribute('data-title');
        const desc = item.getAttribute('data-desc');

        // Update active class
        items.forEach(it => {
          it.classList.remove('selected');
          it.setAttribute('aria-selected', 'false');
        });
        item.classList.add('selected');
        item.setAttribute('aria-selected', 'true');

        // Update trigger presentation
        const titleEl = dropdown.querySelector('.dropdown-selected-title');
        const descEl = dropdown.querySelector('.dropdown-selected-desc');
        if (titleEl) titleEl.textContent = title;
        if (descEl) descEl.textContent = desc;

        // Close dropdown
        dropdown.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'false');

        // Callback
        if (typeof onSelectCallback === 'function') {
          onSelectCallback(dropdownType, value);
        }
      });
    });

    // Keyboard support for accessibility
    dropdown.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        dropdown.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.focus();
      }
    });
  });

  // Global click outside listener to close dropdowns
  document.addEventListener('click', () => {
    dropdowns.forEach(d => {
      d.classList.remove('is-open');
      const t = d.querySelector('.custom-dropdown-trigger');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  });
}

/* --------------------------------------------------------------------------
   6. Clean Lightbox Modal
   -------------------------------------------------------------------------- */
function initLightbox() {
  const overlay = document.getElementById('modal-lightbox');
  const closeBtn = document.getElementById('modal-close');
  const modalImg = document.getElementById('modal-photo');
  const modalVideo = document.getElementById('modal-video');
  const modalTitle = document.getElementById('modal-title-text');
  const modalLoc = document.getElementById('modal-loc-text');
  const modalFormat = document.getElementById('modal-format-badge');
  const modalSpecsList = document.getElementById('modal-specs-list');

  // Format-specific standards: every category carries different technical specs
  const modalCategorySpecs = {
    airport: [
      ['Display Type', 'Indoor 4K LED, high-lumen calibrated'],
      ['Content Format', 'Full-motion video or static, 10-sec loops'],
      ['Audience', 'Domestic and international passengers, high dwell time'],
      ['Operating Hours', 'Terminal hours, 18+ hrs daily']
    ],
    highway: [
      ['Display Type', 'Frontlit flex vinyl, top-mounted LED floodlights'],
      ['Visibility', 'Straight-line sightline for fast-moving traffic'],
      ['Illumination', 'Lit dusk to dawn, automated astronomical timer'],
      ['Creative Rule', 'Max 7 words, high contrast, large brand mark']
    ],
    tech: [
      ['Display Type', 'Backlit or frontlit street-level formats'],
      ['Audience', 'IT professionals, daily repeat commuters'],
      ['Illumination', 'Lit dusk to dawn with surge protection'],
      ['Creative Rule', 'Short message, repeat-exposure recall focus']
    ],
    transit: [
      ['Display Type', 'Railway Station Platforms & High-Traffic Transit Screens'],
      ['Audience', 'Daily Commuters, Inter-City Travelers, High-Dwell Audiences'],
      ['Illumination', 'Continuous 24/7 Platform Illumination & Digital LED'],
      ['Creative Rule', 'Bold Typography, High Contrast & Direct Response Call-to-Action']
    ],
    barricade: [
      ['Display Type', 'Printed flex on site-perimeter barricade'],
      ['Visibility', 'Long continuous run, eye-level and pedestrian reach'],
      ['Duration', 'Project-linked, flexible monthly flights'],
      ['Creative Rule', 'Panoramic layout, repeat the brand mark along the run']
    ],
    experiential: [
      ['Display Type', 'Landmark 3D installation'],
      ['Visibility', 'All-angle, destination-style landmark'],
      ['Audience', 'Visitors, photo-sharing footfall, social reach'],
      ['Creative Rule', 'Custom fabrication, approvals handled by Brand Vision']
    ],
    kiosks: [
      ['Display Type', 'Cyberabad Traffic Police 4-Sided Overhead Kiosk & Umbrella'],
      ['Visibility', '360-Degree Four-Way Major Intersection Eyeline'],
      ['Audience', 'Dense Vehicular Traffic Stoppage, Pedestrians & Commuters'],
      ['Creative Rule', 'Four-sided synchronized panels, municipal police traffic clearance']
    ]
  };

  const cards = document.querySelectorAll('.catalog-card');

  const closeModal = () => {
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
    if (modalVideo) {
      modalVideo.pause();
      modalVideo.removeAttribute('src');
      modalVideo.style.display = 'none';
    }
    if (modalImg) {
      modalImg.style.display = 'block';
    }
  };

  cards.forEach(card => {
    card.addEventListener('click', (e) => {
      if (card.classList.contains('portfolio-editorial-card')) return;
      if (e.target.closest('a')) return;
      const imgEl = card.querySelector('img');
      const vidEl = card.querySelector('video');
      const vidSource = vidEl ? vidEl.querySelector('source') : null;
      const vidSrc = vidSource ? vidSource.getAttribute('src') : (vidEl ? vidEl.getAttribute('src') : '');
      const imgSrc = imgEl ? imgEl.src : (vidEl ? (vidEl.poster || vidSrc) : '');
      const titleEl = card.querySelector('.catalog-title');
      const locEl = card.querySelector('.catalog-location');
      const tagEl = card.querySelector('.catalog-tag-format');

      const title = titleEl ? titleEl.textContent : '';
      const loc = locEl ? locEl.textContent : '';
      const tag = tagEl ? tagEl.textContent : '';

      if (vidEl && vidSrc && modalVideo) {
        if (modalImg) modalImg.style.display = 'none';
        modalVideo.style.display = 'block';
        modalVideo.src = vidSrc;
        modalVideo.muted = true;
        modalVideo.currentTime = 0;
        const playPromise = modalVideo.play();
        if (playPromise !== undefined) playPromise.catch(() => {});
      } else {
        if (modalVideo) {
          modalVideo.pause();
          modalVideo.removeAttribute('src');
          modalVideo.style.display = 'none';
        }
        if (modalImg) {
          modalImg.style.display = 'block';
          if (imgSrc) modalImg.src = imgSrc;
        }
      }

      if (modalTitle) modalTitle.textContent = title;
      if (modalLoc) modalLoc.textContent = loc;
      if (modalFormat) modalFormat.textContent = tag;

      // Per-card site specifications (category standards + this card's own metrics)
      if (modalSpecsList) {
        const category = card.getAttribute('data-category') || 'highway';
        const metrics = Array.from(card.querySelectorAll('.catalog-metric-pill')).map(p => p.textContent.trim());
        const specs = [];
        metrics.forEach(m => specs.push(['Key Metric', m]));
        (modalCategorySpecs[category] || modalCategorySpecs.highway).forEach(s => specs.push(s));
        modalSpecsList.innerHTML = specs.map(s =>
          `<li><span class="spec-key">${escapeHtml(s[0])}</span><span class="spec-val">${escapeHtml(s[1])}</span></li>`
        ).join('');
      }

      if (overlay) overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  const liveExpandBtns = document.querySelectorAll('.live-video-expand-btn');
  liveExpandBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const card = btn.closest('.live-video-card');
      if (!card) return;
      const vidEl = card.querySelector('video');
      const vidSource = vidEl ? vidEl.querySelector('source') : null;
      const vidSrc = vidSource ? vidSource.getAttribute('src') : (vidEl ? vidEl.getAttribute('src') : '');
      const titleEl = card.querySelector('.live-video-title');
      const locEl = card.querySelector('.live-spec-chip');
      const tagEl = card.querySelector('.live-video-format-tag');
      const chips = Array.from(card.querySelectorAll('.live-spec-chip')).map(c => c.textContent.trim());

      const title = titleEl ? titleEl.textContent : 'On-Site Video Footage';
      const loc = locEl ? locEl.textContent : 'Prime Commercial Corridors';
      const tag = tagEl ? tagEl.textContent : 'Digital Video';

      if (vidEl && vidSrc && modalVideo) {
        if (modalImg) modalImg.style.display = 'none';
        modalVideo.style.display = 'block';
        modalVideo.src = vidSrc;
        modalVideo.muted = true;
        modalVideo.currentTime = 0;
        const playPromise = modalVideo.play();
        if (playPromise !== undefined) playPromise.catch(() => {});
      }

      if (modalTitle) modalTitle.textContent = title;
      if (modalLoc) modalLoc.textContent = loc;
      if (modalFormat) modalFormat.textContent = tag;

      if (modalSpecsList) {
        modalSpecsList.innerHTML = chips.map(chip =>
          `<li><span class="spec-key">Key Metric</span><span class="spec-val">${escapeHtml(chip)}</span></li>`
        ).join('');
      }

      if (overlay) overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  if (closeBtn && overlay) {
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal();
    });
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay && overlay.classList.contains('active')) {
      closeModal();
    }
  });
}

/* --------------------------------------------------------------------------
   7. Smooth Anchor Scroll & URL Hash State Synchronization
   -------------------------------------------------------------------------- */
function initSmoothScroll() {
  const header = document.querySelector('.coral-site-header, .site-header');

  function getScrollTargetY(target) {
    const headerH = header ? header.offsetHeight : 78;
    const isMobile = window.innerWidth <= 820;
    const padding = isMobile ? 48 : 20;
    const targetY = target.getBoundingClientRect().top + window.scrollY - headerH - padding;
    return Math.max(0, targetY);
  }

  function scrollToSection(target, smooth = true) {
    const targetY = getScrollTargetY(target);
    window.scrollTo({
      top: targetY,
      behavior: smooth ? 'smooth' : 'auto'
    });
  }

  let scrollTimer = null;
  function setProgrammaticScroll(targetHash) {
    window.__bvProgrammaticScroll = true;
    if (targetHash) {
      try { sessionStorage.setItem('bv_active_hash', targetHash); } catch (e) {}
      if (history.pushState) history.pushState(null, '', targetHash);
      else window.location.hash = targetHash;
    }
    clearTimeout(scrollTimer);
    const onEnd = () => {
      window.__bvProgrammaticScroll = false;
      window.removeEventListener('scrollend', onEnd);
      clearTimeout(scrollTimer);
    };
    if ('onscrollend' in window) {
      window.addEventListener('scrollend', onEnd, { once: true });
    }
    scrollTimer = setTimeout(() => {
      window.__bvProgrammaticScroll = false;
    }, 1200);
  }

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      let href = this.getAttribute('href');
      if (href === '#' || !href) return;
      if (this.hasAttribute('data-doc-target')) return;

      // Clean Home / Top navigation: smoothly scroll to top and keep URL clean (no /#top)
      if (href === '#top' || href === '#home') {
        e.preventDefault();
        try { sessionStorage.removeItem('bv_active_hash'); } catch (err) {}
        if (history.pushState) history.pushState(null, '', window.location.pathname + window.location.search);
        window.__bvProgrammaticScroll = true;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => { window.__bvProgrammaticScroll = false; }, 1200);
        return;
      }

      // Backward-compatibility alias: rewrite #inventory to #portfolio
      if (href === '#inventory') {
        href = '#portfolio';
      }

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        setProgrammaticScroll(href);
        scrollToSection(target, true);
      }
    });
  });

  // Handle initial page load or browser refresh with hash in URL or sessionStorage
  function handleInitialResume() {
    let hash = window.location.hash;

    // Clean up unwanted /#top or /#home on initial load
    if (hash === '#top' || hash === '#home') {
      if (history.replaceState) history.replaceState(null, '', window.location.pathname + window.location.search);
      hash = '';
    }

    // Backward-compatibility alias: if someone visits with /#inventory, redirect hash to /#portfolio
    if (hash === '#inventory') {
      if (history.replaceState) history.replaceState(null, '', '#portfolio');
      hash = '#portfolio';
    }

    if (!hash || hash === '#') {
      try {
        const saved = sessionStorage.getItem('bv_active_hash');
        if (saved && saved !== '#top' && saved !== '#home') {
          hash = saved === '#inventory' ? '#portfolio' : saved;
        }
      } catch (err) {}
    }

    const revealBody = () => {
      document.documentElement.classList.remove('bv-resuming');
    };

    if (!hash || hash === '#' || hash === '#top' || hash === '#home') {
      revealBody();
      return;
    }
    if (['#blogs', '#terms', '#privacy', '#sources'].includes(hash.toLowerCase())) {
      revealBody();
      return;
    }

    const target = document.querySelector(hash);
    if (target) {
      // Instant positioning (auto) while paint shield is active
      scrollToSection(target, false);
      // Reveal body already positioned at target section
      revealBody();

      requestAnimationFrame(() => {
        scrollToSection(target, false);
      });
      setTimeout(() => {
        scrollToSection(target, false);
      }, 100);
    } else {
      revealBody();
    }
  }

  // Execute immediately upon DOM readiness, never wait for full window.load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleInitialResume);
  } else {
    handleInitialResume();
  }

  const handleHashRouting = () => {
    let hash = window.location.hash;
    if (!hash || hash === '#' || hash === '#top' || hash === '#home') {
      if (hash === '#top' || hash === '#home') {
        if (history.replaceState) history.replaceState(null, '', window.location.pathname + window.location.search);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    if (hash === '#inventory') {
      if (history.replaceState) history.replaceState(null, '', '#portfolio');
      hash = '#portfolio';
    }
    const target = document.querySelector(hash);
    if (target) scrollToSection(target, true);
  };

  window.addEventListener('popstate', handleHashRouting);
  window.addEventListener('hashchange', handleHashRouting);
}

/* --------------------------------------------------------------------------
   Shared Utilities
   -------------------------------------------------------------------------- */
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* --------------------------------------------------------------------------
   8. Modern Executive Contact Form & Interactive Format Chips
   -------------------------------------------------------------------------- */
function initModernContactForm() {
  const form = document.getElementById('campaign-inquiry-form');
  const chipsGroup = document.getElementById('format-chips-group');
  const formatsInput = document.getElementById('selected-formats-input');
  const successCard = document.getElementById('contact-success-card');
  const successMsg = document.getElementById('success-message-text');
  const resetBtn = document.getElementById('btn-reset-inquiry');

  if (!form) return;

  // Inline feedback container
  let errorBanner = form.querySelector('.form-error-banner');
  if (!errorBanner) {
    errorBanner = document.createElement('div');
    errorBanner.className = 'form-error-banner';
    errorBanner.style.cssText = 'display:none; padding:10px 14px; border-radius:8px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:#dc2626; font-size:0.85rem; font-weight:600; margin-bottom:12px;';
    form.insertBefore(errorBanner, form.firstChild);
  }

  function clearErrors() {
    errorBanner.style.display = 'none';
    form.querySelectorAll('.modern-input-wrapper input').forEach(inp => {
      inp.removeAttribute('aria-invalid');
      inp.style.borderColor = '';
    });
  }

  // 1. Format Chips Toggle
  if (chipsGroup) {
    const chips = chipsGroup.querySelectorAll('.format-chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chip.classList.toggle('active');
        const activeFormats = [];
        chipsGroup.querySelectorAll('.format-chip.active').forEach(c => {
          activeFormats.push(c.getAttribute('data-format'));
        });
        if (formatsInput) {
          formatsInput.value = activeFormats.join(', ');
        }
      });
    });
  }

  // Clear errors on input
  form.querySelectorAll('input').forEach(inp => {
    inp.addEventListener('input', () => {
      if (errorBanner.style.display !== 'none') clearErrors();
    });
  });

  // 2. Form Submission Handler
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const nameInput = document.getElementById('contact-name');
    const emailInput = document.getElementById('contact-email');
    const phoneInput = document.getElementById('contact-phone');
    const brandInput = document.getElementById('contact-brand');
    const messageInput = document.getElementById('contact-message');

    const name = (nameInput && nameInput.value.trim()) || '';
    const email = (emailInput && emailInput.value.trim()) || '';
    const phone = (phoneInput && phoneInput.value.trim()) || '';
    const brand = (brandInput && brandInput.value.trim()) || '';
    const message = (messageInput && messageInput.value.trim()) || '';
    const formats = (formatsInput && formatsInput.value.trim()) || 'General Outdoor / Airport Media Inquiry';

    clearErrors();

    // Accessible inline validation
    const missingFields = [];
    if (!name) {
      missingFields.push('Full Name');
      if (nameInput) {
        nameInput.setAttribute('aria-invalid', 'true');
        nameInput.style.borderColor = '#ef4444';
      }
    }
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      missingFields.push('Valid Work Email');
      if (emailInput) {
        emailInput.setAttribute('aria-invalid', 'true');
        emailInput.style.borderColor = '#ef4444';
      }
    }
    if (!phone) {
      missingFields.push('Contact Number');
      if (phoneInput) {
        phoneInput.setAttribute('aria-invalid', 'true');
        phoneInput.style.borderColor = '#ef4444';
      }
    }
    if (!brand) {
      missingFields.push('Brand Name');
      if (brandInput) {
        brandInput.setAttribute('aria-invalid', 'true');
        brandInput.style.borderColor = '#ef4444';
      }
    }

    if (missingFields.length > 0) {
      errorBanner.textContent = `Please provide required details: ${missingFields.join(', ')}.`;
      errorBanner.style.display = 'block';
      if (!name && nameInput) nameInput.focus();
      else if ((!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) && emailInput) emailInput.focus();
      else if (!phone && phoneInput) phoneInput.focus();
      else if (!brand && brandInput) brandInput.focus();
      return;
    }

    // Check honeypot anti-spam
    const honeyInput = form.querySelector('input[name="_honey"]');
    if (honeyInput && honeyInput.value) {
      form.style.display = 'none';
      if (successCard) successCard.style.display = 'block';
      return;
    }

    const submitBtn = document.getElementById('btn-submit-inquiry');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px; animation: spin 1s linear infinite;">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
          <path d="M12 2a10 10 0 0 1 10 10"/>
        </svg>
        <span>Sending Request...</span>
      `;
    }

    // Dispatch real email to info@brandvisionhyd.com via FormSubmit AJAX API
    const payload = {
      name: name,
      email: email,
      phone: phone,
      brand: brand,
      message: message || 'N/A',
      formats_of_interest: formats,
      _subject: `New OOH Campaign Request: ${brand} (${name})`,
      _template: 'table',
      _captcha: 'false'
    };

    fetch('https://formsubmit.co/ajax/info@brandvisionhyd.com', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    .then((response) => {
      return response.json().catch(() => ({ success: true }));
    })
    .then((data) => {
      form.style.display = 'none';
      if (successCard) {
        successCard.style.display = 'block';
        if (successMsg) {
          successMsg.innerHTML = `Thank you, <strong>${escapeHtml(name)}</strong>! Your campaign inquiry for <strong>${escapeHtml(brand)}</strong> has been sent to our Hyderabad media planning desk (info@brandvisionhyd.com). We will confirm availability and custom rates within 2 business hours.`;
        }
      }
    })
    .catch((error) => {
      console.warn('Inquiry dispatch notice:', error);
      form.style.display = 'none';
      if (successCard) {
        successCard.style.display = 'block';
        if (successMsg) {
          successMsg.innerHTML = `Thank you, <strong>${escapeHtml(name)}</strong>! Your campaign inquiry for <strong>${escapeHtml(brand)}</strong> has been recorded. Our planning desk will connect with you at <strong>${escapeHtml(phone)}</strong> shortly.`;
        }
      }
    });
  });

  // 3. Reset Button
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      form.reset();
      clearErrors();
      const submitBtn = document.getElementById('btn-submit-inquiry');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
          <span>Request Availability &amp; Rates</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="btn-arrow-icon"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        `;
      }
      if (successCard) successCard.style.display = 'none';
      form.style.display = '';
    });
  }
}

/* ==========================================================================
   Brand Vision AI Automated Support Engine (2026)
   Trained on Outdoor Media, RGIA Airport, Telangana, AP, Bengaluru & Direct Rates
   ========================================================================== */
function initAIChatSupport() {
  const launcher = document.getElementById('bv-chat-launcher');
  const chatWindow = document.getElementById('bv-chat-window');
  const closeBtn = document.getElementById('bv-chat-close');
  const clearBtn = document.getElementById('bv-chat-clear');
  const messagesEl = document.getElementById('bv-chat-messages');
  const emptyStateEl = document.getElementById('bv-chat-empty-state');
  const quickBar = document.getElementById('bv-chat-quick-bar');
  const chatForm = document.getElementById('bv-chat-form');
  const chatInput = document.getElementById('bv-chat-input');

  if (!launcher || !chatWindow || !messagesEl) return;

  const chatContainer = document.querySelector('.bv-chat-container');

  // SVG helper for action chips
  const SVG_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
  const SVG_EXTERNAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

  // Comprehensive Outdoor Media Knowledge Base
  const BV_KNOWLEDGE = [
    {
      id: 'greeting',
      patterns: [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'namaste', 'start', 'help', 'who are you', 'what is this'
      ],
      reply: 'Hello! Welcome to <strong>Brand Vision Media</strong>. Are you looking for billboard and screen availability across Telangana, Andhra Pradesh, Bengaluru, or other major Indian cities?<br><br>Tell me your preferred corridor, campaign duration, or brand name, and our planning desk will assist you directly.',
      chips: [
        { label: 'Check Site Availability', prompt: 'Check site availability by location' },
        { label: 'Pricing & Estimates', prompt: 'How do billboard and airport rates work?' },
        { label: 'Go-Live Timelines', prompt: 'How fast can our campaign go live?' }
      ]
    },
    {
      id: 'site_availability',
      patterns: [
        'availability', 'available', 'check availability', 'check site availability', 'locations',
        'corridors', 'where', 'vacant', 'open sites', 'inventory', 'check site availability by location',
        'location'
      ],
      reply: '<strong>Live Inventory & Site Availability</strong>:<br>Our media planning desk maintains active inventory across Telangana and Andhra Pradesh, prime presence in Bengaluru, and verified networks across major Indian cities:<ul><li><strong>Telangana &amp; Hyderabad Corridors:</strong> Hitec City, Gachibowli, Financial District, Kokapet, and Outer Ring Road (ORR).</li><li><strong>Andhra Pradesh Corridors:</strong> High-traffic arterial corridors in Vijayawada, Visakhapatnam, and key commercial hubs.</li><li><strong>Bengaluru &amp; Pan-India Metros:</strong> Prime tech corridors, arterial flyovers, and major transit routes.</li><li><strong>Airport Transit Routes:</strong> Rajiv Gandhi International Airport (RGIA) concourses, baggage carousels, and approach expressways.</li></ul>Share your target areas and campaign dates below to receive current availability and site options within <strong>2 hours</strong>.',
      chips: [
        { label: 'Browse Location Directory', href: '#locations' },
        { label: 'Request Availability Check', href: '#contact' },
        { label: 'WhatsApp Planning Desk', href: 'https://wa.me/919885335559' }
      ]
    },
    {
      id: 'airport_overview',
      patterns: [
        'rgia', 'airport', 'shamshabad', 'flight', 'flights', 'terminal', 'airports',
        'passenger', 'passengers', 'flyer', 'flyers', 't1'
      ],
      reply: 'Brand Vision operates four exclusive digital and high-impact physical assets inside and approaching <strong>RGIA Shamshabad (2.8M+ monthly flyers)</strong>:<ul><li><strong>T1 Concourse 4K Curved LED:</strong> Overhead walkway to Gates 1-22 reaching 100% of departing passengers.</li><li><strong>Arrivals Baggage Video Walls:</strong> Eye-level displays at carousels 1-6 with an average 28-minute dwell time.</li><li><strong>Boarding Gates 101-112 Totems:</strong> 85-inch portrait 4K screens capturing high-net-worth flyers with 35-45 min captive wait.</li><li><strong>Sequential Highway Unipoles:</strong> 4 in-a-row hoardings along the airport approach road (110K daily vehicles).</li></ul>',
      chips: [
        { label: 'View Airport Media', href: '#locations' },
        { label: 'Airport Rate Proposal', href: '#contact' }
      ]
    },
    {
      id: 'airport_concourse',
      patterns: [
        'concourse', 'curved led', 'curved', 'gates 1-22', 'gate 1', 'sumadhura', 'walkway'
      ],
      reply: '<strong>RGIA Concourse 4K Curved LED Display</strong>:<br>Positioned directly overhead on the central departure walkway leading to Gates 1 through 22. Every departing flyer passes under this screen.<ul><li><strong>Format:</strong> Curved high-density 4K LED</li><li><strong>Brightness:</strong> 1200+ nits calibrated for terminal lighting</li><li><strong>Monthly Reach:</strong> 2,800,000+ verified flyers</li><li><strong>Playback:</strong> Dynamic 10-second / 15-second high-frequency slots</li></ul>',
      chips: [
        { label: 'View in Directory', href: '#locations' },
        { label: 'Request Availability', href: '#contact' },
        { label: 'Test on Visualizer', href: '#preview' }
      ]
    },
    {
      id: 'airport_baggage',
      patterns: [
        'baggage', 'carousel', 'luggage', 'belt', 'arrivals', 'arrival', 'belt 1'
      ],
      reply: '<strong>RGIA Arrivals Baggage Claim Synchronized Video Walls</strong>:<br>Mounted directly at eye level above baggage carousels 1 to 6. Arriving domestic and international travelers spend an average of <strong>28 minutes</strong> waiting for luggage, delivering zero-distraction captive visibility.',
      chips: [
        { label: 'View Baggage Screens', href: '#locations' },
        { label: 'Get Baggage Screen Rates', href: '#contact' },
        { label: 'WhatsApp Planning Desk', href: 'https://wa.me/919885335559' }
      ]
    },
    {
      id: 'airport_gates',
      patterns: [
        'gates', 'gate 101', 'gate 112', '101-112', 'boarding gate', 'waiting area', 'totem', 'totems'
      ],
      reply: '<strong>Boarding Gates 101-112 Digital Totems</strong>:<br>Stationed in the dedicated departure hold zones for gates 101 through 112. Passengers sit here for <strong>35 to 45 minutes</strong> before boarding flights. Ideal for targeting CXOs, tech leadership, luxury buyers, and business-class travelers.',
      chips: [
        { label: 'View Gate Displays', href: '#locations' },
        { label: 'Request Proposal', href: '#contact' },
        { label: 'Call Managing Partner', href: 'tel:+919885335559' }
      ]
    },
    {
      id: 'kokapet_trilight',
      patterns: [
        'kokapet', 'trilight', 'the trilight', 'mega hoarding', 'huge billboard', 'giant billboard',
        '120ft', 'golden mile', 'arterial'
      ],
      reply: '<strong>The Trilight Kokapet Mega Hoarding</strong>:<br>Hyderabad\'s benchmark outdoor advertising site measuring <strong>120 ft width x 35 ft height (4,200 sq.ft)</strong>.<ul><li><strong>Sightline:</strong> Over 500 meters of uninterrupted straight visibility</li><li><strong>Daily Traffic:</strong> 140,000+ vehicles connecting Financial District, Neopolis, and Kokapet</li><li><strong>Illumination:</strong> 100% dusk-to-dawn calibrated commercial floodlights</li><li><strong>Audience:</strong> High-net-worth real estate buyers, tech leaders, and corporate decision-makers</li></ul>',
      chips: [
        { label: 'View Kokapet in Directory', href: '#locations' },
        { label: 'Test Brand on Visualizer', href: '#preview' },
        { label: 'Request Kokapet Rates', href: '#contact' }
      ]
    },
    {
      id: 'sequential_highway',
      patterns: [
        'sequential', 'unipole', 'unipoles', 'highway', 'approach', '4 in a row', 'storytelling', 'series'
      ],
      reply: '<strong>Airport Approach Sequential Unipoles</strong>:<br>A series of four consecutive large-format hoardings along the primary RGIA approach highway. Enables cinematic brand storytelling across 4 sequential frames with 110,000+ daily vehicular impressions.',
      chips: [
        { label: 'View Highway Sites', href: '#locations' },
        { label: 'Request Sequential Rates', href: '#contact' }
      ]
    },
    {
      id: 'gandipet_kiosks',
      patterns: [
        'gandipet', 'kiosk', 'kiosks', 'median', 'backlit', 'it corridor', 'nanakramguda'
      ],
      reply: '<strong>Gandipet & IT Corridor Backlit Median Kiosks</strong>:<br>12 dual-sided illuminated median totems stationed along the high-density Gandipet and Nanakramguda tech corridors. Reaches 85,000 daily vehicles of tech employees, residents, and business commuters with GPS-timestamped daily photo verification.',
      chips: [
        { label: 'View Median Kiosks', href: '#locations' },
        { label: 'Request Kiosk Rates', href: '#contact' }
      ]
    },
    {
      id: 'narsingi_flyover',
      patterns: [
        'narsingi', 'flyover', 'orr', 'outer ring road', 'gachibowli flyover', 'elevated'
      ],
      reply: '<strong>Narsingi Elevated Unipoles</strong>:<br>Standing at 45ft elevation overlooking the Gachibowli-ORR flyover interchange. Commands attention during morning and evening crawl traffic between Cyberabad and Shamshabad with 400m clear visibility.',
      chips: [
        { label: 'View Narsingi Unipoles', href: '#locations' },
        { label: 'Inquire Availability', href: '#contact' }
      ]
    },
    {
      id: 'rates_pricing',
      patterns: [
        'rate', 'rates', 'price', 'pricing', 'cost', 'costs', 'budget', 'quote', 'how much',
        'rate card', 'charges', 'discount', 'packages', 'deal', 'how do billboard and airport rates work',
        'pricing & custom proposal', 'rates & pricing'
      ],
      reply: '<strong>Transparent Media Network Pricing</strong>:<br>Brand Vision provides direct access to prime airport and arterial outdoor media across Telangana, Andhra Pradesh, Bengaluru, and major Indian cities with transparent, competitive rates.<ul><li><strong>Tenures:</strong> 15-day campaign sprints, 30-day standard flights, quarterly (90-day), and annual partnerships.</li><li><strong>Formal Proposal:</strong> Submit your brand and corridor to receive a complete proposal with site availability, GPS coordinates, and technical specs within <strong>2 hours</strong>.</li></ul>',
      chips: [
        { label: 'Request Custom Rate Card', href: '#contact' },
        { label: 'Chat on WhatsApp', href: 'https://wa.me/919885335559' },
        { label: 'Call +91 98853 35559', href: 'tel:+919885335559' }
      ]
    },
    {
      id: 'booking_process',
      patterns: [
        'book', 'booking', 'process', 'procedure', 'how to book', 'steps', 'timeline', 'reserve',
        'launch', 'lead time', 'how fast can our campaign go live', 'execution & timelines',
        'execution', 'timelines', 'turnaround', 'go live'
      ],
      reply: '<span class="bv-msg-heading">Campaign Booking &amp; Execution Workflow</span><div class="bv-steps-list"><div class="bv-step-row"><div class="bv-step-badge">01</div><div class="bv-step-content"><strong>Inquiry:</strong> Specify your target corridor, preferred campaign dates, and brand requirements.</div></div><div class="bv-step-row"><div class="bv-step-badge">02</div><div class="bv-step-content"><strong>Proposal &amp; Availability:</strong> Our desk shares active inventory options, technical dimensions, and rate card within <strong>2 hours</strong>.</div></div><div class="bv-step-row"><div class="bv-step-badge">03</div><div class="bv-step-content"><strong>Creative Submission:</strong> Provide 4K digital MP4/JPG or high-res 300 DPI flex artwork for pre-flight check.</div></div><div class="bv-step-row"><div class="bv-step-badge">04</div><div class="bv-step-content"><strong>Mounting &amp; Calibration:</strong> Digital displays go live within 24 hours; physical flex hoardings are mounted, illuminated, and structural-certified in 48-72 hours.</div></div><div class="bv-step-row"><div class="bv-step-badge">05</div><div class="bv-step-content"><strong>Audit &amp; Proof:</strong> Daily timestamped, geotagged photos provided directly to your marketing team.</div></div></div>',
      chips: [
        { label: 'Start Campaign Inquiry', href: '#contact' },
        { label: 'Test Creative on Visualizer', href: '#preview' },
        { label: 'WhatsApp Planning Desk', href: 'https://wa.me/919885335559' }
      ]
    },
    {
      id: 'visualizer_preview',
      patterns: [
        'visualizer', 'preview', 'mockup', 'see brand', 'test brand', 'try it yourself', 'simulator',
        'sample', 'design', 'placement'
      ],
      reply: '<strong>Interactive Billboard Visualizer Tool</strong>:<br>You can preview your brand name, tagline, and industry sector directly on our flagship hoardings right now on this page. Toggle between daytime sunlight and nighttime illumination to see real-world contrast.',
      chips: [
        { label: 'Open Billboard Visualizer', href: '#preview' },
        { label: 'View Locations Directory', href: '#locations' },
        { label: 'Request Proposal', href: '#contact' }
      ]
    },
    {
      id: 'contact_human',
      patterns: [
        'contact', 'call', 'phone', 'number', 'whatsapp', 'talk', 'human', 'director', 'agent',
        'person', 'speak', 'email', 'office', 'reach', 'managing partner', 'partner', 'sreedhar',
        'talk to managing partner', 'talk to media director', 'connect with managing partner sri k. sreedhar',
        'connect with founder', 'connect with managing partner', 'founder'
      ],
      reply: '<strong>Connect Directly With Our Managing Partner</strong>:<ul><li><strong>K. Sreedhar (Direct):</strong> +91 98853 35559</li><li><strong>WhatsApp Desk:</strong> Instant response for availability &amp; rate sheets</li><li><strong>Email:</strong> info@brandvisionhyd.com</li><li><strong>Corporate Registered Office:</strong> Flat No. 105, Aneesh Towers, Padmarao Nagar, Secunderabad - 500 025, Telangana</li><li><strong>Response Time:</strong> Quotation and site specs provided within 2 business hours</li></ul>',
      chips: [
        { label: 'Chat on WhatsApp', href: 'https://wa.me/919885335559' },
        { label: 'Call +91 98853 35559', href: 'tel:+919885335559' },
        { label: 'Open Contact Form', href: '#contact' }
      ]
    },
    {
      id: 'technical_specs',
      patterns: [
        'spec', 'specs', 'technical', 'resolution', '4k', 'nits', 'lighting', 'night', 'floodlight',
        'lux', 'flex', 'vinyl', 'material', 'dimension', 'dimensions', 'size'
      ],
      reply: '<strong>Technical Standards & Production Specifications</strong>:<ul><li><strong>Digital LED Screens:</strong> Ultra-HD 4K resolution, 1200+ nits brightness, 60 FPS playback, and ambient lux sensor automated dimming.</li><li><strong>Static Mega Hoardings:</strong> 550 GSM heavy-duty frontlit flex vinyl, UV-cured fade-resistant inks, reinforced structural framing certified for wind loads.</li><li><strong>Night Illumination:</strong> 100% dusk-to-dawn warm-white commercial floodlights with automated timer relays and dual surge protection.</li></ul>',
      chips: [
        { label: 'Day / Night Demo', href: '#day-night' },
        { label: 'Download Spec Sheet', href: '#contact' },
        { label: 'WhatsApp Planning Desk', href: 'https://wa.me/919885335559' }
      ]
    },
    {
      id: 'why_brandvision',
      patterns: [
        'why', 'difference', 'advantage', 'broker', 'middleman', 'guarantee', 'proof', 'audit',
        'experience', 'trust'
      ],
      reply: '<span class="bv-msg-heading">The Brand Vision Media Advantage</span><ul><li><strong>Prime Corridors &amp; Direct Access:</strong> Curated high-impact arterial and transit media across prime South Indian business corridors.</li><li><strong>Zero-Failure Illumination:</strong> 100% lit every single night with dusk-to-dawn calibrated commercial illumination.</li><li><strong>Verified GPS Audits:</strong> Comprehensive date, time, and GPS-tagged photo audit proof delivered within 24 hours of live flight.</li><li><strong>Fast 2-Hour Turnaround:</strong> Direct coordination with our managing partner on site selection and proposals.</li></ul>',
      chips: [
        { label: 'Check Rate Card', href: '#contact' },
        { label: 'Browse Locations', href: '#locations' },
        { label: 'Chat on WhatsApp', href: 'https://wa.me/919885335559' }
      ]
    },
    {
      id: 'multicity_bangalore',
      patterns: [
        'bangalore', 'bengaluru', 'karnataka', 'multi city', 'multicity', 'other cities', 'other locations',
        'pan india', 'south india', 'multiple cities', 'expansion'
      ],
      reply: 'Brand Vision executes high-impact outdoor media campaigns across <strong>major cities of India</strong>, with our primary flagship inventory across <strong>Telangana and Andhra Pradesh</strong>, active media presence in <strong>Bengaluru (Karnataka)</strong>, and verified networks across key commercial metros. Our planning desk coordinates multi-city brand campaigns with single-window accountability, verified traffic metrics, and direct rates.',
      chips: [
        { label: 'Multi-City Plan Inquiry', href: '#contact' },
        { label: 'Browse Flagship Sites', href: '#locations' },
        { label: 'Talk to Managing Partner', prompt: 'Talk to Managing Partner' }
      ]
    }
  ];

  // Fallback response for unmapped queries
  const FALLBACK_REPLY = {
    reply: 'Our media planning desk can assist you with active site availability, technical production specifications, custom rate cards, or connecting directly with our Managing Partner Sri Kalapareddygari Sreedhar at <a href="tel:+919885335559" style="color: #ff8533; text-decoration: underline;">+91 98853 35559</a>.',
    chips: [
      { label: 'View Portfolio', href: '#locations' },
      { label: 'Chat on WhatsApp', href: 'https://wa.me/919885335559' }
    ]
  };

  // State management using sessionStorage
  const STORAGE_KEY = 'bv_ai_chat_history_v1';
  let chatHistory = [];

  try {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) {
      chatHistory = JSON.parse(saved);
    }
  } catch (err) {
    chatHistory = [];
  }

  function hideEmptyState() {
    if (emptyStateEl) emptyStateEl.style.display = 'none';
  }

  function showEmptyState() {
    if (emptyStateEl) emptyStateEl.style.display = 'flex';
  }

  // Toggle chat window open / close
  function setChatOpen(open) {
    if (open) {
      document.body.classList.add('has-chat-open');
      if (chatContainer) chatContainer.classList.add('is-open');
      launcher.style.display = 'none';
      launcher.setAttribute('aria-expanded', 'true');
      chatWindow.style.display = 'flex';
      chatWindow.classList.add('is-open');

      // If empty history, show modern empty state; else render saved messages
      if (chatHistory && chatHistory.length > 0) {
        hideEmptyState();
        renderSavedHistory();
      } else {
        showEmptyState();
      }
      setTimeout(() => chatInput && chatInput.focus(), 150);
    } else {
      document.body.classList.remove('has-chat-open');
      if (chatContainer) chatContainer.classList.remove('is-open');
      chatWindow.classList.remove('is-open');
      chatWindow.style.display = 'none';
      launcher.style.display = 'inline-flex';
      launcher.setAttribute('aria-expanded', 'false');
    }
  }

  launcher.addEventListener('click', () => {
    const isOpen = chatWindow.classList.contains('is-open');
    setChatOpen(!isOpen);
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => setChatOpen(false));
  }

  // Clear chat action
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      chatHistory = [];
      try {
        sessionStorage.removeItem(STORAGE_KEY);
      } catch (e) {}
      const rows = messagesEl.querySelectorAll('.bv-msg-row');
      rows.forEach((r) => r.remove());
      showEmptyState();
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && chatWindow.classList.contains('is-open')) {
      setChatOpen(false);
    }
  });

  // Close on click outside of chat window
  document.addEventListener('pointerdown', (e) => {
    if (!chatWindow.classList.contains('is-open')) return;
    if (!chatWindow.contains(e.target) && !launcher.contains(e.target)) {
      setChatOpen(false);
    }
  });

  // Handle Quick Prompt Pills (if present)
  if (quickBar) {
    quickBar.addEventListener('click', (e) => {
      const pill = e.target.closest('.bv-quick-pill');
      if (!pill) return;
      const prompt = pill.getAttribute('data-prompt') || pill.textContent.trim();
      handleUserSubmit(prompt);
    });
  }

  // Handle Starter Cards and Action Chip clicks inside messages
  messagesEl.addEventListener('click', (e) => {
    const starter = e.target.closest('.bv-starter-card');
    if (starter) {
      e.preventDefault();
      const prompt = starter.getAttribute('data-prompt') || starter.textContent.trim();
      handleUserSubmit(prompt);
      return;
    }

    const chip = e.target.closest('.bv-msg-chip');
    if (!chip) return;
    const prompt = chip.getAttribute('data-prompt');
    const href = chip.getAttribute('href');

    if (prompt) {
      e.preventDefault();
      handleUserSubmit(prompt);
    } else if (href && href.startsWith('#')) {
      e.preventDefault();
      const targetSec = document.querySelector(href);
      if (targetSec) {
        setChatOpen(false);
        targetSec.scrollIntoView({ behavior: 'smooth' });
      }
    }
  });

  // Handle Input submission
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = chatInput.value.trim();
      if (!text) return;
      chatInput.value = '';
      handleUserSubmit(text);
    });
  }

  function handleUserSubmit(userText) {
    hideEmptyState();
    // Render user message bubble
    renderUserMessage(userText);
    saveMessageToHistory('user', userText);

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    // Natural Language Matching Engine
    setTimeout(() => {
      removeTypingIndicator(typingIndicator);
      const match = findBestMatch(userText);
      renderBotResponse(match.reply, match.chips, true);
      saveMessageToHistory('bot', match.reply, match.chips);
    }, 550);
  }

  function renderUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'bv-msg-row bv-msg-user';

    const sender = document.createElement('div');
    sender.className = 'bv-msg-sender-label';
    sender.textContent = 'You';

    const bubble = document.createElement('div');
    bubble.className = 'bv-msg-bubble';
    bubble.textContent = text;

    const time = document.createElement('div');
    time.className = 'bv-msg-time';
    time.textContent = getCurrentTimeStr();

    row.appendChild(sender);
    row.appendChild(bubble);
    row.appendChild(time);

    messagesEl.appendChild(row);
    scrollMessagesToBottom();
  }

  function renderBotResponse(replyHtml, chips, shouldAnimate) {
    const row = document.createElement('div');
    row.className = 'bv-msg-row bv-msg-bot';

    const sender = document.createElement('div');
    sender.className = 'bv-msg-sender-label';
    sender.textContent = 'Media Planning Desk';

    const bubble = document.createElement('div');
    bubble.className = 'bv-msg-bubble';
    bubble.innerHTML = replyHtml;

    row.appendChild(sender);
    row.appendChild(bubble);

    if (chips && chips.length > 0) {
      const chipsWrap = document.createElement('div');
      chipsWrap.className = 'bv-msg-chips';

      chips.forEach((c) => {
        const chipEl = document.createElement(c.href ? 'a' : 'button');
        chipEl.className = 'bv-msg-chip';

        if (c.href) {
          chipEl.href = c.href;
          if (c.href.startsWith('http') || c.href.startsWith('tel:')) {
            chipEl.target = '_blank';
            chipEl.rel = 'noopener noreferrer';
          }
        }
        if (c.prompt) {
          chipEl.setAttribute('data-prompt', c.prompt);
          chipEl.type = 'button';
        }

        chipEl.innerHTML = `<span>${escapeHtml(c.label)}</span>${c.href && c.href.startsWith('http') ? SVG_EXTERNAL : SVG_ARROW}`;
        chipsWrap.appendChild(chipEl);
      });

      row.appendChild(chipsWrap);
    }

    const time = document.createElement('div');
    time.className = 'bv-msg-time';
    time.textContent = getCurrentTimeStr();
    row.appendChild(time);

    messagesEl.appendChild(row);
    if (row.offsetHeight > messagesEl.clientHeight * 0.6) {
      row.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      scrollMessagesToBottom();
    }
  }

  function showTypingIndicator() {
    const ind = document.createElement('div');
    ind.className = 'bv-msg-row bv-msg-bot bv-typing-row';
    ind.innerHTML = `
      <div class="bv-typing-indicator">
        <span class="bv-typing-dot"></span>
        <span class="bv-typing-dot"></span>
        <span class="bv-typing-dot"></span>
      </div>
    `;
    messagesEl.appendChild(ind);
    scrollMessagesToBottom();
    return ind;
  }

  function removeTypingIndicator(indicatorEl) {
    if (indicatorEl && indicatorEl.parentNode) {
      indicatorEl.parentNode.removeChild(indicatorEl);
    }
  }

  function scrollMessagesToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function getCurrentTimeStr() {
    const d = new Date();
    let h = d.getHours();
    const m = d.getMinutes().toString().padStart(2, '0');
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return `${h}:${m} ${ampm}`;
  }

  // Tokenization & Multi-Keyword NLP Scoring
  function findBestMatch(inputStr) {
    const clean = inputStr.toLowerCase().replace(/[^a-z0-9\s]/g, ' ');
    const tokens = clean.split(/\s+/).filter(Boolean);

    let bestScore = 0;
    let bestMatch = null;

    BV_KNOWLEDGE.forEach((item) => {
      let score = 0;

      item.patterns.forEach((pattern) => {
        const pClean = pattern.toLowerCase();
        // Exact substring match
        if (clean.includes(pClean)) {
          score += pClean.length * 2.5;
        }

        // Token match
        const pTokens = pClean.split(/\s+/);
        pTokens.forEach((pt) => {
          if (tokens.includes(pt)) {
            score += 4;
          }
        });
      });

      if (score > bestScore) {
        bestScore = score;
        bestMatch = item;
      }
    });

    if (bestMatch && bestScore >= 4) {
      return bestMatch;
    }

    return FALLBACK_REPLY;
  }

  function saveMessageToHistory(role, text, chips) {
    chatHistory.push({ role, text, chips, time: getCurrentTimeStr() });
    if (chatHistory.length > 30) {
      chatHistory = chatHistory.slice(-30);
    }
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
    } catch (e) {}
  }

  function renderSavedHistory() {
    messagesEl.innerHTML = '';
    chatHistory.forEach((msg) => {
      if (msg.role === 'user') {
        renderUserMessage(msg.text);
      } else {
        renderBotResponse(msg.text, msg.chips, false);
      }
    });
  }
}

/* ==========================================================================
   Corporate Document & Policies Modal Viewer (Blogs, Terms, Privacy, Sources)
   ========================================================================== */
function initDocViewer() {
  const modalOverlay = document.getElementById('modal-doc-viewer');
  if (!modalOverlay) return;

  const closeBtns = modalOverlay.querySelectorAll('#doc-modal-close, #doc-modal-close-btn-bottom');
  const tabBtns = modalOverlay.querySelectorAll('.doc-tab-btn');
  const tabPanes = modalOverlay.querySelectorAll('.doc-tab-pane');
  const modalBadge = document.getElementById('doc-modal-badge');
  const modalTitle = document.getElementById('doc-modal-title');
  const modalBody = document.getElementById('doc-modal-body');

  const TAB_META = {
    blogs: {
      badge: 'Media Articles & Insights',
      title: 'Industry Insights & Operational Standards'
    },
    terms: {
      badge: 'Commercial Terms',
      title: 'Outdoor Advertising Booking Terms & Conditions'
    },
    privacy: {
      badge: 'Privacy Notice',
      title: 'Corporate Privacy & Data Governance Policy'
    },
    sources: {
      badge: 'Attributions & Audits',
      title: 'Data Sources, Traffic Counts & Technical Citations'
    }
  };

  function switchTab(targetTab) {
    if (!TAB_META[targetTab]) targetTab = 'blogs';

    tabBtns.forEach(btn => {
      const isMatch = btn.getAttribute('data-tab-target') === targetTab;
      btn.classList.toggle('active', isMatch);
      btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
    });

    tabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === `pane-${targetTab}`);
    });

    if (modalBadge) modalBadge.textContent = TAB_META[targetTab].badge;
    if (modalTitle) modalTitle.textContent = TAB_META[targetTab].title;

    if (modalBody) modalBody.scrollTop = 0;
  }

  function openDocModal(targetTab) {
    switchTab(targetTab);
    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    // If navigation drawer is open, close it cleanly
    if (window.__bvCloseDrawer) {
      window.__bvCloseDrawer();
    } else {
      const drawerOverlay = document.getElementById('coral-drawer-overlay');
      if (drawerOverlay && drawerOverlay.classList.contains('active')) {
        drawerOverlay.classList.remove('active');
        drawerOverlay.setAttribute('aria-hidden', 'true');
        const toggleBtn = document.getElementById('coral-menu-toggle');
        if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
      }
    }
  }

  function closeDocModal() {
    modalOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Trigger buttons across bottom nav bar and navigation drawer
  document.querySelectorAll('[data-doc-target]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const target = trigger.getAttribute('data-doc-target');
      openDocModal(target);
    });
  });

  // Tab switching inside modal
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab-target');
      switchTab(target);
    });
  });

  // Close actions
  closeBtns.forEach(btn => {
    btn.addEventListener('click', closeDocModal);
  });

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      closeDocModal();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
      closeDocModal();
    }
  });

  // Deep-linking support via URL hash
  function checkHash() {
    const rawHash = window.location.hash.toLowerCase().replace('#', '');
    if (['blogs', 'terms', 'privacy', 'sources'].includes(rawHash)) {
      openDocModal(rawHash);
    }
  }

  window.addEventListener('hashchange', checkHash);
  checkHash();
}

/* --------------------------------------------------------------------------
   13. Resilient On-Site & DOOH Video Engine (Silent Autoplay, Toggle, Loop)
   -------------------------------------------------------------------------- */
function initAutoplayVideos() {
  const allVideos = document.querySelectorAll('video:not(#modal-video)');
  if (!allVideos.length) return;

  allVideos.forEach(vid => {
    vid.muted = true;
    vid.defaultMuted = true;
    vid.setAttribute('playsinline', '');
    vid.setAttribute('webkit-playsinline', '');
    vid.removeAttribute('controls');
    if (!vid.preload || vid.preload === 'none') {
      vid.preload = 'metadata';
    }
  });

  // Setup interactive controls on live video cards
  const liveCards = document.querySelectorAll('.live-video-card');
  liveCards.forEach(card => {
    const vid = card.querySelector('video');
    const wrap = card.querySelector('.live-video-media-wrap');
    const playBtn = card.querySelector('.live-video-play-btn');
    if (!vid || !wrap) return;

    let userPaused = false;

    const setPlaying = (playing) => {
      card.classList.toggle('is-playing', playing);
      card.classList.toggle('is-paused', !playing);
      if (playBtn) {
        playBtn.setAttribute('aria-label', playing ? 'Pause video' : 'Play video');
        const playText = playBtn.querySelector('.live-play-text');
        if (playText) {
          playText.textContent = playing ? 'Click to Pause' : 'Click to Play';
        }
      }
    };

    vid.addEventListener('play', () => setPlaying(true));
    vid.addEventListener('pause', () => setPlaying(false));

    const togglePlayback = (e) => {
      if (e) {
        if (e.target.closest('.live-video-expand-btn')) return;
        e.stopPropagation();
      }
      if (vid.paused) {
        userPaused = false;
        vid.muted = true;
        const p = vid.play();
        if (p !== undefined) p.catch(() => {});
      } else {
        userPaused = true;
        vid.pause();
      }
    };

    wrap.addEventListener('click', togglePlayback);
    if (playBtn) {
      playBtn.addEventListener('click', togglePlayback);
    }

    card._bvVideo = {
      vid,
      isUserPaused: () => userPaused,
      playAuto: () => {
        if (!userPaused && vid.paused) {
          vid.muted = true;
          const p = vid.play();
          if (p !== undefined) p.catch(() => {});
        }
      },
      pauseAuto: () => {
        if (!vid.paused) {
          vid.pause();
        }
      }
    };
  });

  // IntersectionObserver: start playback when cards enter viewport, pause when off-screen
  if ('IntersectionObserver' in window) {
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const card = entry.target;
        if (card._bvVideo) {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
            card._bvVideo.playAuto();
          } else {
            card._bvVideo.pauseAuto();
          }
        }
      });
    }, { threshold: [0, 0.2] });

    liveCards.forEach(card => cardObserver.observe(card));

    // Also observe any catalog video cards (e.g. Candeur DOOH card)
    const catalogCardsWithVideo = document.querySelectorAll('.catalog-card video');
    if (catalogCardsWithVideo.length) {
      const catalogVideoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const vid = entry.target;
          if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
            vid.muted = true;
            const p = vid.play();
            if (p !== undefined) p.catch(() => {});
          } else {
            vid.pause();
          }
        });
      }, { threshold: [0, 0.25] });

      catalogCardsWithVideo.forEach(vid => catalogVideoObserver.observe(vid));
    }
  }
}


