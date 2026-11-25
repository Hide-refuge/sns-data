# 추가 작업 (mobiletype-20261126) — 휴대폰 글자 크기 정리 + 검색창 문구 수정
# 1) 휴대폰 화면만 글자 크기를 6단계로 정리 (컴퓨터·태블릿 화면은 그대로)
#    화면 제목 22 · 카드 제목 16 · 본문 15 · 보조 13 · 작은 글자 12~12.5 · 탭 이름 11 (px)
#    홈 플랫폼 카드: 축소 대신 글자 크기 직접 지정 (4개가 한 화면에 들어가는 것은 유지)
# 2) 플랫폼 화면 검색창 문구: '모든 폴더에서 제목·키워드·@계정 검색' → '제목·키워드·@계정 검색'
# 3) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 mobiletype.py  (여러 번 실행해도 결과 같음)
# 되돌리기: 만들어진 .bak 파일로 복원
import pathlib, re, shutil, sys, datetime

MARK = 'mobiletype-20261126'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="liquidglass2-20261126"' not in s:
    sys.exit('index.html에 이전 디자인(liquidglass2)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')
CSS = r"""/* mobiletype-20261126: 휴대폰 글자 크기 체계 정리 (컴퓨터·태블릿 화면은 그대로) */
/* 크기 단계(iOS 기준 참고): 화면 제목 22 · 카드 제목 16 · 본문 15 · 보조 13 · 작은 글자 12 · 탭 이름 11 */
@media (max-width:699px){
 /* 화면 제목과 설명 */
 html body #view .section-head h2{font-size:22px!important;line-height:1.3!important}
 html body #view .section-head h3{font-size:13px!important;line-height:1.5!important}
 html body #view .section-head h3 .item-move-hint{font-size:12px!important}
 /* 스크랩 카드 */
 html body #view .note h3{font-size:16px!important;line-height:1.4!important}
 html body #view .note .summary{font-size:15px!important;line-height:1.6!important}
 html body #view .note .chip{font-size:12px!important;line-height:1.4!important}
 html body #view .note .chip{padding:3px 7px!important}
 html body #view .note .chips{gap:4px!important}
 html body #view .note .meta,html body #view .note .meta *{font-size:12.5px!important;line-height:1.5!important}
 html body #view .note .gallery-thumbs-count{font-size:12px!important}
 html body #view .note .note-actions>a,html body #view .note .note-actions>button{font-size:13px!important}
 /* 폴더 카드 */
 html body #view .folder strong{font-size:16px!important;line-height:1.35!important}
 html body #view .folder .fc-n,html body #view .folder small{font-size:13px!important}
 /* 관리 메뉴 */
 html body .archive-menu-drawer button.btn:not(#_){font-size:14px!important}
 html body .archive-menu-drawer .hint{font-size:12.5px!important;line-height:1.6!important}
 /* 입력 창 이름표, 아래 안내문 */
 html body .dialog label{font-size:13px!important}
 html body footer.footer{line-height:1.6!important}
}
/* 휴대폰 홈 플랫폼 카드: 축소(zoom) 대신 글자 크기를 직접 지정해 4개가 한 화면에 들어가면서 더 잘 읽히게 */
@media (max-width:760px){
 html body #view .platform>*{zoom:1!important}
 html body #view .platform .glyph{font-size:20px!important;line-height:1!important}
 html body #view .platform strong{font-size:16px!important;line-height:1.25!important;margin-bottom:3px!important}
 html body #view .platform .muted{font-size:12.5px!important;line-height:1.35!important}
 html body #view .platform>.muted:last-child{padding-top:0!important;margin-top:auto}
}"""
BLOCK_HTML = f'<style id="{MARK}">\n{CSS}\n</style>'
OLD_PH, NEW_PH = 'placeholder="모든 폴더에서 제목·키워드·@계정 검색"', 'placeholder="제목·키워드·@계정 검색"'
s_new = s
if OLD_PH in s_new:
    assert s_new.count(OLD_PH) == 1, '검색창 문구 위치가 예상과 다릅니다. 중단합니다.'
    s_new = s_new.replace(OLD_PH, NEW_PH)
assert NEW_PH in s_new, '검색창 문구 위치를 찾지 못했습니다. 중단합니다.'
s_new2 = re.sub(r'<style id="mobiletype-20261126">.*?</style>', lambda m: BLOCK_HTML, s_new, flags=re.S)
if s_new2 == s_new and BLOCK_HTML not in s_new:
    assert s_new.count('</body>') == 1, 'index.html에서 </body> 위치를 찾지 못했습니다. 중단합니다.'
    s_new2 = s_new.replace('</body>', BLOCK_HTML + '</body>')
s_new = s_new2
if s_new != s:
    shutil.copy(idx, f'index.html.before-mobiletype-{stamp}.bak')
    s = s_new
    idx.write_text(s, encoding='utf-8'); changed.append('index.html')

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
        '#folderReorderBtn,#folderReorderCancel,#folderReorderSave,#openFolderDelete,#backupTrashBtn')
BLOCK = ('#addPost,#editFolder,#deleteFolder,#openFolderCreate,#openSubfolderModal,#folderMoveOpen,#itemMoveOpen,'
         '[data-editpost],[data-delpost],[data-search-edit],[data-search-edit-post],[data-folder-reorder],'
         '#folderReorderBtn,#folderReorderSave,#folderReorderCancel,#openFolderDelete,#backupTrashBtn,[data-trash-restore],[data-trash-purge],[data-trash-empty]')
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (mobiletype.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
             "const del=async()=>{throw Error('게스트 모드에서는 삭제할 수 없습니다.')};\nconst getAllRaw=getAll;\n") + g[b:]
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
rep('function syncFolderCreateButton(){', "function syncFolderCreateButton(){if(window.SCRAP_GUEST_MODE){document.getElementById('openFolderCreate')?.remove();document.getElementById('openFolderDelete')?.remove();return}")
rep('/* Folder reorder: dedicated touch drag with fixed floating preview. */\n(()=>{',
    '/* Folder reorder: dedicated touch drag with fixed floating preview. */\n(()=>{if(window.SCRAP_GUEST_MODE)return;')
rep("\n(()=>{\n const LONG=420,TOL=9,EDGE=70;", "\n(()=>{\n if(window.SCRAP_GUEST_MODE)return;\n const LONG=420,TOL=9,EDGE=70;")

for must_not in ['sync.js', 'api-settings.js', 'github-direct-publish.js', 'guest-json-export.js', 'openDB(']:
    assert must_not not in g, f'게스트 화면에 관리자 전용 항목이 남음: {must_not}'
if g != g_old:
    shutil.copy(guest, f'guest-app.html.before-mobiletype-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
