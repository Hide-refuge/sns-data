from pathlib import Path
import sys
root = Path.cwd()
index = root / 'index.html'
script = root / 'guest-entry.js'
if not index.is_file() or not (root / 'guest.html').is_file():
    sys.exit('오류: sns-data 폴더에서 실행해야 하며 index.html과 guest.html이 필요합니다.')
if not script.is_file():
    sys.exit('오류: guest-entry.js 파일이 현재 폴더에 없습니다.')
content = index.read_text(encoding='utf-8')
tag = '<script src="./guest-entry.js?v=guest-login-01" defer></script>'
if tag in content:
    print('이미 설치되어 있습니다. 중복 변경하지 않았습니다.')
    sys.exit(0)
if '</body>' not in content:
    sys.exit('오류: index.html에 </body>가 없어 수정하지 않았습니다.')
backup = root / 'index.html.before-guest-login.bak'
if backup.exists():
    sys.exit('기존 백업 파일이 있습니다. 덮어쓰지 않도록 중단합니다.')
backup.write_text(content, encoding='utf-8')
index.write_text(content.replace('</body>', tag + '\n</body>', 1), encoding='utf-8')
print('완료: index.html에 게스트 로그인 스크립트를 연결했습니다.')
print('백업: index.html.before-guest-login.bak (Git에 업로드하지 마세요)')
