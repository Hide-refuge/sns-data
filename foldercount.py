# 추가 작업 (foldercount-20261123)
# 1) 폴더 카드 숫자: "하위 폴더 N개 · 스크랩 M개"
#    N = 바로 아래 단계 폴더 수, M = 아래 모든 단계 폴더의 스크랩까지 합친 총 수량
#    (플랫폼 화면의 폴더 카드와 폴더 안의 하위 폴더 카드 모두 같은 기준)
# 2) 하위 폴더가 없으면 '하위 폴더' 제목과 '하위 폴더가 없습니다.' 칸을 표시하지 않음
# 3) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 foldercount.py
import pathlib, re, shutil, sys, datetime

MARK = 'foldercount-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="mobilefit2-20261123"' not in s:
    sys.exit('index.html에 이전 모바일 2차 수정이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')

REPL = [
    # 총 스크랩 수 계산 함수 추가
    ('function folderOptionHtml(',
     '/* foldercount-20261123: 아래 모든 단계 폴더의 스크랩까지 합친 수 */\n'
     'function folderPostTotal(id){const ids=folderDescendants(id);ids.add(id);return posts.filter(p=>ids.has(p.folderId)).length}\n'
     'function folderOptionHtml('),
    # 폴더 안 하위 폴더 카드
    ('<small>하위 폴더 ${folderChildren(f.id,platform).length}개 · 스크랩 ${posts.filter(p=>p.folderId===f.id).length}개</small>',
     '<small><span class="fc-n">하위 폴더 ${folderChildren(f.id,platform).length}개</span> · <span class="fc-n">스크랩 ${folderPostTotal(f.id)}개</span></small>'),
    # 플랫폼 화면 폴더 카드
    ('<small>스크랩 ${posts.filter(p=>p.folderId===f.id).length}개</small>',
     '<small><span class="fc-n">하위 폴더 ${folderChildren(f.id,f.platform).length}개</span> · <span class="fc-n">스크랩 ${folderPostTotal(f.id)}개</span></small>'),
    # 하위 폴더가 없으면 영역 숨김
    ('<div class="section-head"><h3>하위 폴더<span class="item-move-hint">길게 눌러 순서 변경 · 다른 폴더로 이동</span></h3></div><div class="subfolder-area"><div class="subfolder-list">${folderCards(f.id,f.platform)}</div></div>',
     '${folderChildren(f.id,f.platform).length?`<div class="section-head"><h3>하위 폴더<span class="item-move-hint">길게 눌러 순서 변경 · 다른 폴더로 이동</span></h3></div><div class="subfolder-area"><div class="subfolder-list">${folderCards(f.id,f.platform)}</div></div>`:\'\'}'),
]
if MARK not in s:
    for old, new in REPL:
        assert s.count(old) == 1, 'index.html에서 바꿀 위치를 찾지 못했습니다 → ' + old[:50] + ' … 중단합니다.'
    shutil.copy(idx, f'index.html.before-foldercount-{stamp}.bak')
    for old, new in REPL:
        s = s.replace(old, new)
    s = s.replace('</head>', '<style id="foldercount-20261123">/* 폴더 카드 숫자는 "하위 폴더 N개"·"스크랩 M개" 단위로만 줄바꿈 */.folder small .fc-n{white-space:nowrap}</style></head>', 1)
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (foldercount.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-foldercount-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
