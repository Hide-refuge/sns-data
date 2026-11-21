from pathlib import Path
from datetime import datetime
import re
import sys

root = Path('/workspaces/sns-data')
if not root.is_dir():
    root = Path.cwd()
path = root / 'index.html'
if not path.is_file():
    sys.exit('오류: index.html을 찾을 수 없습니다. sns-data 폴더에서 실행하세요.')

marker = 'mobile-font-tabs-intrinsic-2ch-v4'
css = '''/* mobile-font-tabs-intrinsic-2ch-v4 */
@media (max-width: 650px) {
  .font-section-tabs {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    gap: 6px !important;
  }
  .font-section-tabs .font-section-tab-row {
    display: grid !important;
    grid-template-columns: max-content max-content !important;
    justify-content: center !important;
    align-items: center !important;
    justify-items: center !important;
    column-gap: 6px !important;
    row-gap: 6px !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    box-sizing: border-box !important;
  }
  .font-section-tabs .font-section-tab-row:first-child .font-section-tab:nth-child(3) {
    grid-column: 1 / -1 !important;
    justify-self: center !important;
  }
  .font-section-tabs .font-section-tab-row .font-section-tab {
    box-sizing: border-box !important;
    flex: none !important;
    width: max-content !important;
    min-width: 0 !important;
    max-width: none !important;
    min-height: 32px !important;
    height: auto !important;
    padding: 6px 2ch !important;
    font-size: clamp(9px, 2.5vw, 13px) !important;
    line-height: 1.25 !important;
    white-space: nowrap !important;
    text-align: center !important;
  }
}
'''
original = path.read_text(encoding='utf-8')
if marker in original:
    print('이미 같은 패치가 적용되어 있습니다.')
    sys.exit(0)
if '</head>' not in original:
    sys.exit('오류: </head>를 찾지 못했습니다. 파일을 수정하지 않았습니다.')
# 이전에 제공한 패치의 스타일 블록만 제거합니다.
updated = original
for tag in ['mobile-font-tabs-2-1-2-v3', 'mobile-font-tabs-keep-rows-v2', 'mobile-font-tabs-fit-v1']:
    pattern = r'<style>\s*/\*\s*' + re.escape(tag) + r'\s*\*/.*?</style>\s*'
    updated = re.sub(pattern, '', updated, flags=re.S)
backup = path.with_name('index.html.before-mobile-font-tabs-intrinsic-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
backup.write_bytes(path.read_bytes())
updated = updated.replace('</head>', '<style>\n' + css + '</style>\n</head>', 1)
path.write_text(updated, encoding='utf-8')
print('완료: 1·2 / 3 / 4·5 배치, 각 버튼은 이름 너비 + 좌우 2ch')
print('백업:', backup.name)
print('주의: 실제 모바일 화면에서 겹침 여부와 버튼 동작을 확인하세요.')
