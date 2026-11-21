#!/usr/bin/env python3
"""Install right-side management drawer on development branch; never overwrite original admin logic."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
branch = subprocess.run(['git','branch','--show-current'], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
if branch != 'feature/guest-readonly':
    sys.exit(f'중단: 개발 브랜치(feature/guest-readonly)가 아닙니다. 현재: {branch}')
if not (root / 'archive-menu.js').is_file():
    sys.exit('중단: archive-menu.js 파일이 없습니다.')
script_tag = '<script src="./archive-menu.js?v=menu-20261121-01"></script>'
for name in ('index.html','guest-app.html'):
    file = root / name
    if not file.exists():
        print(f'건너뜀: {name} 파일 없음')
        continue
    content = file.read_text(encoding='utf-8')
    if 'archive-menu.js' in content:
        print(f'이미 적용됨: {name}')
        continue
    if '</body>' not in content or 'id="exportBtn"' not in content:
        sys.exit(f'중단: {name}의 기존 화면 구조가 예상과 다릅니다. 파일을 수정하지 않았습니다.')
    backup = root / f'{name}.before-archive-menu.bak'
    if not backup.exists():
        backup.write_text(content, encoding='utf-8')
    file.write_text(content.replace('</body>',script_tag+'</body>',1), encoding='utf-8')
    print(f'적용 완료: {name} (원본 백업: {backup.name})')
print('완료. 기존 버튼의 ID/이벤트 핸들러와 sync.js/font-settings.js는 변경하지 않았습니다.')
