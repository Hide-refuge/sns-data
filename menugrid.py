# 추가 작업 (menugrid-20261123)
# 1) 관리 메뉴 버튼을 한 줄에 2개씩 배치 — iPad·컴퓨터 화면에서만 (휴대폰 화면은 그대로)
#    (사이트 설정·백업 관리·클라우드 동기화 버튼 모두, '휴지통'은 백업 관리 맨 끝으로)
# 2) 동기화 안내 "…변경 사항이 있습니다. / 지금 동기화를 눌러 업로드하세요." 를 두 줄로 — iPad·컴퓨터 화면에서만
# 3) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 menugrid.py
import pathlib, re, shutil, sys, datetime

MARK = 'menugrid-20261123'
idx, guest, menu = pathlib.Path('index.html'), pathlib.Path('guest-app.html'), pathlib.Path('archive-menu.js')
s, g_old, m = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8'), menu.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="foldertrash-20261123"' not in s:
    sys.exit('index.html에 이전 휴지통 수정(foldertrash)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')

WIDE = '(min-width:700px) and (min-height:540px)'   # iPad·컴퓨터 (휴대폰은 세로·가로 모두 제외)
CSS = """<style id="menugrid-20261123">
/* menugrid-20261123: iPad·컴퓨터 화면에서만 관리 메뉴 버튼 2개씩 한 줄 */
@media """ + WIDE + """{
 html body #archiveMenuDrawer .archive-menu-items:not(#_),
 html body #archiveMenuDrawer #syncControls>.actions:not(#_){display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;justify-content:center!important;align-items:stretch!important;gap:8px!important;width:100%!important;max-width:100%!important;align-self:stretch!important;flex:0 0 auto!important}
 html body #archiveMenuDrawer .archive-menu-items>button:not(#_),
 html body #archiveMenuDrawer .archive-menu-items>a:not(#_),
 html body #archiveMenuDrawer #syncControls>.actions>button:not(#_),
 html body #archiveMenuDrawer #syncControls>.actions>a:not(#_){flex:0 0 calc(50% - 4px)!important;width:calc(50% - 4px)!important;max-width:calc(50% - 4px)!important;align-self:stretch!important;margin:0!important}
 html body #archiveMenuDrawer .archive-menu-items>span:not(#_){flex:0 0 100%!important;text-align:center}
 html body #archiveMenuDrawer #backupTrashBtn:not(#_){order:1!important}
}
/* 휴대폰 화면에서는 동기화 안내의 추가 줄바꿈을 쓰지 않음 */
@media (max-width:699px),(max-height:539px){#archiveMenuDrawer br[data-wide-break]{display:none}}
</style>"""
M_OLD1 = """  const splitBefore = [
    '다른 기기의 수정이 있다면',
    '기존 Supabase는',
    '저장 시 업로드',
    'Google Drive 실제',
  ];"""
M_NEW1 = """  const splitBefore = [
    '다른 기기의 수정이 있다면',
    '기존 Supabase는',
    '저장 시 업로드',
    'Google Drive 실제',
    '지금 동기화를 눌러',
  ];
  // menugrid-20261123: iPad·컴퓨터 화면에서만 줄바꿈하는 문구
  const wideOnly = new Set(['지금 동기화를 눌러']);"""
M_OLD2 = """      if (el.dataset.archiveCloudFormatted === 'true') return;
      if (el.children.length) return;"""
M_NEW2 = """      // 문구가 나중에 바뀌면(동기화 상태 변경) 다시 줄바꿈 처리
      if (el.dataset.archiveCloudFormatted === el.textContent) return;
      if (el.children.length) return;"""
M_OLD3 = """          {text:part.text.slice(at).trimStart(), breakBefore:true});"""
M_NEW3 = """          {text:part.text.slice(at).trimStart(), breakBefore:true, wide:wideOnly.has(phrase)});"""
M_OLD4 = """        if (part.breakBefore) el.appendChild(document.createElement('br'));
        el.appendChild(document.createTextNode(part.text));
      });
      el.dataset.archiveCloudFormatted = 'true';"""
M_NEW4 = """        if (part.breakBefore) {
          if (part.wide) el.appendChild(document.createTextNode(' '));
          const br = document.createElement('br');
          if (part.wide) br.dataset.wideBreak = '';
          el.appendChild(br);
        }
        el.appendChild(document.createTextNode(part.text));
      });
      el.dataset.archiveCloudFormatted = el.textContent;"""
if MARK not in s:
    assert s.count('</head>') == 1 and s.count('./archive-menu.js?v=foldertrash-20261123') == 1, 'index.html에서 바꿀 위치를 찾지 못했습니다. 중단합니다.'
    for old in (M_OLD1, M_OLD2, M_OLD3, M_OLD4):
        assert m.count(old) == 1, 'archive-menu.js에서 바꿀 위치를 찾지 못했습니다 → ' + old.strip()[:50] + ' … 중단합니다.'
    shutil.copy(idx, f'index.html.before-menugrid-{stamp}.bak'); shutil.copy(menu, f'archive-menu.js.before-menugrid-{stamp}.bak')
    for old, new in ((M_OLD1, M_NEW1), (M_OLD2, M_NEW2), (M_OLD3, M_NEW3), (M_OLD4, M_NEW4)):
        m = m.replace(old, new)
    menu.write_text(m, encoding='utf-8'); changed.append('archive-menu.js')
    s = s.replace('</head>', CSS + '</head>').replace('./archive-menu.js?v=foldertrash-20261123', './archive-menu.js?v=' + MARK)
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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (menugrid.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-menugrid-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
