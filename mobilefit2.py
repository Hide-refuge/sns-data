# 추가 작업 (mobilefit2-20261123) — 휴대폰 실제 화면 확인 후 추가 수정
# 1) 관리 메뉴 버튼: 글자를 버튼 가운데로 (위·아래 간격 동일) — 관리자·게스트 모든 버튼
# 2) 홈 플랫폼 카드 4개: 줄 간격을 넓혀 읽기 쉽게
# 3) 스크랩 카드(특히 그리드뷰): 넓이를 넘는 키워드는 '…'로 줄임, 글자는 띄어쓰기 단위로 줄바꿈,
#    추가일과 이미지 수는 그리드뷰에서 2줄로 나눔
# 4) 길게 누르면 아래에 뜨는 안내 창: 글자 한 줄 + 버튼 한 줄로 넓게 표시
# 5) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 mobilefit2.py
import pathlib, re, shutil, sys, datetime

MARK = 'mobilefit2-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="mobilefit-20261123"' not in s:
    sys.exit('index.html에 이전 모바일 수정(mobilefit)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')

CSS2 = """<style id="mobilefit2-20261123">
/* mobilefit2-20261123 */
/* 1) 관리 메뉴 버튼: 글자를 위·아래 가운데로 */
html body .archive-menu-drawer button:not(#_){display:inline-flex!important;align-items:center!important;justify-content:center!important}
/* 3) 스크랩 카드: 키워드는 한 줄('…'), 글자는 띄어쓰기 단위 줄바꿈 */
.note .chips{min-width:0;max-width:100%}
.note .chips .chip{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.note h3,.note .summary,.note .meta,.note-actions>a,.note-actions>button{word-break:keep-all;overflow-wrap:break-word}
.folder-post-grid .note .meta-sep,.search-results-grid .note .meta-sep{display:none}
.folder-post-grid .note .meta-date,.folder-post-grid .note .meta-img,.search-results-grid .note .meta-date,.search-results-grid .note .meta-img{display:block}
/* 4) 길게 누르기 안내 창: 화면 폭에 맞게 넓게, 글자 한 줄 + 버튼 한 줄 */
html body .folder-reorder-tip{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px 8px;width:max-content;max-width:calc(100vw - 24px);box-sizing:border-box;line-height:1.4}
html body .folder-reorder-tip button{margin:0;padding:7px 12px;min-height:34px;white-space:nowrap}
html body .folder-reorder-tip button+button{margin:0}
/* 2) 홈 플랫폼 카드: 줄 간격 */
@media(max-width:760px){
 #view .platform{justify-content:flex-start;gap:10px;min-height:0}
 #view .platform strong{display:block;line-height:1.25;margin-bottom:6px}
 #view .platform .muted{line-height:1.45}
 #view .platform>.muted:last-child{margin-top:auto;padding-top:4px}
}
</style>"""
META_OLD = '<div class="meta">추가일 ${formatDate(p.createdAt)} · 이미지 ${(p.images||[]).length}장</div>'
META_NEW = ('<div class="meta"><span class="meta-date">추가일 ${formatDate(p.createdAt)}</span><span class="meta-sep"> · </span>'
            '<span class="meta-img">이미지 ${(p.images||[]).length}장</span></div>')
if MARK not in s:
    assert s.count('</head>') == 1 and s.count(META_OLD) == 2, 'index.html에서 바꿀 위치를 찾지 못했습니다. 중단합니다.'
    # 이전 수정의 '아무 곳에서나 줄바꿈'을 띄어쓰기 단위로 변경
    OLDWRAP = '.note-actions>a,.note-actions>button{max-width:100%;overflow-wrap:anywhere;white-space:normal;text-align:left}'
    assert s.count(OLDWRAP) == 1, 'index.html에서 이전 모바일 수정 위치를 찾지 못했습니다. 중단합니다.'
    shutil.copy(idx, f'index.html.before-mobilefit2-{stamp}.bak')
    s = s.replace(OLDWRAP, '.note-actions>a,.note-actions>button{max-width:100%;white-space:normal;text-align:left}')
    s = s.replace(META_OLD, META_NEW).replace('</head>', CSS2 + '</head>')
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (mobilefit2.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-mobilefit2-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
