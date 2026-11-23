# 추가 작업 (liquidglass-20261123)
# 1) 사이트 전체에 '리퀴드 글래스 · 블루 & 화이트' 디자인 적용 (글꼴은 바꾸지 않음)
#    - 배경: 흰색→연파랑 그라데이션 + 옅은 파란·분홍 빛 번짐
#    - 카드·버튼·입력창·창·메뉴: 투명 유리(흐림 효과) + 가장자리 흰 빛
#    - 글자색: 진한 파랑 #1E50E6 / 주요 버튼·현재 탭: #3A87FE
# 2) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 liquidglass.py  (여러 번 실행해도 결과 같음)
# 되돌리기: index.html에서 <style id="liquidglass-20261123"> … </style> 부분을 지우고 다시 실행하거나, 만들어진 .bak 파일로 복원
import pathlib, re, shutil, sys, datetime

MARK = 'liquidglass-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'noback-20261123' not in s:
    sys.exit('index.html에 이전 수정(noback)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')
CSS = """html body{background:#F4F8FF!important;color:#1E50E6!important}
html body::before{content:'';position:fixed;inset:-10%;pointer-events:none;z-index:0;
 background:radial-gradient(42% 32% at 12% 18%,rgba(58,135,254,.256),transparent 70%),radial-gradient(38% 30% at 92% 46%,rgba(255,237,255,.76),transparent 70%),
 radial-gradient(46% 34% at 38% 92%,rgba(58,135,254,.192),transparent 72%),linear-gradient(180deg,#F9FBFF 0%,#E9F1FF 60%,#D9E9FF 100%)}
html body .app{position:relative;z-index:1}
html body #archiveEyebrow{color:#1E50E6!important}
html body .top h1,html body #archivePeriod{color:#3E5DA6!important}
html body .muted,html body small,html body .hint,html body .meta,html body .section-head h3{color:#4D6AAE!important}
html body .section-head h2,html body #view h2,html body .note h3,html body .folder strong,html body .platform strong{color:#1E50E6!important}
html body .panel,html body .platform,html body .folder,html body .note,html body .empty{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.22),rgba(255,255,255,.06))!important;
 -webkit-backdrop-filter:blur(26px) saturate(180%);backdrop-filter:blur(26px) saturate(180%);border:1px solid rgba(255,255,255,.55)!important;border-radius:22px!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.85),inset 0 -1px 0 rgba(255,255,255,.25),inset 0 0 18px rgba(255,255,255,.12),0 10px 30px rgba(30,64,175,.12)!important;color:#1E50E6!important}
html body .note{border-left:1px solid rgba(255,255,255,.55)!important}
html body .platform .glyph{color:#3A87FE!important}
html body .folder{border-top:1px solid rgba(255,255,255,.75)!important}
html body .chip{background:rgba(255,255,255,.28)!important;color:#2A6FE0!important;border:1px solid rgba(255,255,255,.6);border-radius:999px!important;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
html body .btn,html body a.btn{background:rgba(255,255,255,.2)!important;color:#1E50E6!important;border:1px solid rgba(255,255,255,.65)!important;border-radius:999px!important;
 -webkit-backdrop-filter:blur(14px) saturate(170%);backdrop-filter:blur(14px) saturate(170%);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 4px 14px rgba(30,64,175,.08)!important}
html body .btn.primary,html body #openFolderCreate{background:linear-gradient(180deg,rgba(104,165,255,.92),rgba(58,135,254,.95))!important;color:#fff!important;border:1px solid rgba(255,255,255,.45)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 8px 20px rgba(58,135,254,.32)!important}
html body .btn.danger{color:#d1435b!important}
html body input,html body select,html body textarea{background:rgba(255,255,255,.3)!important;color:#1E50E6!important;border:1px solid rgba(255,255,255,.7)!important;border-radius:16px!important;-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:inset 0 1px 2px rgba(30,64,175,.08)}
html body input::placeholder,html body textarea::placeholder{color:#6b7fa6!important}
html body #crumb{background:rgba(244,248,255,.62)!important;-webkit-backdrop-filter:blur(22px) saturate(180%);backdrop-filter:blur(22px) saturate(180%);box-shadow:inset 0 -1px 0 rgba(255,255,255,.55)}
html body #crumb button{color:#3A87FE!important}html body #crumb span{color:#7488ad!important}
html body #crumb .nav-count,html body .pill{background:rgba(58,135,254,.12)!important;color:#2A6FE0!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.6)}
html body .archive-menu-toggle{background:rgba(255,255,255,.22)!important;color:#1E50E6!important;border:1px solid rgba(255,255,255,.7)!important;border-radius:14px!important;-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);box-shadow:inset 0 1px 0 rgba(255,255,255,.9)}
html body .nav-tabbar{background:rgba(244,248,255,.6)!important;-webkit-backdrop-filter:blur(28px) saturate(180%);backdrop-filter:blur(28px) saturate(180%);border-top:1px solid rgba(255,255,255,.6)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)!important}
html body .nav-tabbar button{color:#6b7fa6!important}html body .nav-tabbar button.on{color:#3A87FE!important}
html body .nav-tabbar button.on b{background:rgba(255,255,255,.45);border:1px solid rgba(255,255,255,.8);border-radius:999px;padding:2px 14px;box-shadow:inset 0 1px 0 #fff}
html body .nav-fab-add{background:linear-gradient(180deg,rgba(104,165,255,.9),rgba(58,135,254,.95))!important;border:1px solid rgba(255,255,255,.5)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 10px 24px rgba(58,135,254,.36)!important}
html body .nav-fab-top{background:rgba(255,255,255,.25)!important;color:#3A87FE!important;border:1px solid rgba(255,255,255,.75)!important;-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);box-shadow:inset 0 1px 0 #fff,0 6px 16px rgba(30,64,175,.12)!important}
html body .overlay{background:rgba(207,227,255,.35)!important;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
html body .dialog{background:rgba(255,255,255,.4)!important;-webkit-backdrop-filter:blur(30px) saturate(180%);backdrop-filter:blur(30px) saturate(180%);border:1px solid rgba(255,255,255,.75);border-radius:26px!important;box-shadow:inset 0 1px 0 #fff,0 20px 50px rgba(30,64,175,.2)!important}
html body #modalRoot .dialog .post-modal-head{background:rgba(255,255,255,.55)!important;-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}
html body .post-modal-close{background:rgba(255,255,255,.4)!important;border:1px solid rgba(255,255,255,.8)!important;border-radius:999px!important}
html body .footer{color:#6b7fa6!important}
html body .thumb{border-radius:12px!important;border:1px solid rgba(255,255,255,.8)!important}
html body .warning{background:rgba(255,255,255,.3)!important;color:#1E50E6!important;border-color:rgba(255,255,255,.7)!important}
html body #archiveEyebrow,html body .section-head h2,html body #view h2,html body .note h3,html body .folder strong,html body .platform strong{text-shadow:0 0 14px rgba(58,135,254,.28)}
html body .archive-menu-backdrop{background:rgba(207,227,255,.35)!important;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
html body .archive-menu-drawer{background:rgba(246,250,255,.86)!important;-webkit-backdrop-filter:blur(30px) saturate(180%);backdrop-filter:blur(30px) saturate(180%);border-color:rgba(255,255,255,.75)!important;box-shadow:inset 0 1px 0 #fff,0 20px 50px rgba(30,64,175,.18)!important;color:#1E50E6!important}
html body .archive-menu-drawer h2,html body .archive-menu-drawer .archive-menu-heading{color:#1E50E6!important}
html body .archive-menu-drawer .archive-menu-group{border-color:rgba(58,135,254,.16)!important}
html body .archive-menu-drawer.archive-menu-inactive{background:#F6FAFF!important}
html body .archive-menu-drawer .archive-menu-close{background:rgba(255,255,255,.4)!important;color:#1E50E6!important;border:1px solid rgba(255,255,255,.8)!important;border-radius:999px!important;box-shadow:inset 0 1px 0 #fff,0 4px 12px rgba(30,64,175,.1)!important}
/* 흐림 효과를 지원하지 않거나 '투명도 줄이기'를 켠 기기: 반투명 흰색으로 대체 */
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
html body .panel,html body .platform,html body .folder,html body .note,html body .empty,html body .dialog,html body .archive-menu-drawer{background:rgba(255,255,255,.86)!important}
html body #crumb,html body .nav-tabbar{background:rgba(244,248,255,.94)!important}}
@media (prefers-reduced-transparency:reduce){
html body .panel,html body .platform,html body .folder,html body .note,html body .empty,html body .dialog,html body .archive-menu-drawer{background:rgba(255,255,255,.86)!important}
html body #crumb,html body .nav-tabbar{background:rgba(244,248,255,.94)!important}}"""
BLOCK_HTML = f'<style id="{MARK}">/* {MARK}: 리퀴드 글래스 디자인 (liquidglass.py) */\n{CSS}\n</style>'
s_new = re.sub(r'<style id="liquidglass-20261123">.*?</style>', lambda m: BLOCK_HTML, s, flags=re.S)
if s_new == s and BLOCK_HTML not in s:
    assert s.count('</body>') == 1, 'index.html에서 </body> 위치를 찾지 못했습니다. 중단합니다.'
    s_new = s.replace('</body>', BLOCK_HTML + '</body>')
if s_new != s:
    shutil.copy(idx, f'index.html.before-liquidglass-{stamp}.bak')
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (liquidglass.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-liquidglass-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
