#!/usr/bin/env python3
"""Place existing font modal above the archive management drawer."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
js = root / 'archive-menu.js'
if not js.is_file():
    sys.exit('오류: archive-menu.js가 없습니다. 두 파일을 sns-data 최상위 폴더에 배치해 주세요.')
s = js.read_text(encoding='utf-8')
if 'archive-menu-drawer' not in s or 'archive-menu-backdrop' not in s:
    sys.exit('오류: 기존 햄버거 메뉴 코드를 찾을 수 없습니다. 파일을 변경하지 않았습니다.')
rule = '      body.archive-menu-open #modalRoot .overlay{z-index:10010!important}\n'
if rule.strip() in s:
    print('이미 적용되어 있습니다. 추가 수정이 필요하지 않습니다.')
    sys.exit(0)
anchor = '      body.archive-menu-open{overflow:hidden}'
if s.count(anchor) != 1:
    sys.exit('오류: 예상한 CSS 위치를 찾지 못했습니다. 파일을 변경하지 않았습니다.')
backup = js.with_name('archive-menu.js.before-font-popup-fix.bak')
if backup.exists():
    sys.exit(f'오류: 기존 백업 {backup.name}이 있습니다. 덮어쓰지 않았습니다.')
backup.write_text(s, encoding='utf-8')
js.write_text(s.replace(anchor,rule+anchor,1), encoding='utf-8')
print('수정 완료: archive-menu.js')
print('백업 생성:', backup.name)
print('폰트 설정 팝업을 관리 메뉴보다 앞에 표시하도록 수정했습니다.')
