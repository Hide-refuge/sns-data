# 추가 작업 (mobilefit-20261123) — 모바일 화면 전체 검수 결과 반영
# 1) 깨짐 수정: 하위 폴더 생성 창 겹침, 그리드뷰 버튼 넘침, 입력칸 누를 때 iPhone 자동 확대,
#    가로 화면 설정 팝업 잘림, 게스트 폰트 탭 글씨 크기, 관리 메뉴 버튼 크기·위쪽 빈 공간
# 2) 배치 개선(휴대폰): 제목 글자 크기, 홈 플랫폼 카드 2×2, 폴더 카드 2열, 휴대폰에 맞지 않는 안내 문구 숨김
# 3) 게스트 메뉴 정리: 비어 있는 '백업 관리'·동기화 안내 숨김(로그아웃 버튼은 유지)
# 4) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 mobilefit.py   (이미 적용되어 있으면 index.html은 그대로 두고 게스트 화면만 다시 확인)
import pathlib, re, shutil, sys, datetime

MARK = 'mobilefit-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'guestsync-20261123' not in s and 'archive-menu.js?v=guestsync-20261123' not in s:
    sys.exit('index.html이 최신 main 기준이 아닙니다(이전 작업 미반영). 브랜치를 main에서 만들었는지 확인해 주세요. 중단합니다.')

MOBILE_CSS = """<style id="mobilefit-20261123">
/* mobilefit-20261123: 모바일 검수 반영 */
/* 스크랩 버튼(긴 @계정·작성자 이름)이 카드 밖으로 넘치지 않게 */
.note>*{min-width:0}
.note-actions{min-width:0;max-width:100%}
.note-actions>a,.note-actions>button{max-width:100%;overflow-wrap:anywhere;white-space:normal;text-align:left}
/* 손가락 화면: 입력칸 글자 16px (iPhone이 누를 때 화면을 확대하지 않음), 메뉴 버튼 누르기 쉽게 */
@media (pointer:coarse){
 html body input:not(#_):not([type=checkbox]):not([type=radio]):not([type=color]):not([type=range]):not([type=file]),html body select:not(#_),html body textarea:not(#_),
 html body .cbh-api-panel :is(#cbhApiProvider,#cbhApiKey,#cbhApiPrompt){font-size:16px!important}
 html body .archive-menu-drawer button:not(#_),html body #archiveMenuDrawer #syncControls button:not(#_){min-height:40px!important}
 .crumb button{padding:10px 6px;margin:-10px -6px}
}
/* 손가락 화면: 마우스용 설명(말풍선·안내 문구) 숨김 */
@media (hover:none){.folder:hover .tooltip,.folder:focus-visible .tooltip{display:none!important}.hover-only-hint{display:none}}
/* 관리 메뉴는 항상 위에서부터 */
html body .archive-menu-drawer{justify-content:flex-start!important}
/* 폰트 설정 탭: 좁으면 줄바꿈, 글씨 크기 통일 */
html body .font-dialog .font-section-tab-row:not(#_){flex-wrap:wrap!important;max-width:100%}
html body .font-dialog .font-section-tab:not(#_){max-width:100%!important;white-space:normal!important}
@media(max-width:650px){html body .font-dialog .font-section-tabs .font-section-tab-row:not(#_){grid-template-columns:repeat(2,minmax(0,max-content))!important}}
html body .font-dialog .font-section-tab:not(#_){font-size:13px!important}
/* 하위 폴더 생성 창: 좁은 화면은 한 줄에 하나씩 */
@media(max-width:600px){
 html body .subfolder-horizontal .subfolder-row2{grid-template-columns:minmax(0,1fr)!important;overflow:visible!important}
 html body .subfolder-horizontal .subfolder-row2>.field{min-width:0!important}
 html body .subfolder-horizontal .subfolder-create{width:100%!important}
}
/* 가로로 든 휴대폰: 설정 팝업을 메뉴 위 전체 폭으로 */
@media (max-height:520px) and (max-width:1000px){
 html body.archive-menu-open #modalRoot .overlay,html body.archive-menu-open .cbh-api-overlay{right:0!important;z-index:11020!important}
}
/* 휴대폰 배치 */
@media(max-width:760px){
 html body #archiveEyebrow{font-size:clamp(13px,4.2vw,26px);letter-spacing:.08em}
 #view .grid:has(>.platform){grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
 #view .platform{min-height:132px;padding:16px}
 #view .platform strong{font-size:18px}
 #view .platform .glyph{font-size:26px}
 #view .folders{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
 #view .folders .folder{min-height:112px;padding:13px}
 #view .folders .folder .foldericon{font-size:26px}
 #view .folders .folder strong{font-size:15px;margin:8px 0 3px}
}
</style>"""
HINT_OLD = '<h3>폴더에 마우스를 올리거나 키보드로 선택하면 설명을 볼 수 있습니다.</h3>'
HINT_NEW = '<h3 class="hover-only-hint">폴더에 마우스를 올리거나 키보드로 선택하면 설명을 볼 수 있습니다.</h3>'
if MARK not in s:
    assert s.count('</head>') == 1 and s.count(HINT_OLD) == 1, 'index.html에서 바꿀 위치를 찾지 못했습니다. 중단합니다.'
    shutil.copy(idx, f'index.html.before-mobilefit-{stamp}.bak')
    s = s.replace('</head>', MOBILE_CSS + '</head>').replace(HINT_OLD, HINT_NEW)
    idx.write_text(s, encoding='utf-8')
    changed.append('index.html')

# ── 게스트 화면 생성 (index.html 기준) ─────────────────────────────────
g = s


def rep(old, new, regex=False):
    global g
    if regex:
        g2, n = re.subn(old, new, g, count=1)
        assert n == 1, f'게스트 변환 위치를 찾지 못함 → {old[:70]}'
        g = g2
    else:
        assert g.count(old) == 1, f'게스트 변환 위치를 찾지 못함 → {old[:70]}'
        g = g.replace(old, new)


HIDE = ('#syncPanel,#importBtn,#exportBtn,#apiSettingsBtn,#cbhApiSettingsBtn,#addPost,#editFolder,#deleteFolder,'
        '#folderForm,.subfolder-create,#openFolderCreate,#openSubfolderModal,.item-move-hint,#folderMoveOpen,#itemMoveOpen,'
        '[data-editpost],[data-delpost],[data-search-edit],[data-search-edit-post],[data-folder-reorder],.folder-reorder-handle,'
        '#folderReorderBtn,#folderReorderCancel,#folderReorderSave')
BLOCK = ('#addPost,#editFolder,#deleteFolder,#openFolderCreate,#openSubfolderModal,#folderMoveOpen,#itemMoveOpen,'
         '[data-editpost],[data-delpost],[data-search-edit],[data-search-edit-post],[data-folder-reorder],'
         '#folderReorderBtn,#folderReorderSave,#folderReorderCancel')
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (mobilefit.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
<style id="guest-readonly-style">
{HIDE} {{display:none!important}}
/* 기본 화면의 버튼 통합 스타일(display:inline-flex!important)보다 우선하도록 더 구체적인 선택자로 한 번 더 숨김 */
html body .section-head .actions > #editFolder,html body .section-head .actions > #deleteFolder,
html body .section-head .actions > #openSubfolderModal,html body .section-head .actions > #addPost,
html body header.top .actions #openFolderCreate {{display:none!important}}
/* 게스트: 끌어서 옮기기 기능이 없으므로 카드 위에서도 화면 스크롤·글자 선택 가능 */
.folders .folder{{touch-action:auto!important}}
#postList .note{{-webkit-user-select:text!important;user-select:text!important;-webkit-touch-callout:default!important}}
/* 게스트 메뉴: 쓰지 않는 '백업 관리'·동기화 안내 숨김, 로그아웃 버튼만 표시 */
.archive-menu-group:has(#archiveMenuBackup){{display:none!important}}
html body .archive-menu-drawer #syncPanel>:not(#syncControls){{display:none!important}}
html body .archive-menu-drawer #syncPanel{{margin:0!important}}
#archiveMenuCloud::before{{content:'게스트 모드';display:block;font-size:14px;font-weight:700;margin:0 0 12px;text-align:center}}
</style>
<script>
document.addEventListener('DOMContentLoaded',()=>{{
 const footer=document.querySelector('footer.footer');if(footer)footer.textContent='게스트 체험 모드 · 공개용 스크랩 열람 전용 · 변경 사항은 저장되지 않습니다.';
 const hdr=document.querySelector('header.top');
 const actions=hdr?.querySelector('.actions');
 if(actions){{
   const b=document.createElement('span');
   b.textContent='GUEST · 읽기 전용';
   b.style.cssText='display:inline-block!important;visibility:visible!important;opacity:1!important;font-size:12px;color:#455abf;font-weight:700;white-space:nowrap;flex-shrink:0';
   actions.prepend(b);
   actions.style.alignItems='center';
   actions.style.flexWrap='nowrap';
   actions.style.gap='3ch';
   actions.style.justifyContent='flex-end';
   actions.style.marginLeft='auto';
 }}
 const hide=()=>{{
   document.querySelectorAll('{HIDE}').forEach(x=>{{x.hidden=true;x.style.display='none'}});
   document.querySelectorAll('#view button').forEach(x=>{{if(/^(추가|수정|삭제|편집|저장|폴더 생성|스크랩 추가)$/.test(x.textContent.trim())){{x.hidden=true;x.style.display='none'}}}});
 }};
 const view=document.getElementById('view');if(view)new MutationObserver(hide).observe(view,{{childList:true,subtree:true}});hide();
}}, {{once:true}});
document.addEventListener('submit',e=>{{if(e.target.closest('#view,#modalRoot')&&!e.target.closest('.font-dialog')){{e.preventDefault();e.stopImmediatePropagation();alert('게스트 모드에서는 데이터를 변경할 수 없습니다.')}}}},true);
document.addEventListener('click',e=>{{
 const t=e.target.closest('button');if(!t)return;
 if(t.matches('{BLOCK}')){{e.preventDefault();e.stopImmediatePropagation()}}
}},true);
</script>'''
rep('</head>', GUEST_HEAD + '</head>')
# 동기화 스크립트 제외 + 게스트 모드 표시
rep(r'<div id="modalRoot"></div>(?:<!--[^>]*-->)?<script src="\./sync-config\.js"></script><script src="\./sync\.js\?v=[^"]*"></script><script>',
    '<div id="modalRoot"></div><script>window.SCRAP_GUEST_MODE=true;</script><script>', regex=True)
# 저장소: 공개 데이터 스냅샷(읽기 전용)
a = g.index('function openDB(){')
end_mark = "return transact(s,'readwrite',o=>o.delete(id));\n};\n"
b = g.index(end_mark, a) + len(end_mark)
g = g[:a] + ('// GUEST_SAME_LAYOUT_V1: public snapshot, no IndexedDB, no Drive, no mutations.\n'
             'let guestSnapshot={folders:[],posts:[]};\n'
             'const getAll=async store=>guestSnapshot[store]||[];\n'
             "const put=async()=>{throw Error('게스트 모드에서는 변경할 수 없습니다.')};\n"
             "const del=async()=>{throw Error('게스트 모드에서는 삭제할 수 없습니다.')};\n") + g[b:]
# 시작: guest-data.json 불러오기
rep(r"openDB\(\)\.then\(d=>\{db=d;window\.scrapRefresh=refresh;refresh\(\)\}\)\.catch\(err=>\{[^\n]*?\}\);",
    "fetch('./guest-data.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(data=>{\n"
    " if(!Array.isArray(data.folders)||!Array.isArray(data.posts))throw Error('공개 데이터 형식 오류');\n"
    " guestSnapshot={folders:data.folders,posts:data.posts};window.scrapRefresh=refresh;return refresh();\n"
    "}).catch(err=>{$('view').innerHTML='<div class=\"warning\">게스트 데이터 불러오기 실패: '+escapeHtml(err.message)+'</div>'});", regex=True)
# 스크립트: 게스트 폰트 설정 사용, 관리자 전용 기능 제외
rep(r'<script src="\./font-settings\.js\?v=([^"]*)"></script>', r'<script src="./guest-font-settings.js?v=\1"></script>', regex=True)
for pat in [r'<script src="\./api-settings\.js\?v=[^"]*"></script>', r'<script src="\./guest-font-public-export\.js\?v=[^"]*"></script>',
            r'<script src="\./guest-json-export\.js\?v=[^"]*"></script>', r'<script src="\./github-direct-publish\.js\?v=[^"]*"></script>']:
    rep(pat, '', regex=True)
rep(r'(<script src="\./archive-menu\.js\?v=[^"]*"></script>)',
    "<script>\nfetch('./guest-fonts.json',{method:'HEAD',cache:'no-store'}).then(r=>{\n if(r.status===404)console.info('게스트 폰트 정보는 아직 게시되지 않았습니다. 관리자 화면에서 폰트 설정 내보내기를 실행하세요.');\n}).catch(()=>{});\n</script>\\1", regex=True)
# 편집 기능 끄기 (끌어서 옮기기·상단 폴더 생성 버튼)
rep('function syncFolderCreateButton(){', "function syncFolderCreateButton(){if(window.SCRAP_GUEST_MODE){document.getElementById('openFolderCreate')?.remove();return}")
rep('/* Folder reorder: dedicated touch drag with fixed floating preview. */\n(()=>{',
    '/* Folder reorder: dedicated touch drag with fixed floating preview. */\n(()=>{if(window.SCRAP_GUEST_MODE)return;')
rep("\n(()=>{\n const LONG=420,TOL=9,EDGE=70;", "\n(()=>{\n if(window.SCRAP_GUEST_MODE)return;\n const LONG=420,TOL=9,EDGE=70;")

for must_not in ['sync.js', 'api-settings.js', 'github-direct-publish.js', 'guest-json-export.js', 'openDB(']:
    assert must_not not in g, f'게스트 화면에 관리자 전용 항목이 남음: {must_not}'
if g != g_old:
    shutil.copy(guest, f'guest-app.html.before-mobilefit-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
