from pathlib import Path
import shutil
from datetime import datetime

p=Path('archive-menu.js')
if not p.is_file():
    raise SystemExit('오류: archive-menu.js 파일이 없습니다. /workspaces/sns-data에서 실행해 주세요.')
s=p.read_text(encoding='utf-8')
marker='/* FONT_SETTINGS_TEXT_BUTTONS_90_V1 */'
if marker in s:
    print('이미 적용된 패치입니다. 중복 수정하지 않았습니다.')
    raise SystemExit(0)
needle='    document.head.append(css);'
if s.count(needle)!=1:
    raise SystemExit('안전 중단: 예상한 스타일 삽입 위치를 찾지 못했습니다. 기존 파일은 수정하지 않았습니다.')
css='''    // Font Settings popup only: 90% text and button sizing; preserve dialog width/position.
    css.textContent += `
      /* FONT_SETTINGS_TEXT_BUTTONS_90_V1 */
      .font-dialog { font-size: 90% !important; }
      .font-dialog h2 { font-size: 17.1px !important; }
      .font-dialog h3 { font-size: 90% !important; }
      .font-dialog .btn,
      .font-dialog button,
      .font-dialog input,
      .font-dialog select,
      .font-dialog textarea,
      .font-dialog label { font-size: 90% !important; }
      .font-dialog .btn,
      .font-dialog button { padding: 0.9em 1.0em; }
      .font-dialog .font-section-tabs button { padding: 0.65em 0.75em; }
    `;
'''
backup=p.with_name(p.name+'.before-font90-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.bak')
shutil.copy2(p,backup)
p.write_text(s.replace(needle,css+needle,1),encoding='utf-8')
print('적용 완료: Font Settings의 글자 및 버튼 크기 90% 조정')
print('백업 파일:',backup)
print('확인: 브라우저 새로고침 후 Font Settings 팝업의 1~5번 탭을 확인해 주세요.')
