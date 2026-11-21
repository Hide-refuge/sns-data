#!/usr/bin/env python3
"""Make cloud sync controls match the backup buttons: single centered column.
Only adds a scoped CSS override; does not replace HTML or event handlers.
"""
from pathlib import Path
from datetime import datetime
import shutil
import sys

root = Path(__file__).resolve().parent
path = root / 'archive-menu.js'
if not path.is_file():
    sys.exit('오류: archive-menu.js 파일이 없습니다. 스크립트를 sns-data 최상위 폴더에 업로드하세요.')
text = path.read_text(encoding='utf-8')
marker = '/* CLOUD_BUTTONS_MATCH_BACKUP_V1 */'
if marker in text:
    print('이미 적용되어 있습니다. 추가 변경하지 않았습니다.')
    sys.exit(0)
needle = 'document.head.append(css);'
if needle not in text:
    sys.exit('안전 중단: 기존 스타일 삽입 위치를 찾지 못했습니다. 파일을 변경하지 않았습니다.')
css = r'''
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
'''
backup = path.with_name(path.name + '.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
shutil.copy2(path, backup)
text = text.replace(needle, needle + '\n' + css, 1)
path.write_text(text, encoding='utf-8')
print('적용 완료: 클라우드 버튼 4개를 백업 관리와 동일한 1열 중앙 정렬로 변경했습니다.')
print('백업:', backup.name)
print('변경 파일:', path.name)
print('버튼 기능 및 데이터 저장 로직은 변경하지 않았습니다.')
