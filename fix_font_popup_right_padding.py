#!/usr/bin/env python3
"""Adjust Font Settings popup width without touching font logic or cloud data."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parent
path = root / 'archive-menu.js'
if not path.is_file():
    sys.exit('오류: archive-menu.js 파일이 없습니다.')
src = path.read_text(encoding='utf-8')
marker = '/* font-popup-align-registration-20261121 */'
old = 'width: min(540px, calc(100vw - 32px)) !important;'
new = 'width: min(640px, calc(100vw - 32px)) !important;'
if marker not in src:
    sys.exit('오류: 이전 너비 패치를 찾지 못했습니다. 파일은 변경하지 않았습니다.')
if new in src:
    print('이미 640px 너비가 적용되어 있습니다.'); sys.exit(0)
if src.count(old) != 1:
    sys.exit('오류: 기존 540px 설정을 정확히 한 곳에서 찾지 못했습니다. 파일은 변경하지 않았습니다.')
backup = root / 'archive-menu.js.before-font-popup-padding.bak'
if not backup.exists():
    shutil.copy2(path, backup)
path.write_text(src.replace(old, new, 1), encoding='utf-8')
print('완료: 폰트 팝업 너비 540px → 640px, 기존 높이·스크롤 유지')
print('백업:', backup.name)
