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
      .archive-menu-backdrop[hidden],.archive-menu-drawer[hidden]{display:none!important}.archive-menu-drawer.archive-menu-inactive{pointer-events:none}.archive-menu-drawer.archive-menu-inactive>*{opacity:.45;filter:grayscale(.3);transition:opacity .15s}@media(max-width:650px){html body.archive-menu-open .cbh-api-overlay{right:0!important;z-index:11020!important}html body.archive-menu-open .cbh-api-panel{max-width:calc(100vw - 28px)!important}}
      .archive-menu-backdrop{position:fixed;inset:0;background:rgba(17,24,39,.32);z-index:10000}
      .archive-menu-drawer{position:fixed;top:0;right:0;height:100dvh;width:min(410px,92vw);background:#fff;box-shadow:-8px 0 30px rgba(0,0,0,.14);z-index:10001;overflow:auto;padding:20px;box-sizing:border-box;color:#253044}
      /* ARCHIVE_LEFT_PANE_MODAL_CENTER_V1 */
      /* While the management drawer is open, center modals only in the remaining left area. */
      body.archive-menu-open #modalRoot .overlay,
      body.archive-menu-open .cbh-api-overlay{
        right:min(410px,92vw)!important;
        box-sizing:border-box;
      }
      body.archive-menu-open #modalRoot .overlay{
        z-index:10002!important;
      }
      body.archive-menu-open #modalRoot .dialog,
      body.archive-menu-open .cbh-api-panel{
        max-width:100%;
        box-sizing:border-box;
      }
      @media(max-width:650px){
        body.archive-menu-open #modalRoot .overlay,
        body.archive-menu-open .cbh-api-overlay{
          right:min(410px,96vw)!important;
        }
      }
      .archive-menu-heading{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:22px}
      .archive-menu-heading h2{font-size:20px;margin:0}
      .archive-menu-close{border:1px solid #dce1eb;background:#fff;border-radius:8px;padding:6px 12px;font-size:22px;cursor:pointer}
      .archive-menu-group{border-top:1px solid #e5e7eb;padding:18px 0}
      .archive-menu-group h3{font-size:14px;margin:0 0 12px}
      .archive-menu-group .archive-menu-items{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start}
      .archive-menu-drawer #syncPanel{display:block!important;margin:0!important;padding:0!important;border:0!important;box-shadow:none!important;background:transparent!important}
      .archive-menu-drawer #syncControls{display:flex;flex-wrap:wrap;gap:8px}
      .archive-menu-drawer .hint,.archive-menu-drawer p{overflow-wrap:anywhere}
      body.archive-menu-open #modalRoot .overlay{z-index:10010!important}
      body.archive-menu-open{overflow:hidden}
      @media(max-width:650px){.archive-menu-drawer{width:min(410px,96vw);padding:16px}}
    `;
    // Font Settings popup only: 90% text and button sizing; preserve dialog width/position.
    css.textContent += `
      /* FONT_SETTINGS_TEXT_BUTTONS_90_V1 */
      .font-dialog { font-size: 90% !important; }
      .font-dialog h2 { font-size: 17.1px !important; }
      .font-dialog h3 { font-size: 90% !important; }
      .font-dialog .btn,
      .font-dialog button,
      .font-dialog input,
      .font-dialog select,
      .font-dialog textarea,
      .font-dialog label { font-size: 90% !important; }
      .font-dialog .btn,
      .font-dialog button { padding: 0.9em 1.0em; }
      .font-dialog .font-section-tabs button { padding: 0.65em 0.75em; }
    `;
    document.head.append(css);

    // CLOUD_BUTTONS_MATCH_BACKUP_V1: CSS only; original buttons and listeners remain intact.
    const cloudButtonsLayoutStyle = document.createElement('style');
    cloudButtonsLayoutStyle.textContent = `
      /* CLOUD_BUTTONS_MATCH_BACKUP_V1 */
      .archive-menu-drawer #syncControls {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        width: 100% !important;
      }
      .archive-menu-drawer #syncControls > button,
      .archive-menu-drawer #syncControls > .btn,
      .archive-menu-drawer #syncControls > [role="button"] {
        display: inline-flex !important;
        width: fit-content !important;
        max-width: 100% !important;
        flex: 0 0 auto !important;
        align-self: center !important;
        justify-content: center !important;
        white-space: normal !important;
        text-align: center !important;
      }
      .archive-menu-drawer #syncControls > :not(button):not(.btn):not([role="button"]) {
        max-width: 100% !important;
      }
      /* If sync code wraps buttons in rows, make each row a vertical stack too. */
      .archive-menu-drawer #syncControls > div:has(> button) {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 8px !important;
        width: 100% !important;
      }
      .archive-menu-drawer #syncControls > div > button {
        width: fit-content !important;
        max-width: 100% !important;
        align-self: center !important;
        flex: 0 0 auto !important;
      }
    `;
    document.head.append(cloudButtonsLayoutStyle);


    /* font-popup-fixed-size-20261121 */
    const fontPopupSizeStyle = document.createElement('style');
    fontPopupSizeStyle.id = 'archiveFontPopupFixedSize';
    fontPopupSizeStyle.textContent = `
      #modalRoot .overlay:has(.font-dialog) {
        padding: 16px;
      }
      #modalRoot .font-dialog {
        width: min(760px, calc(100vw - 32px)) !important;
        height: min(610px, calc(100dvh - 32px)) !important;
        max-height: calc(100dvh - 32px) !important;
        box-sizing: border-box;
        overflow-y: auto !important;
        overflow-x: hidden;
        overscroll-behavior: contain;
      }
      #modalRoot .font-dialog .font-head {
        position: sticky;
        top: -22px;
        z-index: 2;
        background: white;
        padding: 22px 0 12px;
        margin-top: -22px;
        border-bottom: 1px solid #e5e7eb;
      }
      @media (max-width: 650px) {
        #modalRoot .font-dialog .font-head {
          top: -22px;
        }
      }
    `;
    document.head.append(fontPopupSizeStyle);

    /* font-popup-align-registration-20261121 */
    const fontPopupNarrowStyle = document.createElement('style');
    fontPopupNarrowStyle.id = 'archiveFontPopupNarrow';
    fontPopupNarrowStyle.textContent = `
      #modalRoot .font-dialog {
        width: min(640px, calc(100vw - 32px)) !important;
        max-width: calc(100vw - 32px) !important;
      }
    `;
    document.head.append(fontPopupNarrowStyle);



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
    drawer.innerHTML = `<div class="archive-menu-heading"><h2>관리 메뉴</h2><button class="archive-menu-close" type="button" aria-label="메뉴 닫기">×</button></div><section class="archive-menu-group"><h3>사이트 설정</h3><div class="archive-menu-items" id="archiveMenuSettings"></div></section><section class="archive-menu-group"><h3>백업 관리</h3><div class="archive-menu-items" id="archiveMenuBackup"></div></section><section class="archive-menu-group" id="archiveMenuCloud"></section>`;
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
      // top-folder-create-modal-v1: 상단 '+ 폴더 생성' 버튼은 헤더에 유지
      if (el.id === 'openFolderCreate') return;
      const label = `${el.id} ${el.textContent}`.toLowerCase();
      (label.includes('backup') || label.includes('export') || label.includes('import') ? backup : settings).appendChild(el);
    };
    Array.from(actions.children).forEach(move);
    // Keep the hidden import file input in the document, so its original event handlers work.

    // guest-header-label-v2
    if (document.querySelector('script[src*="guest-app"]') ||
        window.SCRAP_GUEST_MODE === true) {
      const oldGuestLabel = actions.querySelector('span');
      if (oldGuestLabel && oldGuestLabel.textContent.includes('GUEST')) {
        oldGuestLabel.style.display = 'none';
      }

      const guestLabel = document.createElement('span');
      guestLabel.textContent = 'GUEST · 읽기 전용';
      guestLabel.style.cssText =
        'display:inline-block;white-space:nowrap;font-size:12px;' +
        'font-weight:700;color:#455abf;flex-shrink:0;';

      actions.appendChild(guestLabel);
      actions.style.display = 'flex';
      actions.style.alignItems = 'center';
      actions.style.justifyContent = 'flex-end';
      actions.style.flexWrap = 'nowrap';
      actions.style.gap = '12px';
      actions.style.marginLeft = 'auto';
    }

    actions.appendChild(toggle);

    const setOpen = open => {
      if (open) {
        for (const id of ['fontSettingsBtn', 'cbhApiSettingsBtn']) {
          const button = document.getElementById(id);
          if (button && button.parentElement !== settings) {
            settings.appendChild(button);
          }
        }
      }
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

    // menu-platforms-20261123: 설정 팝업이 열려 있는 동안 메뉴는 닫지 않고 비활성화만 함
    const popupOpen = () => Boolean(document.querySelector('#modalRoot .overlay') || document.getElementById('cbhApiOverlay'));
    const syncInactive = () => {
      const inactive = !drawer.hidden && popupOpen();
      drawer.classList.toggle('archive-menu-inactive', inactive);
      if (inactive) drawer.setAttribute('inert', '');
      else drawer.removeAttribute('inert');
    };
    new MutationObserver(syncInactive).observe(document.body, {childList: true});
    const modalRoot = document.getElementById('modalRoot');
    if (modalRoot) new MutationObserver(syncInactive).observe(modalRoot, {childList: true});
    new MutationObserver(syncInactive).observe(drawer, {attributes: true, attributeFilter: ['hidden']});
    // Esc: 팝업이 열려 있으면 팝업만 닫히고 메뉴는 유지 (팝업 처리보다 먼저 상태 확인)
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !drawer.hidden && !popupOpen()) setOpen(false);
    }, true);
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

  /* FONT_DIALOG_EDGE_ALIGN_V1 */
  (() => {
    function align() {
      const dialog = document.querySelector('#modalRoot .font-dialog');
      const first = dialog?.querySelector('#font-tab-button-1');
      const third = dialog?.querySelector('#font-tab-button-3');
      const close = dialog?.querySelector('.font-head [data-close]');
      if (!first || !third || !close) return;
      const d = dialog.getBoundingClientRect();
      const a = first.getBoundingClientRect();
      const b = third.getBoundingClientRect();
      if (!d.width || !a.width || !b.width) return;
      const left = a.left - d.left;
      const width = Math.ceil(b.right - a.left + 2 * left);
      if (width < 320) return;
      dialog.style.setProperty('box-sizing', 'border-box', 'important');
      dialog.style.setProperty('width', 'min(' + width + 'px, 96vw)', 'important');
      dialog.style.setProperty('max-width', '96vw', 'important');
      close.style.setProperty('margin-right', '0', 'important');
    }
    let pending = false;
    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; align(); });
    }
    function start() {
      const root = document.getElementById('modalRoot');
      if (root) new MutationObserver(schedule).observe(root, {childList:true});
      schedule();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
    window.addEventListener('resize', schedule);
  })();


  /* ARCHIVE_MENU_ONE_BUTTON_PER_ROW_V1 */
  (() => {
    const style = document.createElement('style');
    style.textContent = `
      .archive-menu-drawer .archive-menu-items,
      .archive-menu-drawer #syncControls {
        display:flex!important;
        flex-direction:column!important;
        flex-wrap:nowrap!important;
        align-items:flex-start!important;
        gap:8px!important;
      }
      .archive-menu-drawer .archive-menu-items > :is(button,a,[role="button"]),
      .archive-menu-drawer #syncControls > :is(button,a,[role="button"]) {
        display:inline-flex!important;
        flex:0 0 auto!important;
        width:max-content!important;
        max-width:100%!important;
        box-sizing:border-box!important;
        white-space:normal!important;
        text-align:left;
      }
      /* Other cloud actions, such as guest sign-in, remain on separate lines. */
      .archive-menu-drawer #archiveMenuCloud #syncPanel button {
        max-width:100%;
        box-sizing:border-box;
      }
      .archive-menu-drawer #archiveMenuCloud #syncPanel button:not(#syncControls button) {
        display:block;
        margin-bottom:8px;
      }
      .archive-menu-drawer.archive-menu-compact {
        padding-top:12px!important;
        padding-bottom:12px!important;
      }
      .archive-menu-drawer.archive-menu-compact .archive-menu-heading {
        margin-bottom:12px!important;
      }
      .archive-menu-drawer.archive-menu-compact .archive-menu-group {
        padding-top:10px!important;
        padding-bottom:10px!important;
      }
      .archive-menu-drawer.archive-menu-compact .archive-menu-items,
      .archive-menu-drawer.archive-menu-compact #syncControls {
        gap:5px!important;
      }
      .archive-menu-drawer.archive-menu-compact button {
        padding-top:5px!important;
        padding-bottom:5px!important;
        font-size:0.94em!important;
      }
    `;
    document.head.appendChild(style);
    let scheduled = false;
    const update = () => {
      scheduled = false;
      const drawer = document.getElementById('archiveMenuDrawer');
      if (!drawer || drawer.hidden) return;
      drawer.classList.remove('archive-menu-compact');
      if (drawer.scrollHeight > drawer.clientHeight + 2) {
        drawer.classList.add('archive-menu-compact');
      }
    };
    const schedule = () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(update);
    };
    const start = () => {
      const drawer = document.getElementById('archiveMenuDrawer');
      if (!drawer) return;
      new MutationObserver(schedule).observe(drawer, {attributes:true, attributeFilter:['hidden'], childList:true, subtree:true, characterData:true});
      window.addEventListener('resize', schedule);
      schedule();
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
  })();

})();


/* ARCHIVE_CLOUD_ROWS_V2: only presentation; original event handlers stay attached. */
(() => {
  const style = document.createElement('style');
  style.textContent = `
    .archive-menu-drawer #syncControls {
      display:flex!important;
      flex-direction:column!important;
      flex-wrap:nowrap!important;
      align-items:flex-start!important;
      gap:8px!important;
    }
    .archive-menu-drawer #syncControls > * {
      flex:0 0 auto!important;
      width:max-content!important;
      max-width:100%!important;
      box-sizing:border-box!important;
      margin-left:0!important;
      margin-right:0!important;
    }
    .archive-menu-drawer #syncControls > button,
    .archive-menu-drawer #syncControls > a,
    .archive-menu-drawer #syncControls > [role="button"] {
      display:block!important;
      white-space:normal!important;
      text-align:left;
    }
    .archive-menu-drawer #syncPanel .archive-cloud-break {
      display:block;
    }
    .archive-menu-drawer #syncPanel .hint,
    .archive-menu-drawer #syncPanel p {
      line-height:1.6;
    }
    .archive-menu-drawer.archive-menu-cloud-compact #syncControls {
      gap:5px!important;
    }
    .archive-menu-drawer.archive-menu-cloud-compact #syncControls button {
      padding:5px 9px!important;
      font-size:0.94em!important;
    }
  `;
  document.head.appendChild(style);

  // Only split at the phrases marked in the screenshot; never replace entire
  // nodes or their handlers. This also supports status text that updates later.
  const splitBefore = [
    '다른 기기의 수정이 있다면',
    '기존 Supabase는',
    '저장 시 업로드',
    'Google Drive 실제',
  ];
  const formatHints = panel => {
    const targets = panel.querySelectorAll('.hint, p');
    targets.forEach(el => {
      if (el.dataset.archiveCloudFormatted === 'true') return;
      if (el.children.length) return;
      const original = el.textContent || '';
      const matches = splitBefore.filter(phrase => original.includes(phrase));
      if (!matches.length) return;
      const parts = [{text: original, breakBefore:false}];
      for (const phrase of matches) {
        const idx = parts.findIndex(part => part.text.includes(phrase));
        if (idx < 0) continue;
        const part = parts[idx];
        const at = part.text.indexOf(phrase);
        if (at <= 0) continue;
        parts.splice(idx, 1,
          {text:part.text.slice(0,at).trimEnd(), breakBefore:part.breakBefore},
          {text:part.text.slice(at).trimStart(), breakBefore:true});
      }
      if (parts.length === 1) return;
      el.replaceChildren();
      parts.forEach(part => {
        if (part.breakBefore) el.appendChild(document.createElement('br'));
        el.appendChild(document.createTextNode(part.text));
      });
      el.dataset.archiveCloudFormatted = 'true';
    });
  };
  let queued = false;
  const update = () => {
    queued = false;
    const drawer = document.getElementById('archiveMenuDrawer');
    const panel = document.getElementById('syncPanel');
    if (!drawer || !panel || drawer.hidden) return;
    formatHints(panel);
    drawer.classList.remove('archive-menu-cloud-compact');
    if (drawer.scrollHeight > drawer.clientHeight + 2)
      drawer.classList.add('archive-menu-cloud-compact');
  };
  const queue = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(update);
  };
  const init = () => {
    const drawer = document.getElementById('archiveMenuDrawer');
    const panel = document.getElementById('syncPanel');
    if (!drawer || !panel) return;
    new MutationObserver(queue).observe(drawer, {
      attributes:true, attributeFilter:['hidden'],
      childList:true, subtree:true, characterData:true
    });
    window.addEventListener('resize', queue);
    queue();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();


/* ARCHIVE_MENU_CENTER_80_V1: visual-only; preserve existing controls and handlers. */
(() => {
  const css = document.createElement('style');
  css.setAttribute('data-archive-menu-center-80', '');
  css.textContent = `
    /* Center the entire menu vertically when there is room; retain scrolling if not. */
    .archive-menu-drawer {
      display:flex!important;
      flex-direction:column!important;
      justify-content:safe center!important;
      overflow-y:auto!important;
      overflow-x:hidden!important;
      overscroll-behavior:contain;
    }
    .archive-menu-drawer[hidden] { display:none!important; }
    .archive-menu-drawer .archive-menu-heading,
    .archive-menu-drawer .archive-menu-group {
      flex:0 0 auto;
      width:100%;
      min-width:0;
    }
    /* Keep section titles and status copy readable, center their content. */
    .archive-menu-drawer .archive-menu-group {
      text-align:center!important;
    }
    .archive-menu-drawer .archive-menu-items,
    .archive-menu-drawer #syncControls {
      display:flex!important;
      flex-direction:column!important;
      flex-wrap:nowrap!important;
      align-items:center!important;
      justify-content:center!important;
      gap:7px!important;
      width:100%!important;
    }
    /* 0.8x button font size and box dimensions: scale the rendered control,
       while reserving 80% of its original layout height to avoid large gaps. */
    .archive-menu-drawer .archive-menu-items > button,
    .archive-menu-drawer .archive-menu-items > a,
    .archive-menu-drawer #syncControls > button,
    .archive-menu-drawer #syncControls > a,
    .archive-menu-drawer #syncControls > [role="button"] {
      font-size:80%!important;
      padding:6px 10px!important;
      width:max-content!important;
      max-width:100%!important;
      min-height:0!important;
      margin:0!important;
      line-height:1.3!important;
      box-sizing:border-box!important;
      white-space:normal!important;
      text-align:center!important;
    }
    .archive-menu-drawer #syncPanel {
      text-align:center!important;
      width:100%!important;
    }
    .archive-menu-drawer #syncPanel .hint,
    .archive-menu-drawer #syncPanel p {
      text-align:center!important;
      overflow-wrap:anywhere;
    }
    /* Keep the close button at the heading's right edge. */
    .archive-menu-drawer .archive-menu-heading {
      justify-content:space-between!important;
    }
    @media (max-height:700px) {
      .archive-menu-drawer .archive-menu-group { padding-top:10px!important; padding-bottom:10px!important; }
      .archive-menu-drawer .archive-menu-heading { margin-bottom:10px!important; }
    }
  `;
  document.head.appendChild(css);
})();


/* ARCHIVE_CLOUD_BUTTONS_SINGLE_COLUMN_V1
   Visual-only override: keep original button elements and event handlers. */
(() => {
  const style = document.createElement('style');
  style.setAttribute('data-archive-cloud-single-column', '');
  style.textContent = `
    /* Sync action buttons were inside a nested row, unlike the upper controls. */
    #archiveMenuDrawer #syncControls,
    #archiveMenuDrawer #syncPanel #syncControls {
      display: flex !important;
      flex-direction: column !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 7px !important;
      width: 100% !important;
    }
    #archiveMenuDrawer #syncControls > *,
    #archiveMenuDrawer #syncControls button,
    #archiveMenuDrawer #syncControls a,
    #archiveMenuDrawer #syncControls [role="button"] {
      flex: 0 0 auto !important;
      align-self: center !important;
      width: max-content !important;
      max-width: 100% !important;
      min-width: 0 !important;
      margin: 0 !important;
      box-sizing: border-box !important;
    }
    #archiveMenuDrawer #syncControls button,
    #archiveMenuDrawer #syncControls a,
    #archiveMenuDrawer #syncControls [role="button"] {
      font-size: 80% !important;
      padding: 6px 10px !important;
      min-height: 0 !important;
      line-height: 1.3 !important;
      white-space: normal !important;
      text-align: center !important;
    }
  `;
  document.head.appendChild(style);
})();
