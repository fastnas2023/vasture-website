/* ============================================================
   扬州卓圣轩服装贸易有限公司 - Shared Interactions JS
   Handles: nav scroll state, mobile drawer, theme toggle,
            scroll reveal, form interactions, product filtering
   ============================================================ */
(function () {
  'use strict';

  // ---------- 1. Header scroll state ----------
  const header = document.querySelector('.site-header');
  const onScroll = () => {
    if (window.scrollY > 8) {
      header && header.classList.add('scrolled');
    } else {
      header && header.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- 2. Active Nav Highlight by data-dom-id ----------
  const pageMap = {
    'nav-home': 'home.html',
    'nav-products': 'products.html',
    'nav-factory': 'factory.html',
    'nav-services': 'services.html',
    'nav-about': 'about.html',
    'nav-blog': 'blog.html',
    'nav-resources': 'resources.html',
    'nav-contact': 'contact.html'
  };
  const currentFile = (location.pathname.split('/').pop() || 'home.html').toLowerCase();
  let activeKey = 'nav-home';
  for (const [key, file] of Object.entries(pageMap)) {
    if (file.toLowerCase() === currentFile) { activeKey = key; break; }
  }
  document.querySelectorAll(`[data-dom-id="${activeKey}"]`).forEach((el) => {
    if (el.tagName === 'A') el.classList.add('active');
  });

  // ---------- 2.5. Canonical navigation labels across legacy page headers ----------
  const navLabels = {
    'nav-home': '首页',
    'nav-products': '产品中心',
    'nav-factory': '供应链能力',
    'nav-services': 'OEM/ODM定制',
    'nav-about': '关于我们',
    'nav-blog': '行业资讯',
    'nav-resources': '采购资料',
    'nav-contact': '联系我们'
  };
  const primaryNavItems = [
    ['nav-home', 'home.html'],
    ['nav-products', 'products.html'],
    ['nav-services', 'services.html'],
    ['nav-factory', 'factory.html'],
    ['nav-about', 'about.html'],
    ['nav-resources', 'resources.html'],
    ['nav-blog', 'blog.html']
  ];
  document.querySelectorAll('.site-header nav, .mobile-drawer-nav').forEach((nav) => {
    const isMobile = nav.classList.contains('mobile-drawer-nav');
    const items = isMobile ? primaryNavItems.concat([['nav-contact', 'contact.html']]) : primaryNavItems;
    const existing = new Map(Array.from(nav.querySelectorAll(':scope > a')).map((el) => [el.dataset.domId, el]));
    items.forEach(([id, href]) => {
      let link = existing.get(id);
      if (!link) {
        link = document.createElement('a');
        link.dataset.domId = id;
        nav.appendChild(link);
      }
      const icon = link.querySelector('svg');
      link.href = href;
      link.textContent = navLabels[id] || id;
      if (icon && isMobile) link.append(' ', icon);
      link.classList.toggle('active', id === activeKey);
      // Re-append every canonical item so legacy headers are reordered as well
      // as relabeled. This keeps desktop and mobile navigation identical.
      nav.appendChild(link);
    });
    Array.from(nav.querySelectorAll(':scope > a')).forEach((link) => {
      if (!items.some(([id]) => id === link.dataset.domId)) link.remove();
    });
  });
  document.querySelectorAll('.site-header .lang-switch').forEach((group) => {
    const buttons = group.querySelectorAll('.lang-btn');
    if (buttons.length >= 2) {
      buttons[0].textContent = '中文';
      buttons[1].textContent = 'EN';
    }
    const divider = group.querySelector('.lang-divider');
    if (divider) divider.textContent = '|';
  });
  document.querySelectorAll('.site-header [data-theme-toggle]').forEach((el) => el.remove());
  document.querySelectorAll('.site-header a.cf-btn-primary, .site-header button.cf-btn-primary').forEach((el) => {
    const textNode = Array.from(el.childNodes).find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
    if (textNode) textNode.textContent = '获取报价';
  });
  document.querySelectorAll('.mobile-drawer [data-theme-toggle]').forEach((el) => el.remove());
  document.querySelectorAll('.mobile-drawer .lang-switch').forEach((el) => el.remove());

  // ---------- 3. Mobile Drawer ----------
  const drawer = document.querySelector('.mobile-drawer');
  const drawerBackdrop = document.querySelector('.drawer-backdrop');
  const openBtn = document.querySelector('[data-action="open-menu"]');
  const closeBtn = document.querySelector('[data-action="close-menu"]');
  const openDrawer = () => {
    drawer && drawer.classList.add('open');
    drawerBackdrop && drawerBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  const closeDrawer = () => {
    drawer && drawer.classList.remove('open');
    drawerBackdrop && drawerBackdrop.classList.remove('open');
    document.body.style.overflow = '';
  };
  openBtn && openBtn.addEventListener('click', openDrawer);
  closeBtn && closeBtn.addEventListener('click', closeDrawer);
  drawerBackdrop && drawerBackdrop.addEventListener('click', closeDrawer);
  drawer && drawer.querySelectorAll('a').forEach((a) => {
    a.addEventListener('click', () => setTimeout(closeDrawer, 120));
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) closeDrawer();
  });

  // ---------- 4. Theme Toggle (Light / Dark) ----------
  const rootEl = document.documentElement;
  const applyTheme = (t) => {
    if (t === 'dark') {
      rootEl.classList.add('dark');
      rootEl.setAttribute('data-theme', 'dark');
    } else {
      rootEl.classList.remove('dark');
      rootEl.setAttribute('data-theme', 'light');
    }
    try { localStorage.setItem('vasture-theme', t); } catch (_) {}
  };
  let saved = null;
  try { saved = localStorage.getItem('vasture-theme'); } catch (_) {}
  if (saved) applyTheme(saved);
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      applyTheme(rootEl.classList.contains('dark') ? 'light' : 'dark');
    });
  });

  // ---------- 5. Language Switch ----------
  document.querySelectorAll('.lang-switch').forEach((group) => {
    const buttons = Array.from(group.querySelectorAll('.lang-btn'));
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const lang = btn.getAttribute('data-lang');
        if (lang === 'en') {
          showToast('英文版页面正在制作中，当前先保留中文版。', 'info');
          return;
        }
        buttons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });

  // ---------- 6. Scroll Reveal (IntersectionObserver) ----------
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('visible'));
  }

  // ---------- 7. Smooth Anchor Offsets (for fixed header) ----------
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ---------- 8. Contact / Quote Form ----------
  const quoteForm = document.querySelector('[data-quote-form]') || document.querySelector('.form-card form');
  if (quoteForm) {
    // File upload preview
    const fileInput = quoteForm.querySelector('input[type="file"]');
    const uploadBox = quoteForm.querySelector('.file-upload');
    if (fileInput && uploadBox) {
      const fuText = uploadBox.querySelector('.fu-text');
      const originalText = fuText ? fuText.textContent : '';
      fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files[0]) {
          const f = fileInput.files[0];
          if (fuText) fuText.textContent = `已选择: ${f.name} (${formatSize(f.size)})`;
        } else if (fuText) {
          fuText.textContent = originalText;
        }
      });
    }
    // Submit handler (demo)
    quoteForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const required = quoteForm.querySelectorAll('[required]');
      let ok = true;
      required.forEach((f) => {
        if (!f.value || (f.tagName === 'SELECT' && f.disabled)) {
          ok = false;
          f.classList.add('field-error');
        } else {
          f.classList.remove('field-error');
        }
      });
      const submitBtn = quoteForm.querySelector('[type="submit"]');
      if (!ok) {
        showToast('请填写所有必填项', 'error');
        return;
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M22 12a10 10 0 0 1-10 10" stroke-linecap="round"/></svg> &nbsp; 提交中...';
      }
      setTimeout(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '提交成功 &nbsp;<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
        }
        showToast('已收到您的询价，我们将在24小时内与您联系！', 'success');
        quoteForm.reset();
        setTimeout(() => {
          if (submitBtn) submitBtn.innerHTML = '获取免费报价 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>';
        }, 2500);
      }, 1400);
    });
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / 1024 / 1024).toFixed(2) + 'MB';
  }

  // ---------- 9. Toast Notifications ----------
  function showToast(msg, type) {
    type = type || 'info';
    const colors = {
      success: 'background:#2D7A4E;color:#fff;',
      error:   'background:#C0392B;color:#fff;',
      info:    'background:var(--cf-primary);color:#fff;'
    };
    const el = document.createElement('div');
    el.textContent = msg;
    el.setAttribute('role', type === 'error' ? 'alert' : 'status');
    el.style.cssText = `position:fixed;top:88px;left:50%;transform:translateX(-50%) translateY(-12px);z-index:9999;
      padding:12px 22px;border-radius:10px;font-size:14px;font-weight:500;
      box-shadow:0 10px 30px rgba(0,0,0,0.18);opacity:0;transition:all 250ms cubic-bezier(.2,.8,.2,1);
      ${colors[type] || colors.info};max-width:90vw;`;
    document.body.appendChild(el);
    requestAnimationFrame(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(-50%) translateY(-12px)';
      setTimeout(() => el.remove(), 260);
    }, 3200);
  }

  // ---------- 10. Products Page Filter & Sort ----------
  const filterSidebar = document.querySelector('.filter-sidebar');
  if (filterSidebar) {
    const allCards = Array.from(document.querySelectorAll('.product-card'));
    const countEl = document.querySelector('.grid-toolbar__count strong');
    const sortSelect = document.querySelector('.sort-select');
    const resetBtn = document.querySelector('.filter-reset');

    function getFilters() {
      const out = { type: [], fabric: [], craft: [], scene: [] };
      ['type', 'fabric', 'craft', 'scene'].forEach((group) => {
        filterSidebar.querySelectorAll(`input[name="${group}"]:checked`).forEach((cb) => out[group].push(cb.value));
      });
      return out;
    }

    function apply() {
      const filters = getFilters();
      const sortBy = sortSelect ? sortSelect.value : 'recommend';
      const cards = allCards.slice();
      // simple keyword-based demo filter using data attributes or name text
      cards.forEach((card) => {
        let show = true;
        const hay = (card.textContent + (card.dataset.filters || '')).toLowerCase();
        const typeMap = {
          hoodie: '卫衣',
          workshirt: '工作衫',
          jacket: '夹克',
          vest: '背心',
          pants: '裤',
          coverall: '连体服',
          polo: 'polo',
          workwear: '工作服'
        };
        if (filters.type.length) {
          show = filters.type.some((v) => hay.includes(v) || hay.includes(typeMap[v] || ''));
        }
        if (show && filters.fabric.length) {
          const fm = { fleece: 'fleece', softshell: 'softshell', oxford: 'oxford', mesh: 'mesh' };
          show = filters.fabric.some((v) => hay.includes(v) || hay.includes(fm[v] || ''));
        }
        if (show && filters.craft.length) {
          const cm = { reflective: 'reflective', branding: 'branding', waterproof: 'waterproof', functional: 'functional' };
          show = filters.craft.some((v) => hay.includes(v) || hay.includes(cm[v] || ''));
        }
        if (show && filters.scene.length) {
          const sm = { safety: 'safety', outdoor: 'outdoor', business: 'business', project: 'project' };
          show = filters.scene.some((v) => hay.includes(v) || hay.includes(sm[v] || ''));
        }
        card.style.display = show ? '' : 'none';
      });

      const visible = cards.filter((c) => c.style.display !== 'none');
      if (sortBy === 'moq-asc' || sortBy === 'moq-desc') {
        const moqRe = /MOQ\s*(\d+)/i;
        visible.sort((a, b) => {
          const ma = (a.textContent.match(moqRe) || [])[1] || 9999;
          const mb = (b.textContent.match(moqRe) || [])[1] || 9999;
          return sortBy === 'moq-asc' ? ma - mb : mb - ma;
        });
        const grid = document.querySelector('.product-grid');
        if (grid) visible.forEach((c) => grid.appendChild(c));
      }
      if (countEl) countEl.textContent = visible.length;
    }

    filterSidebar.querySelectorAll('input[type="checkbox"]').forEach((cb) => cb.addEventListener('change', apply));
    sortSelect && sortSelect.addEventListener('change', apply);
    resetBtn && resetBtn.addEventListener('click', () => {
      filterSidebar.querySelectorAll('input[type="checkbox"]').forEach((cb) => { cb.checked = false; });
      if (sortSelect) sortSelect.value = 'recommend';
      apply();
      showToast('筛选已重置', 'info');
    });
  }

  // ---------- 11. Blog / Resources Pagination Tabs ----------
  document.querySelectorAll('[data-tabs]').forEach((wrap) => {
    const btns = wrap.querySelectorAll('[data-tab]');
    const panels = wrap.querySelectorAll('[data-panel]');
    btns.forEach((b) => {
      b.addEventListener('click', () => {
        const t = b.dataset.tab;
        btns.forEach((x) => x.classList.toggle('active', x === b));
        panels.forEach((p) => p.style.display = p.dataset.panel === t ? '' : 'none');
      });
    });
  });

  // ---------- 12. Expose some globals (optional debug) ----------
  window.VASTURE = { showToast };
})();
