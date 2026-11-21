from pathlib import Path
from datetime import datetime
import re
import sys

root = Path('/workspaces/sns-data')
if not root.is_dir():
    root = Path.cwd()
path = root / 'index.html'
if not path.is_file():
    sys.exit('오류: index.html을 찾을 수 없습니다.')

css = '''/* mobile-font-tabs-keep-rows-v2 */
@media (max-width: 650px) {
  .font-section-tabs {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
  }
  .font-section-tabs .font-section-tab-row {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    width: 100% !important;
    max-width: 100% !important;
    gap: 4px !important;
    overflow: visible !important;
    box-sizing: border-box !important;
  }
  .font-section-tabs .font-section-tab-row .font-section-tab {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    width: 0 !important;
    max-width: 100% !important;
    min-height: 32px !important;
    height: auto !important;
    padding: 5px 2px !important;
    font-size: clamp(9px, 2.4vw, 12px) !important;
    line-height: 1.25 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: keep-all !important;
    text-align: center !important;
    box-sizing: border-box !important;
  }
}
'''
html = path.read_text(encoding='utf-8')
if 'mobile-font-tabs-keep-rows-v2' in html:
    print('이미 수정된 패치가 적용되어 있습니다.')
    sys.exit(0)
if '</head>' not in html:
    sys.exit('오류: </head>가 없어 수정하지 않았습니다.')
backup = path.with_name('index.html.before-mobile-font-tabs-keep-rows-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bak')
backup.write_bytes(path.read_bytes())
# 이전에 제공한 2열 그리드 패치가 적용되어 있다면 해당 스타일 블록을 교체합니다.
old_pattern = r'<style>\s*/\* mobile-font-tabs-fit-v1 \*/.*?</style>\s*'
html, removed = re.subn(old_pattern, '', html, flags=re.S)
html = html.replace('</head>', '<style>\n' + css + '</style>\n</head>', 1)
path.write_text(html, encoding='utf-8')
print('완료: 버튼 순서 및 기존 1행 3개 / 2행 2개 배치를 유지하고 모바일 버튼 너비와 글자 크기만 조절했습니다.')
print('이전 2열 배치 패치 제거:', '예' if removed else '해당 없음')
print('백업:', backup.name)
