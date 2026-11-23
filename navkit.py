# 추가 작업 (navkit-20261123) — 내비게이션 4가지
# 1) 09 뒤로 가기: 화면 이동을 브라우저 기록에 남김 → iPhone 스와이프·뒤로 가기 = 상위 화면으로 이동
#    주소가 #/instagram/폴더 형식으로 바뀌어, 새로고침하거나 주소를 열어도 같은 화면으로 이동
#    휴대폰: 경로 위에 '‹ 상위 폴더' 버튼
# 2) 05 고정 헤더: 스크롤해도 경로(홈 › 플랫폼 › 폴더)와 스크랩 수가 위에 고정 (모든 기기)
# 3) 06 플로팅 버튼 (휴대폰): '+ 스크랩 추가'와 '↑ 맨 위로' — 두 버튼 같은 크기, 기존 '+ 스크랩 추가' 버튼은 휴대폰에서 숨김
# 4) 01 하단 탭바 (휴대폰): 홈 · Instagram · X · YouTube · 블로그
# 5) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성 (게스트는 '+' 버튼 없음)
# 사용: 사이트 폴더에서 python3 navkit.py
import pathlib, re, shutil, sys, datetime

MARK = 'navkit-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="menugrid-20261123"' not in s:
    sys.exit('index.html에 이전 메뉴 2열 수정(menugrid)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')

NAV_CSS = '<style id="navkit-20261123">\n' + '/* navkit-20261123 */\nhtml{scroll-padding-top:56px}\n/* 05 고정 헤더 */\n#crumb{position:sticky;top:0;z-index:5;background:rgba(246,247,251,.96);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);margin-left:-22px;margin-right:-22px;padding:12px 22px;transition:box-shadow .2s}\n#crumb.nav-stuck{box-shadow:0 6px 16px #25315a14}\n#crumb .nav-count{margin-left:auto;font-size:12px;color:#5363b2;background:#eef0fb;border-radius:30px;padding:3px 9px;white-space:nowrap}\n@media(max-width:760px){#crumb{margin-left:-13px;margin-right:-13px;padding:10px 13px}}\n/* 09 뒤로 가기 버튼 (휴대폰만) */\n#crumb .nav-back{display:none}\n/* 06 플로팅 버튼 · 01 하단 탭바 (휴대폰만) */\n.nav-fabs,.nav-tabbar{display:none}\n@media(max-width:699px){\n html{scroll-padding-bottom:96px}\n #crumb{flex-wrap:wrap;row-gap:4px}\n #crumb .nav-back{display:inline-flex;align-items:center;flex:0 0 100%;border:0;background:none;color:#465cc7;font-size:15px;font-weight:600;padding:2px 0 4px;margin:0;text-align:left}\n body.has-tabbar{padding-bottom:calc(68px + env(safe-area-inset-bottom))}\n .nav-tabbar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;z-index:8;background:rgba(255,255,255,.97);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-top:1px solid #e3e7f0;padding:6px 4px calc(6px + env(safe-area-inset-bottom));box-shadow:0 -4px 16px #25315a0d}\n .nav-tabbar button{border:0;background:none;display:flex;flex-direction:column;align-items:center;gap:2px;min-height:48px;justify-content:center;font-size:11px;color:#8b91a1;padding:2px 0}\n .nav-tabbar button b{font-size:19px;line-height:1.1;font-weight:400}\n .nav-tabbar button.on{color:#465cc7;font-weight:700}\n .nav-fabs{display:flex;flex-direction:column;align-items:center;gap:12px;position:fixed;right:16px;bottom:calc(84px + env(safe-area-inset-bottom));z-index:8;pointer-events:none}\n .nav-fab{pointer-events:auto;width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:26px;line-height:1;padding:0;box-sizing:border-box}\n .nav-fab[hidden]{display:none}\n .nav-fab-add{border:0;background:#465cc7;color:#fff;font-size:30px;box-shadow:0 8px 22px #465cc766}\n .nav-fab-top{border:1px solid #dfe3ed;background:#fff;color:#465cc7;box-shadow:0 4px 12px #0001;opacity:0;transform:translateY(10px);transition:opacity .2s,transform .2s;pointer-events:none}\n .nav-fab-top.show{opacity:1;transform:none;pointer-events:auto}\n html body .section-head .actions>#addPost:not(#_){display:none!important}\n body.has-tabbar .folder-reorder-tip,body.has-tabbar .trash-toast{bottom:calc(84px + env(safe-area-inset-bottom))!important}\n}\n' + '</style>'
NAV_JS = '<script id="navkit-20261123-js">\n' + '/* navkit-20261123: 뒤로 가기(브라우저 기록) · 고정 헤더 · 플로팅 버튼 · 하단 탭바 */\n(()=>{\n const PHONE=\'(max-width:699px)\';\n const isPhone=()=>matchMedia(PHONE).matches;\n const view=()=>document.getElementById(\'view\');\n /* ── 09 뒤로 가기: 화면 이동을 브라우저 기록에 남김 ───────────────── */\n const orig=go;let popping=false;\n const key=r=>(r.platform||\'\')+\'/\'+(r.folder||\'\');\n const hashOf=(p,f)=>\'#/\'+(p?encodeURIComponent(p)+(f?\'/\'+encodeURIComponent(f):\'\'):\'\');\n const depth=()=>Number(history.state?.navDepth)||0;\n go=function(platform=null,folder=null){\n  const before=key(route);orig(platform,folder);\n  if(!popping&&key(route)!==before){try{history.pushState({navkit:1,p:route.platform,f:route.folder,navDepth:depth()+1},\'\',hashOf(route.platform,route.folder))}catch{}}\n };\n window.go=go;\n try{history.replaceState({navkit:1,p:null,f:null,navDepth:0},\'\',location.hash&&location.hash.startsWith(\'#/\')?location.hash:hashOf(null,null))}catch{}\n const parseHash=()=>{const m=/^#\\/([^/]*)\\/?([^/]*)$/.exec(location.hash||\'\');if(!m)return{p:null,f:null};return{p:decodeURIComponent(m[1])||null,f:decodeURIComponent(m[2])||null}};\n const valid=(p,f)=>(!p||platforms[p])&&(!f||folders.some(x=>x.id===f&&x.platform===p));\n addEventListener(\'popstate\',e=>{\n  const st=e.state?.navkit?e.state:parseHash();\n  if(document.querySelector(\'#modalRoot .overlay\'))closeModal();\n  const d=document.getElementById(\'archiveMenuDrawer\');if(d&&!d.hidden)d.querySelector(\'.archive-menu-close\')?.click();\n  popping=true;try{if(valid(st.p,st.f))orig(st.p||null,st.f||null);else orig(null,null)}finally{popping=false}\n });\n // 주소(#/플랫폼/폴더)로 들어오면 자료를 불러온 뒤 그 화면으로 이동\n let deep=parseHash(),deepDone=!deep.p,deepStart=Date.now();\n const tryDeep=()=>{if(deepDone)return;if(Date.now()-deepStart>15000){deepDone=true;return}\n  if(typeof folders===\'undefined\')return;\n  if(deep.f&&!folders.some(x=>x.id===deep.f))return;\n  if(!platforms[deep.p]){deepDone=true;return}\n  deepDone=true;popping=true;try{orig(deep.p,deep.f)}finally{popping=false}\n  try{history.replaceState({navkit:1,p:route.platform,f:route.folder,navDepth:0},\'\',hashOf(route.platform,route.folder))}catch{}\n };\n // 휴대폰: 경로 위 \'‹ 상위\' 버튼\n const parentRoute=()=>{if(route.folder){const f=folders.find(x=>x.id===route.folder);return{p:route.platform,f:f?.parentId||null}}return{p:null,f:null}};\n const parentName=()=>{const r=parentRoute();if(r.f)return folders.find(x=>x.id===r.f)?.name||\'상위 폴더\';return r.p?platforms[r.p]?.name||\'플랫폼\':\'홈\'};\n const syncBack=()=>{const c=document.getElementById(\'crumb\');let b=document.getElementById(\'navBack\');\n  if(!c||!(route.platform||route.folder)){b?.remove();return}\n  if(!b){b=document.createElement(\'button\');b.type=\'button\';b.id=\'navBack\';b.className=\'nav-back\';\n   b.addEventListener(\'click\',()=>{const r=parentRoute();if(depth()>0&&history.state?.navkit)history.back();else go(r.p,r.f)})}\n  b.textContent=\'‹ \'+parentName();if(c.firstElementChild!==b)c.prepend(b)};\n /* ── 05 고정 헤더: 경로 + 스크랩 수 ─────────────────────────────── */\n const syncCount=()=>{const c=document.getElementById(\'crumb\');if(!c)return;let s=c.querySelector(\'.nav-count\');\n  const list=document.getElementById(\'postList\');const n=list?list.querySelectorAll(\'.note\').length:0;\n  if(list){if(!s){s=document.createElement(\'span\');s.className=\'nav-count\'}s.textContent=\'스크랩 \'+n+\'개\';if(c.lastElementChild!==s)c.appendChild(s)}else s?.remove()};\n const syncStuck=()=>{const c=document.getElementById(\'crumb\');if(c)c.classList.toggle(\'nav-stuck\',scrollY>8&&c.getBoundingClientRect().top<=1)};\n /* ── 06 플로팅 버튼 (휴대폰): + 스크랩 추가 · ↑ 맨 위로, 같은 크기 ─────── */\n const fabs=document.createElement(\'div\');fabs.className=\'nav-fabs\';\n const up=document.createElement(\'button\');up.type=\'button\';up.id=\'fabTop\';up.className=\'nav-fab nav-fab-top\';up.setAttribute(\'aria-label\',\'맨 위로\');up.textContent=\'↑\';\n const add=document.createElement(\'button\');add.type=\'button\';add.id=\'fabAdd\';add.className=\'nav-fab nav-fab-add\';add.setAttribute(\'aria-label\',\'스크랩 추가\');add.textContent=\'+\';\n up.addEventListener(\'click\',()=>scrollTo({top:0,behavior:\'smooth\'}));\n add.addEventListener(\'click\',()=>document.getElementById(\'addPost\')?.click());\n fabs.append(up,add);\n const syncFab=()=>{const canAdd=!window.SCRAP_GUEST_MODE&&!!document.getElementById(\'addPost\');add.hidden=!canAdd;up.classList.toggle(\'show\',scrollY>500)};\n /* ── 01 하단 탭바 (휴대폰): 홈 + 플랫폼 ─────────────────────────── */\n const bar=document.createElement(\'nav\');bar.className=\'nav-tabbar\';bar.setAttribute(\'aria-label\',\'플랫폼 이동\');\n bar.innerHTML=[[\'\',\'⌂\',\'홈\'],...Object.entries(platforms).map(([k,v])=>[k,v.glyph,k===\'naverblog\'?\'블로그\':k===\'twitter\'?\'X\':v.name])]\n  .map(([k,g,n])=>`<button type="button" data-navtab="${k}"><b aria-hidden="true">${g}</b><span>${n}</span></button>`).join(\'\');\n bar.addEventListener(\'click\',e=>{const b=e.target.closest(\'[data-navtab]\');if(!b)return;const k=b.dataset.navtab||null;if(k===route.platform&&!route.folder){scrollTo({top:0,behavior:\'smooth\'});return}go(k,null)});\n const syncBar=()=>{bar.querySelectorAll(\'[data-navtab]\').forEach(b=>{const on=(b.dataset.navtab||null)===(route.platform||null);b.classList.toggle(\'on\',on);b.setAttribute(\'aria-current\',on?\'page\':\'false\')});\n  document.body.classList.toggle(\'has-tabbar\',isPhone())};\n const all=()=>{tryDeep();syncBack();syncCount();syncStuck();syncFab();syncBar()};\n const start=()=>{document.body.append(fabs,bar);const v=view();if(v)new MutationObserver(all).observe(v,{childList:true,subtree:true});\n  addEventListener(\'scroll\',()=>{syncStuck();syncFab()},{passive:true});matchMedia(PHONE).addEventListener?.(\'change\',all);all()};\n if(document.readyState===\'loading\')document.addEventListener(\'DOMContentLoaded\',start);else start();\n})();\n' + '</script>\n'
if MARK not in s:
    assert s.count('</head>') == 1 and s.count('</body>') == 1 and s.count('function go(platform=null,folder=null){') == 1, 'index.html에서 바꿀 위치를 찾지 못했습니다. 중단합니다.'
    shutil.copy(idx, f'index.html.before-navkit-{stamp}.bak')
    s = s.replace('</head>', NAV_CSS + '</head>').replace('</body>', NAV_JS + '</body>')
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (navkit.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-navkit-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
