# 2단계 임시 코드 정리 (cleanup-20261123)
# - 진단 패널 삭제, 폴더 버튼 CSS 7개 → 1개, 하위 폴더 팝업 스크립트 4개(v3~v6) + 높이 맞춤 스크립트 → 1개
# - 폴더 화면 버튼 4개를 처음부터 올바른 순서로 표시 (수정 → 삭제 → 하위 폴더 생성 → 스크랩 추가)
# - 데스크톱 상단 버튼 높이 42px 통일, 터치 화면에서 폴더 설명 말풍선이 남는 문제 수정
# 사용: 사이트 폴더에서 python3 apply_cleanup_v1.py  (이미 적용되어 있으면 아무것도 바꾸지 않음)
import pathlib, re, shutil, sys, datetime

idx = pathlib.Path('index.html')
s = idx.read_text(encoding='utf-8')
if 'cleanup-20261123' in s:
    sys.exit('이미 적용되어 있습니다. 변경 없음.')
if 'top-folder-create-modal-v1' not in s:
    sys.exit('먼저 상단 + 폴더 생성 작업(apply_top_folder_modal)이 적용되어 있어야 합니다.')


def cut(text, start_marker, end_marker, keep_end=True):
    """start_marker부터 end_marker 직전(또는 포함)까지 잘라낸다. 각각 정확히 1번 있어야 함."""
    assert text.count(start_marker) == 1, f'표시를 찾지 못함: {start_marker}'
    a = text.index(start_marker)
    b = text.index(end_marker, a)
    if not keep_end:
        b += len(end_marker)
    return text[:a], text[a:b], text[b:]


# 1) 폴더 화면 버튼: 인라인 스타일 제거 + 하위 폴더 버튼을 처음부터 올바른 위치에 표시
m = re.search(r'<div class="actions"><button class="btn" id="editFolder"[^>]*>폴더 수정</button>'
              r'<button class="btn danger" id="deleteFolder"[^>]*>폴더 삭제</button>'
              r'<button class="btn primary" id="addPost"[^>]*>(＋ 스크랩 추가)</button></div>', s)
assert m and len(re.findall(r'id="editFolder"', s)) == 1, '폴더 화면 버튼 위치를 찾지 못함'
s = s[:m.start()] + ('<div class="actions"><button class="btn" id="editFolder">폴더 수정</button>'
                     '<button class="btn danger" id="deleteFolder">폴더 삭제</button>'
                     '<button class="btn primary" type="button" id="openSubfolderModal">+ 하위 폴더 생성</button>'
                     f'<button class="btn primary" id="addPost">{m.group(1)}</button></div>') + s[m.end():]

# 2) 머리말의 버튼 CSS 패치 5개(v1·v2·v2·v3·v4) → 통합 CSS 1개
CSS = '''<!-- cleanup-20261123: 버튼 스타일 통합 (folder-action-button-size-v1 ~ folder-buttons-font14-v1 대체) -->
<style>
/* 폴더 화면 상단 버튼 4개: 높이 42px · 글자 14px */
.section-head .actions > #editFolder,
.section-head .actions > #deleteFolder,
.section-head .actions > #openSubfolderModal,
.section-head .actions > #addPost{
  height:42px!important;min-height:42px!important;max-height:42px!important;
  padding:0 12px!important;font-size:14px!important;font-weight:500!important;line-height:1!important;
  border-radius:8px!important;box-sizing:border-box!important;
  display:inline-flex!important;align-items:center!important;justify-content:center!important;
  vertical-align:middle!important;white-space:nowrap!important;flex-shrink:0!important}
/* 상단 '+ 폴더 생성'·햄버거 버튼: 모든 화면에서 높이 42px */
header.top .actions #openFolderCreate,
header.top .actions #archiveMenuToggle{height:42px!important;min-height:42px!important;padding-top:0!important;padding-bottom:0!important;box-sizing:border-box!important}
header.top .actions #openFolderCreate{display:inline-flex;align-items:center;justify-content:center;font-size:14px;line-height:1;white-space:nowrap}
/* 터치 화면: 폴더를 누른 뒤 설명 말풍선이 화면에 남지 않도록 */
@media (hover:none){.folder:hover .tooltip{display:none}}
</style>
'''
pre, _, post = cut(s, '<!-- folder-action-button-size-v1 -->', '<!-- top-folder-create-mobile-v1 -->')
s = pre + CSS + '\n' + post

# 3) 하위 폴더 팝업 스크립트: v3 스크립트 ~ 진단 패널까지(버튼 배치·순서·높이 측정·진단) → 통합 스크립트 1개
#    (v3의 팝업 CSS는 그대로 유지)
SCRIPT = '''<!-- cleanup-20261123: 폴더 팝업 정리 (subfolder-modal v3~v6, folder-white-button-match, folder-button-diagnostic 대체) -->
<script>
(function () {
  // 폴더 생성 팝업(하위·상위 공통): 접힌 입력 영역 펼치기, 오른쪽 위 × 닫기 버튼, 이모지 버튼 문구
  function tidyFolderModal() {
    const root = document.getElementById('modalRoot');
    const dialog = root && root.querySelector('.dialog');
    const form = root && root.querySelector('#folderForm');
    if (!dialog || !form) return;
    const details = form.closest('details');
    if (details) { if (!details.open) details.open = true; if (details.style.display !== 'block') details.style.display = 'block'; }
    if (!dialog.querySelector('.subfolder-modal-close')) {
      const close = document.createElement('button');
      close.type = 'button';
      close.className = 'subfolder-modal-close';
      close.textContent = '×';
      close.setAttribute('aria-label', '팝업 닫기');
      close.setAttribute('data-close', '');
      dialog.prepend(close);
    }
    const label = '전체 이모지 선택';
    root.querySelectorAll('button').forEach(b => {
      const t = b.textContent;
      if (b.classList.contains('subfolder-emoji-toggle') || t.includes('전체 이모지 검색') || t.includes(label)) {
        if (t.trim() !== label) b.textContent = label;
        if (b.getAttribute('aria-label') !== label) b.setAttribute('aria-label', label);
      }
    });
  }
  function init() {
    const root = document.getElementById('modalRoot');
    if (root) new MutationObserver(tidyFolderModal).observe(root, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
</script>
'''
pre, mid, post = cut(s, '<!-- subfolder-modal-layout-v3 -->', '<!-- folder-buttons-font14-v1 -->')
assert mid.count('<script>') == 6 and '<!-- folder-button-diagnostic-v1 -->' in mid, '정리 대상 스크립트 구성이 예상과 다름'
style_end = mid.index('</style>') + len('</style>')
s = pre + mid[:style_end] + '\n\n' + SCRIPT + post

# 4) 마지막 패치(font14-v1) 삭제 — 2)의 통합 CSS에 포함됨
pre, _, post = cut(s, '<!-- folder-buttons-font14-v1 -->', '</style>', keep_end=False)
s = pre + post

for gone in ['folderButtonDiagnostic', '<!-- folder-white-button-match-blue-v1 -->', '<!-- subfolder-button-order-v5 -->',
             '<!-- subfolder-button-order-v6 -->', '<!-- subfolder-modal-adjust-v4 -->', '<!-- folder-buttons-final-height-v4 -->',
             '<!-- folder-buttons-font14-v1 -->', 'style="height:42px!important']:
    assert gone not in s, f'정리되지 않은 항목: {gone}'

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy(idx, f'index.html.before-cleanup-{stamp}.bak')
idx.write_text(s, encoding='utf-8')
print(f'적용 완료: index.html 정리 (백업: index.html.before-cleanup-{stamp}.bak)')
