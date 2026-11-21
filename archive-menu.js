/* Archive management drawer: move existing controls without cloning or replacing handlers. */
(() => {
  'use strict';
  function init() {
    if (document.getElementById('archiveMenuToggle')) return;
    const header = document.querySelector('header.top');
    const actions = header?.querySelector('.actions');
    if (!header || !actions) return;

    const css = document.createElement('style');
    css.textContent = `
      .archive-menu-toggle{display:inline-flex;align-items:center;justify-content:center;width:42px;height:40px;cursor:pointer;border:1px solid #dce1eb;border-radius:10px;background:#fff;color:#303b55;font-size:22px;line-height:1}
      .archive-menu-toggle:focus-visible,.archive-menu-close:focus-visible{outline:3px solid #5574d0;outline-offset:2px}
      .archive-menu-backdrop[hidden],.archive-menu-drawer[hidden]{display:none!important}
      .archive-menu-backdrop{position:fixed;inset:0;background:rgba(17,24,39,.32);z-index:10000}
      .archive-menu-drawer{position:fixed;top:0;right:0;height:100dvh;width:min(410px,92vw);background:#fff;box-shadow:-8px 0 30px rgba(0,0,0,.14);z-index:10001;overflow:auto;padding:20px;box-sizing:border-box;color:#253044}
      .archive-menu-heading{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:22px}
      .archive-menu-heading h2{font-size:20px;margin:0}
      .archive-menu-close{border:1px solid #dce1eb;background:#fff;border-radius:8px;padding:6px 12px;font-size:22px;cursor:pointer}
      .archive-menu-group{border-top:1px solid #e5e7eb;padding:18px 0}
      .archive-menu-group h3{font-size:14px;margin:0 0 12px}
      .archive-menu-group .archive-menu-items{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start}
      .archive-menu-drawer #syncPanel{display:block!important;margin:0!important;padding:0!important;border:0!important;box-shadow:none!important;background:transparent!important}
      .archive-menu-drawer #syncControls{display:flex;flex-wrap:wrap;gap:8px}
      .archive-menu-drawer .hint,.archive-menu-drawer p{overflow-wrap:anywhere}
      body.archive-menu-open{overflow:hidden}
      @media(max-width:650px){.archive-menu-drawer{width:min(410px,96vw);padding:16px}}
    `;
    document.head.append(css);

    const toggle = document.createElement('button');
    toggle.id = 'archiveMenuToggle';
    toggle.className = 'archive-menu-toggle';
    toggle.type = 'button';
    toggle.textContent = '☰';
    toggle.setAttribute('aria-label', '관리 메뉴 열기');
    toggle.setAttribute('aria-controls', 'archiveMenuDrawer');
    toggle.setAttribute('aria-expanded', 'false');

    const backdrop = document.createElement('div');
    backdrop.className = 'archive-menu-backdrop';
    backdrop.hidden = true;
    const drawer = document.createElement('aside');
    drawer.className = 'archive-menu-drawer';
    drawer.id = 'archiveMenuDrawer';
    drawer.setAttribute('aria-label', '관리 메뉴');
    drawer.hidden = true;
    drawer.innerHTML = `<div class="archive-menu-heading"><h2>관리 메뉴</h2><button class="archive-menu-close" type="button" aria-label="메뉴 닫기">×</button></div><section class="archive-menu-group"><h3>사이트 설정</h3><div class="archive-menu-items" id="archiveMenuSettings"></div></section><section class="archive-menu-group"><h3>백업 관리</h3><div class="archive-menu-items" id="archiveMenuBackup"></div></section><section class="archive-menu-group" id="archiveMenuCloud"><h3>클라우드 동기화</h3></section>`;
    document.body.append(backdrop, drawer);

    const settings = drawer.querySelector('#archiveMenuSettings');
    const backup = drawer.querySelector('#archiveMenuBackup');
    const cloud = drawer.querySelector('#archiveMenuCloud');
    const syncPanel = document.getElementById('syncPanel');
    if (syncPanel) cloud.appendChild(syncPanel);
    else cloud.hidden = true;

    // Move original DOM elements, preserving their IDs, events, state and data bindings.
    const move = el => {
      if (el === toggle || el.tagName === 'INPUT') return;
      const label = `${el.id} ${el.textContent}`.toLowerCase();
      (label.includes('backup') || label.includes('export') || label.includes('import') ? backup : settings).appendChild(el);
    };
    Array.from(actions.children).forEach(move);
    // Keep the hidden import file input in the document, so its original event handlers work.
    actions.appendChild(toggle);

    const setOpen = open => {
      drawer.hidden = !open;
      backdrop.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('archive-menu-open', open);
      if (open) drawer.querySelector('.archive-menu-close').focus();
      else toggle.focus();
    };
    toggle.addEventListener('click', () => setOpen(drawer.hidden));
    backdrop.addEventListener('click', () => setOpen(false));
    drawer.querySelector('.archive-menu-close').addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !drawer.hidden) setOpen(false);
    });
    // Dynamically added header buttons (e.g. font or API settings) are moved as well.
    const observer = new MutationObserver(records => {
      records.forEach(record => record.addedNodes.forEach(node => {
        if (node.nodeType === 1 && node !== toggle) move(node);
      }));
    });
    observer.observe(actions, {childList:true});
    // Do not change button handlers; modal and sync actions remain bound to originals.
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
