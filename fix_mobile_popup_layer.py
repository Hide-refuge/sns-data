#!/usr/bin/env python3
"""Mobile-only modal stacking fix for SNS Scrap Hub. No JS behavior changes."""
from pathlib import Path
from datetime import datetime
import shutil

root = Path(__file__).resolve().parent
index = root / 'index.html'
if not index.is_file():
    raise SystemExit('오류: index.html과 같은 폴더에서 실행해 주세요.')

start = '<!-- mobile-popup-layer-fix:start -->'
end = '<!-- mobile-popup-layer-fix:end -->'
patch = '''<!-- mobile-popup-layer-fix:start -->
<style>
/* Mobile only: keep all existing dialogs above the management drawer. */
@media (max-width: 650px) {
  body:has(.archive-menu-drawer:not([hidden])) #modalRoot:has(.overlay),
  body:has(.archive-menu-drawer:not([hidden])) #modalRoot:has(.overlay) .overlay {
    z-index: 11020 !important;
  }
  body:has(.archive-menu-drawer:not([hidden])) #modalRoot:has(.overlay) {
    position: relative;
  }
  body:has(.archive-menu-drawer:not([hidden])) #modalRoot .overlay {
    position: fixed !important;
    inset: 0 !important;
    width: 100vw;
    height: 100dvh;
    box-sizing: border-box;
  }
  body:has(.archive-menu-drawer:not([hidden])) #modalRoot .dialog {
    max-width: calc(100vw - 32px);
    max-height: calc(100dvh - 32px);
  }
}
</style>
<!-- mobile-popup-layer-fix:end -->'''

content = index.read_text(encoding='utf-8')
if start in content and end in content:
    before, remainder = content.split(start, 1)
    _, after = remainder.split(end, 1)
    updated = before + patch + after
elif start in content or end in content:
    raise SystemExit('오류: 기존 패치 표시가 불완전합니다. 변경하지 않았습니다.')
else:
    if '</head>' not in content:
        raise SystemExit('오류: </head>를 찾지 못했습니다. 변경하지 않았습니다.')
    updated = content.replace('</head>', patch + '\n</head>', 1)
if updated == content:
    print('이미 최신 패치가 적용되어 있습니다.')
else:
    backup = index.with_name('index.html.before-mobile-popup-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
    shutil.copy2(index, backup)
    index.write_text(updated, encoding='utf-8')
    print('모바일 팝업 표시 순서 패치 적용 완료')
    print('백업:', backup.name)
    print('수정 파일: index.html (모바일 전용 CSS 추가)')
