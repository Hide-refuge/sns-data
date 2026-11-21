#!/usr/bin/env python3
"""Fix Font Settings popup size without changing its handlers or font data."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / 'archive-menu.js'
MARKER = '/* font-popup-fixed-size-20261121 */'
ANCHOR = 'document.head.append(css);'

if not TARGET.is_file():
    sys.exit('오류: archive-menu.js 파일이 없습니다. 이 스크립트를 해당 파일과 같은 폴더에 배치하세요.')
source = TARGET.read_text(encoding='utf-8')
if MARKER in source:
    print('이미 적용된 패치입니다. 추가 변경하지 않았습니다.')
    sys.exit(0)
if ANCHOR not in source:
    sys.exit('오류: 예상한 코드 위치를 찾지 못했습니다. 기존 파일을 수정하지 않았습니다.')

# Use a distinct style element to avoid replacing any existing drawer CSS or z-index fixes.
addition = r'''
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
'''
backup = TARGET.with_name('archive-menu.js.before-font-popup-size.bak')
if not backup.exists():
    shutil.copy2(TARGET, backup)
TARGET.write_text(source.replace(ANCHOR, ANCHOR + '\n' + addition, 1), encoding='utf-8')
print('완료: archive-menu.js 팝업 크기 CSS 적용')
print('백업:', backup.name)
print('원본 폰트 파일 및 관리자 데이터 변경 없음')
