#!/usr/bin/env python3
"""Center archive modal overlays in the space left of the open management drawer."""
from pathlib import Path
from datetime import datetime
import shutil

file = Path(__file__).resolve().parent / 'archive-menu.js'
if not file.is_file():
    raise SystemExit('archive-menu.js 파일이 없습니다. 저장소 최상위 폴더에 패치 파일을 업로드해 주세요.')
source = file.read_text(encoding='utf-8')
marker = '/* ARCHIVE_LEFT_PANE_MODAL_CENTER_V1 */'
if marker in source:
    print('이미 적용되어 있습니다. 추가 변경 없음.')
    raise SystemExit(0)
anchor = '      .archive-menu-heading{'
if source.count(anchor) != 1:
    raise SystemExit('현재 archive-menu.js의 예상 CSS 구조와 다릅니다. 파일을 수정하지 않았습니다.')
css = '''      /* ARCHIVE_LEFT_PANE_MODAL_CENTER_V1 */
      /* While the management drawer is open, center modals only in the remaining left area. */
      body.archive-menu-open #modalRoot .overlay,
      body.archive-menu-open .cbh-api-overlay{
        right:min(410px,92vw)!important;
        box-sizing:border-box;
      }
      body.archive-menu-open #modalRoot .overlay{
        z-index:10002!important;
      }
      body.archive-menu-open #modalRoot .dialog,
      body.archive-menu-open .cbh-api-panel{
        max-width:100%;
        box-sizing:border-box;
      }
      @media(max-width:650px){
        body.archive-menu-open #modalRoot .overlay,
        body.archive-menu-open .cbh-api-overlay{
          right:min(410px,96vw)!important;
        }
      }
'''
backup = file.with_name('archive-menu.js.before-left-center-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
shutil.copy2(file, backup)
file.write_text(source.replace(anchor, css + anchor, 1), encoding='utf-8')
print('패치 적용 완료: archive-menu.js')
print('기존 파일 백업:', backup.name)
print('검증: 햄버거 메뉴 열린 상태에서 Font Settings / API Settings 팝업 위치를 확인하세요.')
