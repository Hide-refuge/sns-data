# 추가 작업 (liquidglass2-20261126) — iOS 리퀴드 글래스 원칙 반영 + 검토 의견 수정
# 1) 카드(내용)는 잘 읽히는 서리 유리, 버튼·탭바·메뉴(조작)만 맑은 유리 / 버튼 위쪽 반사광
# 2) 파란색은 주요 동작(스크랩 추가·폴더 생성·＋)에만, '+ 하위 폴더 생성'은 유리 버튼
# 3) 휴대폰 하단 탭바: 떠 있는 캡슐 / 관리 메뉴: 떠 있는 유리판(더 불투명) / 팝업: 뒤를 살짝 어둡게
# 4) 뒷배경 채도 75% / 헤더 아래 색 차이 제거 / 경로 줄: 글자 길이에 맞춘 캡슐(스크랩 수 버튼은 기존 색)
# 5) 휴대폰 홈 플랫폼 카드 4개가 한 화면에 보이도록 축소 / 폰트 설정 창 윗부분 흰 배경 삭제 / 색상 칩 둥근 네모
# 6) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 liquidglass2.py  (여러 번 실행해도 결과 같음)
# 되돌리기: 만들어진 .bak 파일로 복원하거나, index.html에서 id가 liquidglass2-20261126인 style·script 두 부분을 지우고 다시 실행
import pathlib, re, shutil, sys, datetime

MARK = 'liquidglass2-20261126'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="liquidglass-20261123"' not in s:
    sys.exit('index.html에 이전 디자인(liquidglass)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')
CSS = r"""/* liquidglass2-20261126: iOS 리퀴드 글래스 원칙 반영 (내용층·조작층 분리, 떠 있는 캡슐, 가장자리 반사광, 동심 모서리) */
/* 1) 내용층(카드)은 잘 읽히는 서리 유리, 조작층(버튼·탭바·메뉴)만 맑은 유리 */
html body .panel,html body .platform,html body .folder,html body .note,html body .empty{
 background:linear-gradient(165deg,rgba(255,255,255,.74),rgba(255,255,255,.56))!important;
 -webkit-backdrop-filter:blur(18px) saturate(140%);backdrop-filter:blur(18px) saturate(140%);
 border:1px solid rgba(255,255,255,.8)!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.95),0 1px 2px rgba(30,64,175,.05),0 12px 32px -12px rgba(30,64,175,.18)!important}
html body .note{border-left:1px solid rgba(255,255,255,.8)!important}
html body .folder{border-top:1px solid rgba(255,255,255,.95)!important}
html body #archiveEyebrow,html body .section-head h2,html body #view h2,html body .note h3,html body .folder strong,html body .platform strong{text-shadow:none!important}
/* 2) 동심 모서리: 카드 22px 안쪽 요소는 그보다 작게 */
html body .thumb{border-radius:10px!important}
html body .note .chip{background:rgba(58,135,254,.08)!important;border-color:rgba(58,135,254,.10)!important;-webkit-backdrop-filter:none;backdrop-filter:none}
/* 3) 유리 버튼: 위쪽 반사광 + 가장자리 빛 테두리 */
html body .btn,html body a.btn,html body .archive-menu-toggle,html body .nav-fab-top,html body .post-modal-close,html body .archive-menu-drawer .archive-menu-close{
 background:radial-gradient(120% 90% at 30% 0%,rgba(255,255,255,.78),rgba(255,255,255,0) 58%),rgba(255,255,255,.34)!important;
 border:1px solid rgba(255,255,255,.75)!important;
 -webkit-backdrop-filter:blur(14px) saturate(180%);backdrop-filter:blur(14px) saturate(180%);
 box-shadow:inset 1px 1px 0 rgba(255,255,255,.95),inset -1px -1px 0 rgba(255,255,255,.4),0 1px 2px rgba(30,64,175,.06),0 6px 16px -4px rgba(30,64,175,.16)!important}
html body .archive-menu-toggle{border-radius:999px!important}
/* 4) 색은 주요 동작 하나에만: 스크랩 추가·폴더 생성·＋ 버튼 */
html body .btn.primary,html body #openFolderCreate,html body .nav-fab-add{
 background:radial-gradient(120% 90% at 30% 0%,rgba(255,255,255,.45),rgba(255,255,255,0) 55%),linear-gradient(180deg,#5C9EFF,#3A87FE)!important;color:#fff!important;
 border:1px solid rgba(255,255,255,.5)!important;
 box-shadow:inset 1px 1px 0 rgba(255,255,255,.6),inset -1px -1px 0 rgba(255,255,255,.18),0 8px 20px -4px rgba(58,135,254,.5)!important}
html body .section-head .actions>#openSubfolderModal{background:radial-gradient(120% 90% at 30% 0%,rgba(255,255,255,.78),rgba(255,255,255,0) 58%),rgba(255,255,255,.34)!important;color:#1E50E6!important;border:1px solid rgba(255,255,255,.75)!important;box-shadow:inset 1px 1px 0 rgba(255,255,255,.95),inset -1px -1px 0 rgba(255,255,255,.4),0 6px 16px -4px rgba(30,64,175,.16)!important}
html body .btn:active,html body .nav-fab:active,html body .nav-tabbar button:active{transform:scale(.96)}
html body .btn,html body .nav-fab{transition:transform .15s ease,box-shadow .2s ease}
/* 5) 상단 경로 줄: 딱딱한 띠 대신 아래로 흐려지는 가장자리 */
html body #crumb{background:linear-gradient(180deg,rgba(244,248,255,.82) 0%,rgba(244,248,255,.6) 70%,rgba(244,248,255,0) 100%)!important;
 -webkit-backdrop-filter:blur(14px) saturate(170%);backdrop-filter:blur(14px) saturate(170%);
 -webkit-mask-image:linear-gradient(180deg,#000 72%,transparent);mask-image:linear-gradient(180deg,#000 72%,transparent);
 box-shadow:none!important;padding-bottom:20px!important;margin-bottom:-8px}
html body #crumb.nav-stuck{box-shadow:none!important}
/* 6) 휴대폰 하단 탭바: 화면 가장자리에서 떨어져 떠 있는 캡슐 */
@media (max-width:699px){
 html body .nav-tabbar{left:12px;right:12px;bottom:calc(8px + env(safe-area-inset-bottom));padding:6px 6px;border-radius:32px;
  background:radial-gradient(120% 100% at 30% 0%,rgba(255,255,255,.7),rgba(255,255,255,0) 60%),rgba(240,246,255,.74)!important;
  -webkit-backdrop-filter:blur(24px) saturate(190%);backdrop-filter:blur(24px) saturate(190%);
  border:1px solid rgba(255,255,255,.75)!important;
  box-shadow:inset 1px 1px 0 rgba(255,255,255,.95),inset -1px -1px 0 rgba(255,255,255,.45),0 12px 30px -8px rgba(30,64,175,.28)!important}
 html body .nav-tabbar button{min-height:50px;border-radius:26px}
 html body .nav-tabbar button.on{background:rgba(58,135,254,.12)!important;color:#1E50E6!important}
 html body .nav-tabbar button.on b{background:none!important;border:0!important;padding:0!important;box-shadow:none!important}
 html body .nav-fabs{bottom:calc(92px + env(safe-area-inset-bottom))}
 html body .app{padding-bottom:calc(96px + env(safe-area-inset-bottom))!important}
}
/* 7) 관리 메뉴: 화면 끝에 붙지 않고 떠 있는 유리판 */
html body .archive-menu-drawer{top:10px!important;right:10px!important;height:calc(100dvh - 20px)!important;border-radius:30px!important;border:1px solid rgba(255,255,255,.85)!important;
 background:radial-gradient(90% 40% at 20% 0%,rgba(255,255,255,.7),rgba(255,255,255,0) 60%),rgba(244,249,255,.87)!important;
 box-shadow:inset 1px 1px 0 #fff,inset -1px -1px 0 rgba(255,255,255,.5),0 24px 60px -12px rgba(30,64,175,.3)!important}
html body .archive-menu-backdrop{background:rgba(22,42,92,.12)!important;-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
/* 8) 입력 창(팝업): 뒤를 살짝 어둡게 해 집중, 창은 더 불투명한 유리 */
html body .overlay{background:rgba(22,42,92,.18)!important;-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}
html body .dialog{background:radial-gradient(90% 40% at 20% 0%,rgba(255,255,255,.75),rgba(255,255,255,0) 60%),rgba(246,250,255,.82)!important;border:1px solid rgba(255,255,255,.9)!important;border-radius:32px!important;
 box-shadow:inset 1px 1px 0 #fff,inset -1px -1px 0 rgba(255,255,255,.5),0 30px 70px -16px rgba(30,64,175,.35)!important}
html body input,html body select,html body textarea{background:rgba(255,255,255,.55)!important;border:1px solid rgba(58,135,254,.14)!important;box-shadow:inset 0 1px 2px rgba(30,64,175,.06)!important}
html body input:focus,html body select:focus,html body textarea:focus{outline:none;border-color:rgba(58,135,254,.55)!important;box-shadow:0 0 0 4px rgba(58,135,254,.16)!important}
/* ── 2차 수정 (사용자 검토 반영) ── */
/* 9) 뒷배경 채도: 현재 대비 75% */
html body{background:#F5F8FE!important}
html body::before{background:radial-gradient(42% 32% at 12% 18%,rgba(83,140,230,.256),transparent 70%),radial-gradient(38% 30% at 92% 46%,rgba(253,239,253,.76),transparent 70%),
 radial-gradient(46% 34% at 38% 92%,rgba(83,140,230,.192),transparent 72%),linear-gradient(180deg,#FAFBFE 0%,#ECF2FC 60%,#DEEAFA 100%)!important}
/* 10) 경로 줄: 글자 길이에 맞춘 유리 캡슐 (스크랩 수는 오른쪽 작은 캡슐 유지) */
html body #crumb{background:transparent!important;-webkit-backdrop-filter:none;backdrop-filter:none;padding-top:8px!important;padding-bottom:10px!important;margin-bottom:-4px}
html body #crumb.nav-stuck{background:linear-gradient(180deg,rgba(244,248,255,.6) 0%,rgba(244,248,255,.35) 70%,rgba(244,248,255,0) 100%)!important;-webkit-backdrop-filter:blur(14px) saturate(170%);backdrop-filter:blur(14px) saturate(170%)}
html body #crumb .crumb-path{display:inline-flex;align-items:center;flex-wrap:wrap;gap:4px 8px;min-width:0;max-width:100%;box-sizing:border-box;padding:8px 16px;border-radius:22px;color:#1E50E6!important;
 background:radial-gradient(120% 90% at 30% 0%,rgba(255,255,255,.8),rgba(255,255,255,0) 58%),rgba(255,255,255,.5);
 border:1px solid rgba(255,255,255,.8);-webkit-backdrop-filter:blur(16px) saturate(180%);backdrop-filter:blur(16px) saturate(180%);
 box-shadow:inset 1px 1px 0 rgba(255,255,255,.95),inset -1px -1px 0 rgba(255,255,255,.4),0 6px 16px -4px rgba(30,64,175,.16)}
html body #crumb .nav-count{padding:6px 12px!important;border:0!important;background:rgba(58,135,254,.12)!important;color:#2A6FE0!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.6)!important}
@media (max-width:699px){
 html body #crumb{gap:6px!important}
 html body #crumb .crumb-path{padding:6px 12px;gap:3px 6px}
 html body #crumb .nav-count{padding:5px 10px!important}
}
/* 11) 휴대폰 홈 플랫폼 카드: 4개가 하단 탭바 위 한 화면에 모두 보이도록 축소 */
@media (max-width:760px){
 html body #view .platform{padding:11px 13px!important;gap:6px!important;border-radius:18px!important}
 html body #view .platform>*{zoom:.76}
 html body #view .platform>.muted:last-child{padding-top:0!important}
 html body #view .grid:has(>.platform){gap:10px}
}
/* 12) 관리 메뉴 판: 비치는 정도를 80%로 (위 7번 배경값에 반영) */
/* 13) 폰트 설정 창 윗부분: 흰색 배경 삭제, 내용이 지나갈 때만 흐리게 */
html body #modalRoot .font-dialog .font-head{background:transparent!important;border-bottom:0!important;padding-bottom:16px!important;
 -webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);-webkit-mask-image:linear-gradient(180deg,#000 78%,transparent);mask-image:linear-gradient(180deg,#000 78%,transparent)}
/* 14) 폴더 테두리 색상 칩: 모서리가 둥근 네모 유리 칩 */
html body .folder-color-picker input[type=color]{-webkit-appearance:none;appearance:none;width:44px!important;height:44px!important;min-width:44px;padding:5px!important;border-radius:14px!important;cursor:pointer;
 border:1px solid rgba(255,255,255,.9)!important;background:radial-gradient(120% 90% at 30% 0%,rgba(255,255,255,.85),rgba(255,255,255,0) 60%),rgba(255,255,255,.45)!important;
 -webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);box-shadow:inset 1px 1px 0 #fff,inset -1px -1px 0 rgba(255,255,255,.5),0 6px 14px -4px rgba(30,64,175,.22)!important}
html body .folder-color-picker input[type=color]::-webkit-color-swatch-wrapper{padding:0}
html body .folder-color-picker input[type=color]::-webkit-color-swatch{border:0;border-radius:9px;box-shadow:inset 0 0 0 1px rgba(30,64,175,.18)}
html body .folder-color-picker input[type=color]::-moz-color-swatch{border:0;border-radius:9px}
/* 투명도 줄이기·흐림 미지원 기기 */
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
 html body .nav-tabbar,html body .dialog,html body .archive-menu-drawer{background:rgba(246,250,255,.96)!important}
 html body #crumb .crumb-path,html body #crumb .nav-count{background:rgba(255,255,255,.94)!important}
 html body #modalRoot .font-dialog .font-head{background:rgba(246,250,255,.96)!important;-webkit-mask-image:none;mask-image:none}
 html body #crumb{background:rgba(244,248,255,.96)!important;-webkit-mask-image:none;mask-image:none}}
@media (prefers-reduced-transparency:reduce){
 html body .panel,html body .platform,html body .folder,html body .note,html body .empty{background:rgba(255,255,255,.92)!important}
 html body .nav-tabbar,html body .dialog,html body .archive-menu-drawer{background:rgba(246,250,255,.96)!important}
 html body #crumb .crumb-path,html body #crumb .nav-count{background:rgba(255,255,255,.94)!important}
 html body #modalRoot .font-dialog .font-head{background:rgba(246,250,255,.96)!important;-webkit-mask-image:none;mask-image:none}
 html body #crumb{background:rgba(244,248,255,.96)!important;-webkit-mask-image:none;mask-image:none}}"""
JS = r"""/* 경로 줄 캡슐: 홈 › 플랫폼 › 폴더 부분을 하나의 묶음(.crumb-path)으로 감쌈 */
(()=>{const c=document.getElementById('crumb');if(!c)return;
 const wrap=()=>{let p=c.querySelector(':scope>.crumb-path');
  const items=[...c.children].filter(x=>x!==p&&x.id!=='navBack'&&!x.classList.contains('nav-count'));
  if(!items.length)return;
  if(!p){p=document.createElement('span');p.className='crumb-path'}
  items.forEach(x=>p.appendChild(x));
  if(p.parentNode!==c){const b=c.querySelector(':scope>#navBack');b?b.after(p):c.prepend(p)}};
 new MutationObserver(wrap).observe(c,{childList:true});wrap();})();"""
BLOCK_HTML = (f'<style id="{MARK}">\n{CSS}\n</style>'
              f'<script id="{MARK}-crumb">\n{JS}\n</script>')
s_new = re.sub(r'<style id="liquidglass2-20261126">.*?</style><script id="liquidglass2-20261126-crumb">.*?</script>', lambda m: BLOCK_HTML, s, flags=re.S)
if s_new == s and BLOCK_HTML not in s:
    assert 'liquidglass2-20261126' not in s, 'index.html의 이전 적용 부분 모양이 달라 자동 교체할 수 없습니다. .bak 파일로 복원 후 다시 실행해 주세요. 중단합니다.'
    assert s.count('</body>') == 1, 'index.html에서 </body> 위치를 찾지 못했습니다. 중단합니다.'
    s_new = s.replace('</body>', BLOCK_HTML + '</body>')
if s_new != s:
    shutil.copy(idx, f'index.html.before-liquidglass2-{stamp}.bak')
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (liquidglass2.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-liquidglass2-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
