#!/usr/bin/env python3
"""Adjust only Font Settings 1-5 tab button text responsive size."""
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime

root = Path(__file__).resolve().parent
file = root / 'font-settings.js'
if not file.is_file():
    sys.exit('오류: 이 파일을 font-settings.js가 있는 프로젝트 최상위 폴더에 넣어주세요.')
source = file.read_text(encoding='utf-8')
marker = '.font-section-tab[aria-selected="true"]'
if marker not in source:
    sys.exit('안전 중단: 예상한 폰트 탭 CSS를 찾지 못했습니다. 기존 파일은 변경되지 않았습니다.')
# The CSS is injected by font-settings.js. Keep all existing layout and behavior intact.
new_rule = '.font-dialog .font-section-tab{font-size:clamp(9.5px,2.5vw,13.5px)!important}'
old_rule_pattern = r'\.font-dialog \.font-section-tab\{font-size:clamp\([^}]+\)!important\}'
if new_rule in source:
    print('이미 9.5~13.5px 설정이 적용되어 있습니다. 변경 사항 없음.')
    sys.exit(0)
if re.search(old_rule_pattern, source):
    changed = re.sub(old_rule_pattern, new_rule, source, count=1)
else:
    changed = source.replace(marker, new_rule + marker, 1)
if changed == source:
    sys.exit('안전 중단: 수정할 위치를 찾지 못했습니다.')
backup = root / ('font-settings.js.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
shutil.copy2(file, backup)
file.write_text(changed, encoding='utf-8')
print('완료: Font Settings 1~5번 버튼 글자 크기만 9.5~13.5px로 변경했습니다.')
print('기존 버튼 배치, 여백, 다른 글자 크기 및 기능은 수정하지 않았습니다.')
print('백업:', backup.name)
