#!/usr/bin/env python3
"""Cloud section vertical button layout and controlled text breaks."""
from pathlib import Path
from datetime import datetime
import shutil

path = Path(__file__).resolve().parent / 'archive-menu.js'
if not path.exists():
    raise SystemExit('archive-menu.js 파일이 없습니다. 패치를 동일한 폴더에 업로드해 주세요.')
src = path.read_text(encoding='utf-8')
marker = 'ARCHIVE_CLOUD_ROWS_V2'
if marker in src:
    raise SystemExit('이미 적용된 패치입니다. 중복 적용하지 않았습니다.')
if 'archiveMenuCloud' not in src or 'archiveMenuDrawer' not in src:
    raise SystemExit('기존 메뉴 구조를 확인할 수 없어 파일을 변경하지 않았습니다.')

addon = r'''
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
      if (el.querySelector('.archive-cloud-break')) return;
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
'''
# Fix potential repeated formatting on subsequent mutation notifications.
addon = addon.replace("if (el.querySelector('.archive-cloud-break')) return;", "if (el.dataset.archiveCloudFormatted === 'true') return;")
backup = path.with_name('archive-menu.js.before-cloud-rows-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
shutil.copy2(path, backup)
path.write_text(src + '\n' + addon, encoding='utf-8')
print('적용 완료: 클라우드 버튼 한 줄씩 배치 및 설명 문장 줄바꿈')
print('백업:', backup.name)
