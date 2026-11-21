#!/usr/bin/env python3
"""Fix only cloud-sync action buttons in the existing archive drawer."""
from pathlib import Path
from datetime import datetime
import shutil

path = Path(__file__).resolve().parent / 'archive-menu.js'
if not path.is_file():
    raise SystemExit('archive-menu.js 파일이 없습니다. 같은 폴더에 패치 파일을 업로드해 주세요.')
source = path.read_text(encoding='utf-8')
marker = 'ARCHIVE_CLOUD_BUTTONS_SINGLE_COLUMN_V1'
if marker in source:
    raise SystemExit('이미 적용되어 있습니다. 중복 적용하지 않습니다.')
if 'archiveMenuDrawer' not in source or 'archiveMenuCloud' not in source:
    raise SystemExit('기존 메뉴 구조를 확인할 수 없어 안전을 위해 중단합니다.')

patch = r'''
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
'''
backup = path.with_name('archive-menu.js.before-cloud-buttons-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
shutil.copy2(path, backup)
path.write_text(source + '\n' + patch, encoding='utf-8')
print('완료: 클라우드 동기화 버튼을 상단 메뉴와 동일하게 한 줄당 하나씩 중앙 정렬')
print('백업:', backup.name)
