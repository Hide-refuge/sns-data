#!/usr/bin/env python3
"""Scale drawer controls to 80%, center content, and remove duplicate cloud heading."""
from pathlib import Path
from datetime import datetime
import shutil

path = Path(__file__).resolve().parent / 'archive-menu.js'
if not path.is_file():
    raise SystemExit('archive-menu.js 파일을 찾을 수 없습니다. 이 스크립트를 같은 폴더에 업로드해 주세요.')
src = path.read_text(encoding='utf-8')
marker = 'ARCHIVE_MENU_CENTER_80_V1'
if marker in src:
    raise SystemExit('이미 적용된 패치입니다. 중복 적용하지 않습니다.')
cloud_heading = '<h3>클라우드 동기화</h3>'
if src.count(cloud_heading) != 1:
    raise SystemExit('중복 제목 위치를 정확히 확인할 수 없어 변경하지 않았습니다.')
if 'archiveMenuDrawer' not in src or 'archiveMenuCloud' not in src:
    raise SystemExit('예상한 햄버거 메뉴 구조가 없어 변경을 중단했습니다.')

addon = r'''
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
'''
backup = path.with_name('archive-menu.js.before-center-80-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
shutil.copy2(path, backup)
# Remove only the drawer's duplicate heading; keep the original sync panel heading.
src = src.replace(cloud_heading, '', 1)
path.write_text(src + '\n' + addon, encoding='utf-8')
print('완료: 80% 크기, 중앙 정렬, 중복 클라우드 동기화 제목 삭제')
print('원본 백업:', backup.name)
