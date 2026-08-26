/* ============================================================
   扬州卓圣轩服装贸易有限公司 - Shared Interactions JS
   Handles: nav scroll state, mobile drawer, theme toggle,
            scroll reveal, form interactions, product filtering
   ============================================================ */
(function () {
  'use strict';

  // Keep content visible if JavaScript is unavailable or an observer fails.
  // CSS uses this class to opt into the scroll-reveal enhancement only.
  document.documentElement.classList.add('js-enabled');

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

  // ---------- 1.5. Hero scene controls ----------
  const hero = document.querySelector('.hero');
  const heroSceneTabs = hero ? Array.from(hero.querySelectorAll('.hero-scene-control [data-hero-scene]')) : [];
  const heroSceneControl = hero ? hero.querySelector('.hero-scene-control') : null;
  const heroSceneCount = hero ? hero.querySelector('.hero-scene-control__count') : null;
  const heroEyebrowCopy = hero ? hero.querySelector('.hero-eyebrow-copy') : null;
  const heroPathPreviews = hero ? Array.from(hero.querySelectorAll('[data-hero-preview-scene]')) : [];
  const defaultHeroEyebrow = heroEyebrowCopy ? heroEyebrowCopy.textContent : '';
  const reduceHeroMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const heroSceneDuration = 5600;
  let heroSceneIndex = 0;
  let heroSceneTimer = null;

  if (hero && heroSceneTabs.length) {
    const stopHeroScenes = () => {
      if (heroSceneTimer) window.clearInterval(heroSceneTimer);
      heroSceneTimer = null;
    };
    const renderHeroScene = (index, restartProgress = false) => {
      heroSceneIndex = (index + heroSceneTabs.length) % heroSceneTabs.length;
      hero.dataset.activeScene = String(heroSceneIndex);
      heroSceneTabs.forEach((tab, tabIndex) => {
        tab.classList.remove('is-active');
        tab.setAttribute('aria-selected', String(tabIndex === heroSceneIndex));
      });
      if (restartProgress) void hero.offsetWidth;
      heroSceneTabs[heroSceneIndex].classList.add('is-active');
      if (heroSceneCount) heroSceneCount.textContent = `0${heroSceneIndex + 1} / 0${heroSceneTabs.length}`;
    };
    const startHeroScenes = () => {
      if (reduceHeroMotion) return;
      stopHeroScenes();
      heroSceneTimer = window.setInterval(() => renderHeroScene(heroSceneIndex + 1, true), heroSceneDuration);
    };

    renderHeroScene(0, true);
    startHeroScenes();
    heroSceneTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        renderHeroScene(Number(tab.dataset.heroScene || 0), true);
        startHeroScenes();
      });
    });
    // Only pause while the visitor is choosing a scene. Pausing on the whole
    // hero made a normal mouse position prevent any automatic rotation.
    heroSceneControl && heroSceneControl.addEventListener('mouseenter', stopHeroScenes);
    heroSceneControl && heroSceneControl.addEventListener('mouseleave', startHeroScenes);

    const previewBuyerPath = (path) => {
      stopHeroScenes();
      renderHeroScene(Number(path.dataset.heroPreviewScene || 0), true);
      if (heroEyebrowCopy) heroEyebrowCopy.textContent = path.dataset.heroPreviewCopy || defaultHeroEyebrow;
    };
    const resetBuyerPath = () => {
      if (heroEyebrowCopy) heroEyebrowCopy.textContent = defaultHeroEyebrow;
      startHeroScenes();
    };
    heroPathPreviews.forEach((path) => {
      path.addEventListener('mouseenter', () => previewBuyerPath(path));
      path.addEventListener('mouseleave', resetBuyerPath);
      path.addEventListener('focus', () => previewBuyerPath(path));
      path.addEventListener('blur', resetBuyerPath);
    });
  }

  // ---------- 2. Active Nav Highlight by data-dom-id ----------
  // WordPress renders its own archive/page URLs. Do not replace them with
  // legacy .html links when this shared script is loaded by the WP theme.
  const isWordPressTheme = document.body.classList.contains('wp-theme-vasture-b2b');
  if (!isWordPressTheme) {
  const pageMap = {
    'nav-home': 'index.html',
    'nav-products': 'products.html',
    'nav-factory': 'factory.html',
    'nav-services': 'services.html',
    'nav-about': 'about.html',
    'nav-blog': 'blog.html',
    'nav-resources': 'resources.html',
    'nav-contact': 'contact.html'
  };
  const currentFile = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  let activeKey = 'nav-home';
  if (location.pathname.includes('/product/')) activeKey = 'nav-products';
  for (const [key, file] of Object.entries(pageMap)) {
    if (activeKey === 'nav-products') break;
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
    ['nav-home', 'index.html'],
    ['nav-products', 'products.html'],
    ['nav-services', 'services.html'],
    ['nav-factory', 'factory.html'],
    ['nav-about', 'about.html'],
    ['nav-resources', 'resources.html'],
    ['nav-blog', 'blog.html']
  ];
  const navBase = location.pathname.includes('/product/') ? '../' : '';
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
      link.href = `${navBase}${href}`;
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
  }

  // ---------- 2.8. Social profile links ----------
  // Add the complete public profile URL here when each account is ready.
  // Empty values keep the matching footer icon visible but non-clickable.
  const SOCIAL_LINKS = {
    linkedin: '',
    facebook: '',
    instagram: '',
    tiktok: '',
    pinterest: '',
    youtube: ''
  };
  const socialLabels = {
    linkedin: 'LinkedIn',
    facebook: 'Facebook',
    instagram: 'Instagram',
    tiktok: 'TikTok',
    pinterest: 'Pinterest',
    youtube: 'YouTube'
  };
  document.querySelectorAll('[data-social]').forEach((icon) => {
    const platform = icon.dataset.social;
    const url = SOCIAL_LINKS[platform] || '';
    const label = socialLabels[platform] || platform;
    if (/^https?:\/\//i.test(url)) {
      icon.href = url;
      icon.target = '_blank';
      icon.rel = 'noopener noreferrer';
      icon.classList.remove('social-icon--placeholder');
      icon.removeAttribute('role');
      icon.removeAttribute('aria-disabled');
      icon.removeAttribute('tabindex');
      icon.setAttribute('aria-label', `${label} 官方账号（新窗口）`);
      icon.title = label;
    }
  });

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
    // Prefill the quote form when a product detail/listing CTA passes context.
    const query = new URLSearchParams(window.location.search);
    const productName = query.get('name');
    const productNeed = query.get('need');
    const productId = query.get('product');
    const requestedProductType = query.get('type');
    const productField = quoteForm.querySelector('#q-product');
    const descriptionField = quoteForm.querySelector('#q-desc');
    if (requestedProductType && productField && Array.from(productField.options).some((option) => option.value === requestedProductType)) {
      productField.value = requestedProductType;
    } else if (productId && productField) {
      fetch('data/products.json')
        .then((response) => response.ok ? response.json() : null)
        .then((catalogue) => {
          const selected = catalogue && catalogue.products && catalogue.products.find((item) => item.id === productId);
          if (selected && Array.from(productField.options).some((option) => option.value === selected.product_type)) {
            productField.value = selected.product_type;
          }
        })
        .catch(() => {});
    }
    if (productNeed && descriptionField) {
      descriptionField.value = productNeed;
    } else if (productName && descriptionField) {
      descriptionField.value = `咨询${productName}的ODM开发方案`;
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

  // ---------- 10. Temporary product favourites ----------
  const favouriteKey = 'vasture-product-favourites';
  let favourites = [];
  try { favourites = JSON.parse(localStorage.getItem(favouriteKey) || '[]'); } catch (_) { favourites = []; }
  const syncFavourites = () => {
    const saved = new Set(favourites);
    document.querySelectorAll('[data-favorite-id]').forEach((button) => {
      const active = saved.has(button.dataset.favoriteId);
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
      const icon = button.querySelector('span');
      if (icon) icon.textContent = active ? '♥' : '♡';
      if (button.classList.contains('product-detail__favorite')) button.lastChild.textContent = active ? ' 已收藏' : ' 收藏';
    });
  };
  document.querySelectorAll('[data-favorite-id]').forEach((button) => button.addEventListener('click', (event) => {
    event.preventDefault(); event.stopPropagation();
    const id = button.dataset.favoriteId;
    favourites = favourites.includes(id) ? favourites.filter((item) => item !== id) : [...favourites, id];
    try { localStorage.setItem(favouriteKey, JSON.stringify(favourites)); } catch (_) {}
    syncFavourites();
  }));
  syncFavourites();

  // ---------- 11. Products Page Filter & Sort ----------
  const filterSidebar = document.querySelector('.filter-sidebar');
  if (filterSidebar) {
    const allCards = Array.from(document.querySelectorAll('.product-card'));
    const countEl = document.querySelector('.grid-toolbar__count strong');
    const sortSelect = document.querySelector('.sort-select');
    const searchInput = document.querySelector('#product-search');
    const resetBtn = document.querySelector('.filter-reset');
    const emptyResetBtn = document.querySelector('.product-empty__reset');
    const emptyState = document.querySelector('.product-empty');
    const productGrid = document.querySelector('.product-grid');
    const pagination = document.querySelector('[data-product-pagination]');
    const paginationControls = document.querySelector('[data-product-pagination-controls]');
    const paginationStatus = document.querySelector('[data-product-pagination-status]');
    const filterCard = filterSidebar.querySelector('.filter-card');
    const mobileToggle = filterSidebar.querySelector('.filter-mobile-toggle');
    const selectionBox = filterSidebar.querySelector('[data-filter-selection]');
    const selectionList = filterSidebar.querySelector('[data-filter-selection-list]');
    const filterGroups = ['type', 'feature', 'material'];
    const pageSize = 24;
    let currentPage = 1;

    allCards.forEach((card, index) => {
      card._filterTokens = new Set((card.dataset.filters || '').toLowerCase().split(/\s+/).filter(Boolean));
      card._initialIndex = index;
    });

    mobileToggle && mobileToggle.addEventListener('click', () => {
      const isOpen = filterCard.classList.toggle('is-open');
      mobileToggle.setAttribute('aria-expanded', String(isOpen));
      mobileToggle.textContent = isOpen ? '收起筛选' : '展开筛选';
    });

    function getFilters() {
      const out = { type: [], feature: [], material: [] };
      filterGroups.forEach((group) => {
        filterSidebar.querySelectorAll(`input[name="${group}"]:checked`).forEach((cb) => out[group].push(cb.value));
      });
      if (out.type.includes('all')) out.type = [];
      return out;
    }

    function matchesFilters(card, filters, ignoredGroup) {
      return filterGroups.every((group) => {
        if (group === ignoredGroup || !filters[group].length) return true;
        return filters[group].some((value) => card._filterTokens.has(value));
      });
    }

    function matchesSearch(card) {
      const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
      if (!query) return true;
      const haystack = [card.dataset.sku, card.dataset.filters, card.querySelector('.product-card__cat')?.textContent, card.querySelector('.product-card__title')?.textContent, card.querySelector('.product-card__desc')?.textContent].join(' ').toLowerCase();
      return haystack.includes(query);
    }

    function updateFilterOptions(filters) {
      filterGroups.forEach((group) => {
        filterSidebar.querySelectorAll(`input[name="${group}"]`).forEach((input) => {
          let optionCount;
          if (group === 'type') {
            const candidateFilters = {};
            filterGroups.forEach((name) => { candidateFilters[name] = filters[name].slice(); });
            candidateFilters.type = input.value === 'all' ? [] : [input.value];
            optionCount = allCards.filter((card) => matchesFilters(card, candidateFilters)).length;
          } else {
            const candidateFilters = {};
            filterGroups.forEach((name) => { candidateFilters[name] = filters[name].slice(); });
            if (!input.checked) candidateFilters[group] = [...new Set([...candidateFilters[group], input.value])];
            optionCount = allCards.filter((card) => matchesFilters(card, candidateFilters)).length;
          }

          const option = input.closest('.filter-option');
          const optionCountEl = option && option.querySelector('.count');
          if (optionCountEl) optionCountEl.textContent = optionCount;
          const shouldDisable = optionCount === 0 && !input.checked;
          input.disabled = shouldDisable;
          option && option.classList.toggle('is-disabled', shouldDisable);
        });
      });
    }

    function filterLabel(input) {
      return input.closest('.filter-option')?.querySelector('.filter-option__label')?.textContent?.trim() || input.value;
    }

    function renderSelectedFilters(filters) {
      if (!selectionBox || !selectionList) return;
      const activeInputs = filterGroups.flatMap((group) => filters[group]
        .filter((value) => group !== 'type' || value !== 'all')
        .map((value) => filterSidebar.querySelector(`input[name="${group}"][value="${value}"]`))
        .filter(Boolean));
      const hasSearch = Boolean(searchInput?.value.trim());
      const hasActive = activeInputs.length > 0 || hasSearch;
      selectionBox.hidden = !hasActive;
      if (resetBtn) resetBtn.hidden = !hasActive;
      if (!hasActive) {
        selectionList.replaceChildren();
        return;
      }
      const fragment = document.createDocumentFragment();
      activeInputs.forEach((input) => {
        const tag = document.createElement('button');
        tag.type = 'button';
        tag.className = 'filter-selection__tag';
        tag.dataset.filterName = input.name;
        tag.dataset.filterValue = input.value;
        tag.setAttribute('aria-label', `移除筛选：${filterLabel(input)}`);
        tag.textContent = filterLabel(input);
        fragment.appendChild(tag);
      });
      if (hasSearch) {
        const tag = document.createElement('button');
        tag.type = 'button';
        tag.className = 'filter-selection__tag';
        tag.dataset.clearSearch = 'true';
        tag.setAttribute('aria-label', `清除搜索：${searchInput.value.trim()}`);
        tag.textContent = `搜索：${searchInput.value.trim()}`;
        fragment.appendChild(tag);
      }
      selectionList.replaceChildren(fragment);
    }

    function syncProductUrl() {
      const selectedType = filterSidebar.querySelector('input[name="type"]:checked');
      const url = new URL(window.location.href);
      if (selectedType && selectedType.value !== 'all') {
        url.searchParams.set('type', selectedType.value);
      } else {
        url.searchParams.delete('type');
      }
      if (currentPage > 1) {
        url.searchParams.set('page', String(currentPage));
      } else {
        url.searchParams.delete('page');
      }
      filterGroups.filter((group) => group !== 'type').forEach((group) => {
        const values = Array.from(filterSidebar.querySelectorAll(`input[name="${group}"]:checked`)).map((input) => input.value);
        if (values.length) url.searchParams.set(group, values.join(','));
        else url.searchParams.delete(group);
      });
      const query = searchInput?.value.trim();
      if (query) url.searchParams.set('q', query);
      else url.searchParams.delete('q');
      try {
        window.history.replaceState({}, '', url.href);
      } catch (error) {
        // Some browsers restrict history updates for pages opened directly with file://.
        // Filtering must continue even when the address bar cannot be updated.
      }
    }

    function pageButtons(pageCount) {
      if (pageCount <= 7) return Array.from({ length: pageCount }, (_, index) => index + 1);
      if (currentPage <= 4) return [1, 2, 3, 4, 5, '…', pageCount];
      if (currentPage >= pageCount - 3) return [1, '…', pageCount - 4, pageCount - 3, pageCount - 2, pageCount - 1, pageCount];
      return [1, '…', currentPage - 1, currentPage, currentPage + 1, '…', pageCount];
    }

    function renderPagination(matchedCount) {
      if (!pagination || !paginationControls || !paginationStatus) return;
      const pageCount = Math.max(1, Math.ceil(matchedCount / pageSize));
      pagination.hidden = matchedCount === 0 || pageCount === 1;
      paginationStatus.textContent = `第 ${currentPage} / ${pageCount} 页 · 共 ${matchedCount} 款`;
      if (pagination.hidden) return;

      const makeButton = (label, page, options = {}) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `product-pagination__button${options.primary ? ' product-pagination__button--page' : ''}${options.current ? ' is-current' : ''}`;
        button.textContent = label;
        button.disabled = Boolean(options.disabled);
        button.dataset.page = String(page);
        button.setAttribute('aria-label', options.ariaLabel || label);
        if (options.current) button.setAttribute('aria-current', 'page');
        return button;
      };

      const fragment = document.createDocumentFragment();
      fragment.appendChild(makeButton('首页', 1, { disabled: currentPage === 1, ariaLabel: '跳转到首页' }));
      fragment.appendChild(makeButton('上一页', currentPage - 1, { disabled: currentPage === 1, ariaLabel: '上一页' }));
      pageButtons(pageCount).forEach((page) => {
        if (page === '…') {
          const dots = document.createElement('span');
          dots.className = 'product-pagination__ellipsis';
          dots.textContent = '…';
          dots.setAttribute('aria-hidden', 'true');
          fragment.appendChild(dots);
          return;
        }
        fragment.appendChild(makeButton(String(page), page, { primary: true, current: page === currentPage, ariaLabel: `第 ${page} 页` }));
      });
      fragment.appendChild(makeButton('下一页', currentPage + 1, { disabled: currentPage === pageCount, ariaLabel: '下一页' }));
      fragment.appendChild(makeButton('末页', pageCount, { disabled: currentPage === pageCount, ariaLabel: '跳转到末页' }));
      paginationControls.replaceChildren(fragment);
    }

    function apply() {
      const filters = getFilters();
      const sortBy = sortSelect ? sortSelect.value : 'recommend';
      const cards = allCards.slice();
      if (sortBy === 'newest') {
        cards.sort((a, b) => (b.dataset.addedDate || '').localeCompare(a.dataset.addedDate || '') || a._initialIndex - b._initialIndex);
      } else if (sortBy === 'sku-asc') {
        cards.sort((a, b) => (a.dataset.sku || '').localeCompare(b.dataset.sku || '', undefined, { numeric: true }) || a._initialIndex - b._initialIndex);
      } else {
        cards.sort((a, b) => a._initialIndex - b._initialIndex);
      }
      if (productGrid) cards.forEach((card) => productGrid.appendChild(card));

      const matched = cards.filter((card) => matchesFilters(card, filters) && matchesSearch(card));
      const pageCount = Math.max(1, Math.ceil(matched.length / pageSize));
      currentPage = Math.min(Math.max(currentPage, 1), pageCount);
      const start = (currentPage - 1) * pageSize;
      const visible = new Set(matched.slice(start, start + pageSize));
      cards.forEach((card) => {
        const isCurrentPage = visible.has(card);
        card.style.display = isCurrentPage ? '' : 'none';
        // Pagination can reveal cards after the initial observer pass; keep
        // current-page catalogue content visible instead of leaving blank rows.
        if (isCurrentPage) card.classList.add('visible');
      });

      if (countEl) countEl.textContent = matched.length;
      if (productGrid) productGrid.hidden = matched.length === 0;
      if (emptyState) emptyState.hidden = matched.length !== 0;
      renderPagination(matched.length);
      updateFilterOptions(filters);
      renderSelectedFilters(filters);
    }

    function goToPage(page, scrollToResults = false) {
      currentPage = Number(page) || 1;
      apply();
      syncProductUrl();
      if (scrollToResults && productGrid) productGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    filterSidebar.querySelectorAll('input').forEach((input) => input.addEventListener('change', () => goToPage(1)));
    sortSelect && sortSelect.addEventListener('change', () => {
      goToPage(1);
    });
    searchInput && searchInput.addEventListener('input', () => { goToPage(1); });
    paginationControls && paginationControls.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-page]');
      if (!button || button.disabled) return;
      goToPage(button.dataset.page, true);
    });
    const requestedParams = new URLSearchParams(window.location.search);
    const requestedType = requestedParams.get('type');
    const requestedPage = Number(requestedParams.get('page'));
    if (requestedType) {
      const requestedRadio = Array.from(filterSidebar.querySelectorAll('input[name="type"]'))
        .find((radio) => radio.value === requestedType);
      if (requestedRadio) {
        requestedRadio.checked = true;
      } else {
        syncProductUrl();
      }
    }
    filterGroups.filter((group) => group !== 'type').forEach((group) => {
      const values = (requestedParams.get(group) || '').split(',').filter(Boolean);
      values.forEach((value) => {
        const input = filterSidebar.querySelector(`input[name="${group}"][value="${value}"]`);
        if (input) input.checked = true;
      });
    });
    if (searchInput && requestedParams.get('q')) searchInput.value = requestedParams.get('q');
    if (Number.isInteger(requestedPage) && requestedPage > 1) currentPage = requestedPage;

    function resetFilters(showMessage) {
      filterSidebar.querySelectorAll('input[type="checkbox"]').forEach((cb) => { cb.checked = false; });
      const allType = filterSidebar.querySelector('input[name="type"][value="all"]');
      if (allType) allType.checked = true;
      if (searchInput) searchInput.value = '';
      if (sortSelect) sortSelect.value = 'recommend';
      currentPage = 1;
      syncProductUrl();
      apply();
      if (showMessage) showToast('筛选已重置', 'info');
    }

    resetBtn && resetBtn.addEventListener('click', () => resetFilters(true));
    selectionList && selectionList.addEventListener('click', (event) => {
      const tag = event.target.closest('.filter-selection__tag');
      if (!tag) return;
      if (tag.dataset.clearSearch === 'true' && searchInput) {
        searchInput.value = '';
      } else {
        const input = filterSidebar.querySelector(`input[name="${tag.dataset.filterName}"][value="${tag.dataset.filterValue}"]`);
        if (input?.type === 'radio') {
          const allType = filterSidebar.querySelector('input[name="type"][value="all"]');
          if (allType) allType.checked = true;
        } else if (input) {
          input.checked = false;
        }
      }
      goToPage(1);
    });
    emptyResetBtn && emptyResetBtn.addEventListener('click', () => resetFilters(false));
    apply();
    syncProductUrl();
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

  // ---------- 12. Catalogue source-page lightbox ----------
  const catalogueLinks = document.querySelectorAll('[data-catalogue-lightbox]');
  if (catalogueLinks.length && typeof HTMLDialogElement !== 'undefined') {
    const lightbox = document.createElement('dialog');
    lightbox.className = 'catalogue-lightbox';
    lightbox.setAttribute('aria-label', '画册原页大图');
    lightbox.innerHTML = `
      <div class="catalogue-lightbox__panel">
        <button type="button" class="catalogue-lightbox__close" aria-label="关闭大图">×</button>
        <div class="catalogue-lightbox__image-wrap"><img alt="" /></div>
        <div class="catalogue-lightbox__caption"></div>
      </div>`;
    document.body.appendChild(lightbox);

    const lightboxImage = lightbox.querySelector('img');
    const lightboxCaption = lightbox.querySelector('.catalogue-lightbox__caption');
    const closeLightbox = () => lightbox.close();
    lightbox.querySelector('.catalogue-lightbox__close').addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox) closeLightbox();
    });

    catalogueLinks.forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const preview = link.querySelector('img');
        const figure = link.closest('figure');
        const caption = figure && figure.querySelector('figcaption');
        lightboxImage.src = link.href;
        lightboxImage.alt = preview ? preview.alt : '画册原页图';
        lightboxCaption.textContent = caption ? caption.textContent.replace(' · 点击可放大', '') : '画册原页参考';
        lightbox.showModal();
      });
    });
  }

  // ---------- 13. Product colour thumbnails ----------
  document.querySelectorAll('[data-product-colour-picker]').forEach((picker) => {
    const mainImage = document.querySelector('[data-product-colour-main]');
    const currentLabel = picker.querySelector('[data-product-colour-label]');
    const colourButtons = picker.querySelectorAll('[data-colour-src]');
    if (!mainImage || !colourButtons.length) return;

    colourButtons.forEach((button) => {
      button.addEventListener('click', () => {
        if (button.classList.contains('is-active')) return;
        mainImage.classList.add('is-switching');
        mainImage.src = button.dataset.colourSrc;
        mainImage.alt = button.dataset.colourAlt || mainImage.alt;
        if (currentLabel) currentLabel.textContent = button.dataset.colourLabel || '';
        colourButtons.forEach((item) => {
          const active = item === button;
          item.classList.toggle('is-active', active);
          item.setAttribute('aria-pressed', String(active));
        });
        if (mainImage.complete) mainImage.classList.remove('is-switching');
        else mainImage.addEventListener('load', () => mainImage.classList.remove('is-switching'), { once: true });
      });
    });
  });

  // ---------- 14. Expose some globals (optional debug) ----------
  window.VASTURE = { showToast };
})();
