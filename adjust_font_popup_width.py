#!/usr/bin/env python3
"""Narrow the existing fixed-size Font Settings popup, retaining scrolling and behavior."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parent
target = root / 'archive-menu.js'
marker = '/* font-popup-align-registration-20261121 */'
anchor = 'document.head.append(fontPopupSizeStyle);'
if not target.is_file():
    sys.exit('오류: archive-menu.js가 없습니다. 파일을 저장소 최상위 폴더에 업로드해 주세요.')
source = target.read_text(encoding='utf-8')
if marker in source:
    print('이미 적용된 패치입니다.'); sys.exit(0)
if anchor not in source:
    sys.exit('오류: 이전 팝업 크기 패치가 확인되지 않습니다. 기존 파일은 수정하지 않았습니다.')
addition = r'''
    /* font-popup-align-registration-20261121 */
    const fontPopupNarrowStyle = document.createElement('style');
    fontPopupNarrowStyle.id = 'archiveFontPopupNarrow';
    fontPopupNarrowStyle.textContent = `
      #modalRoot .font-dialog {
        width: min(540px, calc(100vw - 32px)) !important;
        max-width: calc(100vw - 32px) !important;
      }
    `;
    document.head.append(fontPopupNarrowStyle);
'''
backup = root / 'archive-menu.js.before-font-popup-narrow.bak'
if not backup.exists():
    shutil.copy2(target, backup)
target.write_text(source.replace(anchor, anchor + '\n' + addition, 1), encoding='utf-8')
print('완료: Font Settings 팝업 너비 540px 적용 (높이/스크롤 유지)')
print('백업:', backup.name)
