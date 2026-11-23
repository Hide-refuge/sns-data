# 추가 작업 (foldertrash-20261123)
# 1) 폴더 화면의 '폴더 삭제': 현재 폴더가 아니라, 그 안의 하위 폴더를 골라서 삭제
#    (하위 폴더가 없으면 '삭제할 하위 폴더가 없습니다' 안내만 표시)
# 2) 플랫폼 화면(맨 위 단계)에 '폴더 삭제' 버튼 추가: 맨 위 단계 폴더를 골라서 삭제
# 3) 삭제하면 선택한 폴더와 그 아래 모든 하위 폴더·스크랩을 함께 '휴지통'으로 이동
#    스크랩 개별 삭제도 휴지통으로 이동. 관리 메뉴 > 백업 관리 > '휴지통'에서 복원·영구 삭제·비우기
#    (휴지통 항목은 Google Drive 동기화에 함께 저장되며, 게스트 공개용 JSON·GitHub 게시에는 포함되지 않음)
# 4) 게스트 화면(guest-app.html)을 고친 index.html 기준으로 다시 생성
# 사용: 사이트 폴더에서 python3 foldertrash.py
import pathlib, re, shutil, sys, datetime

MARK = 'foldertrash-20261123'
idx, guest = pathlib.Path('index.html'), pathlib.Path('guest-app.html')
menu, gje, gdp = pathlib.Path('archive-menu.js'), pathlib.Path('guest-json-export.js'), pathlib.Path('github-direct-publish.js')
s, g_old = idx.read_text(encoding='utf-8'), guest.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
changed = []
if 'id="foldercount-20261123"' not in s:
    sys.exit('index.html에 이전 폴더 숫자 수정(foldercount)이 없습니다. main 최신 내용에서 브랜치를 만들었는지 확인해 주세요. 중단합니다.')

TRASH_JS = '/* foldertrash-20261123: 폴더 삭제 = 하위 폴더 선택 삭제, 삭제한 폴더·스크랩은 휴지통으로 */\nfunction trashToast(text){document.getElementById(\'trashToast\')?.remove();const t=document.createElement(\'div\');t.id=\'trashToast\';t.className=\'trash-toast\';t.textContent=text;document.body.appendChild(t);setTimeout(()=>t.remove(),3200)}\nasync function trashItems(folderIds,postIds,label){\n const id=\'trash-\'+Date.now().toString(36)+Math.random().toString(36).slice(2,6),at=new Date().toISOString();\n const fset=new Set(folderIds),pset=new Set(postIds);\n for(const f of folders.filter(x=>fset.has(x.id)))await put(\'folders\',{...f,trashedAt:at,trashId:id,trashLabel:label});\n for(const p of posts.filter(x=>pset.has(x.id)))await put(\'posts\',{...p,trashedAt:at,trashId:id,trashLabel:label});\n}\nfunction openFolderDeleteDialog(parentId,platform){\n const kids=folderChildren(parentId||null,platform);\n const title=parentId?\'하위 폴더 삭제\':\'폴더 삭제\';\n if(!kids.length){modal(`<h2>${title}</h2><p class="hint">삭제할 하위 폴더가 없습니다.</p><div class="actions" style="justify-content:flex-end"><button class="btn" type="button" data-close>닫기</button></div>`);return}\n modal(`<h2>${title}</h2><form id="folderDeleteForm"><div class="field"><label for="folderDeleteTarget">삭제할 폴더</label><select id="folderDeleteTarget">${kids.map(f=>`<option value="${escapeHtml(f.id)}">${escapeHtml(f.icon||\'📁\')} ${escapeHtml(f.name)} (하위 폴더 ${folderChildren(f.id,platform).length}개 · 스크랩 ${folderPostTotal(f.id)}개)</option>`).join(\'\')}</select></div><p class="hint">선택한 폴더와 그 안의 모든 하위 폴더·스크랩이 휴지통으로 이동합니다. 관리 메뉴의 \'휴지통\'에서 복원할 수 있습니다.</p><div class="actions" style="justify-content:flex-end"><button class="btn" type="button" data-close>취소</button><button class="btn danger" type="submit">휴지통으로 이동</button></div></form>`);\n}\ndocument.addEventListener(\'submit\',async e=>{\n if(e.target.id!==\'folderDeleteForm\')return;\n e.preventDefault();\n const f=folders.find(x=>x.id===document.getElementById(\'folderDeleteTarget\').value);if(!f)return;\n const ids=[f.id,...folderDescendants(f.id)],idset=new Set(ids),ps=posts.filter(p=>idset.has(p.folderId)).map(p=>p.id);\n if(!confirm(`\'${f.name}\' 폴더와 그 안의 하위 폴더 ${ids.length-1}개(아래 모든 단계), 스크랩 ${ps.length}개를 휴지통으로 옮기시겠습니까?`))return;\n try{await trashItems(ids,ps,`폴더 \'${f.name}\'`);closeModal();await refresh();trashToast(\'휴지통으로 옮겼습니다 · 관리 메뉴 > 휴지통에서 복원할 수 있습니다\')}\n catch(err){alert(\'삭제 실패: \'+err.message)}\n});\nfunction trashGroups(fa,pa){\n const m=new Map();\n for(const [kind,list] of [[\'folders\',fa],[\'posts\',pa]])for(const x of list){if(!x.trashedAt)continue;const k=x.trashId||(\'t-\'+x.trashedAt);\n  if(!m.has(k))m.set(k,{id:k,label:x.trashLabel||\'삭제한 항목\',at:x.trashedAt,folders:[],posts:[]});m.get(k)[kind].push(x)}\n return [...m.values()].sort((a,b)=>String(b.at).localeCompare(String(a.at)));\n}\nasync function openTrash(){\n const [fa,pa]=await Promise.all([getAllRaw(\'folders\'),getAllRaw(\'posts\')]);\n const groups=trashGroups(fa,pa);\n const when=v=>{try{return new Date(v).toLocaleString(\'ko-KR\',{dateStyle:\'medium\',timeStyle:\'short\'})}catch{return \'\'}};\n modal(`<h2>휴지통</h2><p class="hint">삭제한 폴더·스크랩입니다. 복원하면 원래 위치로 돌아갑니다. 영구 삭제하면 되돌릴 수 없습니다.</p>${groups.length?`<div class="trash-list">${groups.map(g=>`<div class="trash-item"><div class="trash-info"><strong>${escapeHtml(g.label)}</strong><small>${escapeHtml(when(g.at))} · 폴더 ${g.folders.length}개 · 스크랩 ${g.posts.length}개</small></div><div class="trash-actions"><button type="button" class="btn" data-trash-restore="${escapeHtml(g.id)}">복원</button><button type="button" class="btn danger" data-trash-purge="${escapeHtml(g.id)}">영구 삭제</button></div></div>`).join(\'\')}</div><div class="actions trash-foot"><button type="button" class="btn danger" data-trash-empty>휴지통 비우기</button><button type="button" class="btn" data-close>닫기</button></div>`:`<div class="empty">휴지통이 비어 있습니다.</div><div class="actions trash-foot" style="justify-content:flex-end"><button type="button" class="btn" data-close>닫기</button></div>`}`);\n}\nlet trashPendingPosts=null;\nasync function restoreTrash(id){\n const [fa,pa]=await Promise.all([getAllRaw(\'folders\'),getAllRaw(\'posts\')]);\n const g=trashGroups(fa,pa).find(x=>x.id===id);if(!g)return;\n const clean=x=>{const y={...x};delete y.trashedAt;delete y.trashId;delete y.trashLabel;return y};\n const active=new Set(fa.filter(x=>!x.trashedAt).map(x=>x.id)),batch=new Set(g.folders.map(x=>x.id));let lifted=0;\n for(const f of g.folders){const y=clean(f);if(y.parentId&&!active.has(y.parentId)&&!batch.has(y.parentId)){y.parentId=null;lifted++}await put(\'folders\',y)}\n const ok=new Set([...active,...batch]),orphans=[];\n for(const p of g.posts){const y=clean(p);if(!ok.has(y.folderId)){orphans.push(p);continue}await put(\'posts\',y)}\n await refresh();\n if(orphans.length){trashPendingPosts=orphans;const platform=orphans[0].platform;\n  const opts=folderOptionHtml(platform,\'\',null);\n  if(!folders.some(f=>f.platform===platform)){alert(\'원래 폴더가 없어 스크랩을 복원할 수 없습니다. 먼저 폴더를 복원하거나 만들어 주세요.\');trashPendingPosts=null;return openTrash()}\n  modal(`<h2>스크랩 복원 위치</h2><form id="trashRestoreForm"><p class="hint">원래 폴더가 없거나 휴지통에 있어, 스크랩 ${orphans.length}개를 넣을 폴더를 골라 주세요.</p><div class="field"><label for="trashRestoreTarget">복원할 폴더</label><select id="trashRestoreTarget">${opts}</select></div><div class="actions" style="justify-content:flex-end"><button class="btn" type="button" data-close>취소</button><button class="btn primary" type="submit">복원</button></div></form>`);return}\n closeModal();trashToast(lifted?\'복원했습니다 · 원래 상위 폴더가 없어 맨 위 단계로 복원했습니다\':\'복원했습니다\');\n}\ndocument.addEventListener(\'submit\',async e=>{\n if(e.target.id!==\'trashRestoreForm\')return;e.preventDefault();\n const target=document.getElementById(\'trashRestoreTarget\').value;if(!target||!trashPendingPosts)return;\n for(const p of trashPendingPosts){const y={...p,folderId:target};delete y.trashedAt;delete y.trashId;delete y.trashLabel;await put(\'posts\',y)}\n trashPendingPosts=null;closeModal();await refresh();trashToast(\'복원했습니다\');\n});\nasync function purgeTrash(id){\n const [fa,pa]=await Promise.all([getAllRaw(\'folders\'),getAllRaw(\'posts\')]);\n const groups=trashGroups(fa,pa).filter(g=>id==null||g.id===id);\n const nf=groups.reduce((a,g)=>a+g.folders.length,0),np=groups.reduce((a,g)=>a+g.posts.length,0);\n if(!groups.length)return;\n if(!confirm(`폴더 ${nf}개, 스크랩 ${np}개를 영구 삭제합니다. 되돌릴 수 없습니다. 계속하시겠습니까?`))return;\n for(const g of groups){for(const p of g.posts)await del(\'posts\',p.id);for(const f of g.folders)await del(\'folders\',f.id)}\n await refresh();await openTrash();\n}\ndocument.addEventListener(\'click\',async e=>{\n const b=e.target.closest(\'#openFolderDelete,#backupTrashBtn,[data-trash-restore],[data-trash-purge],[data-trash-empty]\');if(!b||window.SCRAP_GUEST_MODE)return;\n e.preventDefault();\n try{\n  if(b.id===\'openFolderDelete\')openFolderDeleteDialog(null,route.platform);\n  else if(b.id===\'backupTrashBtn\')await openTrash();\n  else if(b.dataset.trashRestore)await restoreTrash(b.dataset.trashRestore);\n  else if(b.dataset.trashPurge)await purgeTrash(b.dataset.trashPurge);\n  else if(b.hasAttribute(\'data-trash-empty\'))await purgeTrash(null);\n }catch(err){alert(\'휴지통 작업 실패: \'+err.message)}\n});\n'
CSS = """<style id="foldertrash-20261123">
/* foldertrash-20261123 */
html body header.top .actions #openFolderDelete{display:inline-flex;align-items:center;justify-content:center;height:42px;min-height:42px;padding:0 14px;font-size:14px;line-height:1;border-radius:8px;box-sizing:border-box;white-space:nowrap}
.trash-list{display:flex;flex-direction:column;gap:10px;max-height:55vh;overflow:auto;margin:6px 0 0}
.trash-item{display:flex;justify-content:space-between;align-items:center;gap:12px;border:1px solid #e3e7f0;border-radius:12px;padding:12px 14px;background:#fff}
.trash-info{min-width:0}.trash-info strong{display:block;word-break:keep-all;overflow-wrap:break-word}.trash-info small{color:#8b91a1}
.trash-actions{display:flex;gap:6px;flex:none}
.trash-foot{justify-content:space-between;margin-top:14px}
.trash-toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#1c2d52;color:#fff;padding:12px 16px;border-radius:12px;z-index:100000;font-size:14px;line-height:1.4;width:max-content;max-width:calc(100vw - 24px);box-sizing:border-box;text-align:center;box-shadow:0 8px 24px #0003}
@media(max-width:520px){.trash-item{flex-direction:column;align-items:stretch}.trash-actions{justify-content:flex-end}}
</style>"""
OLD_DEL = "else if(t.id==='deleteFolder'){const f=folders.find(f=>f.id===route.folder),related=posts.filter(p=>p.folderId===f.id);if(folderChildren(f.id,f.platform).length){alert('하위 폴더가 존재합니다. 하위 폴더를 먼저 이동하거나 삭제해 주세요.');return}if(confirm(`'${f.name}' 폴더와 스크랩 ${related.length}개를 모두 삭제하시겠습니까?`)){for(const p of related)await del('posts',p.id);await del('folders',f.id);route.folder=null;await refresh()}}"
NEW_DEL = "else if(t.id==='deleteFolder'){const f=folders.find(f=>f.id===route.folder);if(f)openFolderDeleteDialog(f.id,f.platform)}"
OLD_DELPOST = "else if(t.dataset.delpost){if(confirm('이 스크랩을 삭제하시겠습니까?')){await del('posts',t.dataset.delpost);await refresh()}}"
NEW_DELPOST = "else if(t.dataset.delpost){const p=posts.find(x=>x.id===t.dataset.delpost);if(p&&confirm('이 스크랩을 휴지통으로 옮기시겠습니까? 관리 메뉴의 휴지통에서 복원할 수 있습니다.')){await trashItems([],[p.id],`스크랩 '${p.title||'제목 없음'}'`);await refresh();trashToast('휴지통으로 옮겼습니다')}}"
OLD_SYNC = """function syncFolderCreateButton(){
  const show=Boolean(route.platform&&!route.folder);
  let btn=document.getElementById('openFolderCreate');
  if(!show){if(btn)btn.remove();return}
  const actions=document.querySelector('header.top .actions');
  if(!actions)return;
  if(!btn){btn=document.createElement('button');btn.type='button';btn.id='openFolderCreate';btn.className='btn primary';btn.textContent='+ 폴더 생성'}
  const toggle=document.getElementById('archiveMenuToggle');
  if(toggle&&toggle.parentElement===actions){if(btn.nextElementSibling!==toggle)actions.insertBefore(btn,toggle)}
  else if(btn.parentElement!==actions)actions.appendChild(btn);
}
"""
NEW_SYNC = """function syncFolderCreateButton(){
  const show=Boolean(route.platform&&!route.folder);
  let btn=document.getElementById('openFolderCreate'),dbtn=document.getElementById('openFolderDelete');
  if(!show){if(btn)btn.remove();if(dbtn)dbtn.remove();return}
  const actions=document.querySelector('header.top .actions');
  if(!actions)return;
  if(!btn){btn=document.createElement('button');btn.type='button';btn.id='openFolderCreate';btn.className='btn primary';btn.textContent='+ 폴더 생성'}
  if(!dbtn){dbtn=document.createElement('button');dbtn.type='button';dbtn.id='openFolderDelete';dbtn.className='btn danger';dbtn.textContent='폴더 삭제'}
  const toggle=document.getElementById('archiveMenuToggle');
  const anchor=toggle&&toggle.parentElement===actions?toggle:null;
  if(btn.parentElement!==actions||btn.nextElementSibling!==dbtn||dbtn.nextElementSibling!==anchor){actions.insertBefore(btn,anchor);actions.insertBefore(dbtn,anchor)}
}
"""
REPL = [
    ("const getAll=async s=>{\n // CBH_LOCAL_FIRST_V1", "const getAllRaw=async s=>{\n // CBH_LOCAL_FIRST_V1"),
    ("return cached??transact(s,'readonly',o=>o.getAll());\n};\nconst put=",
     "return cached??transact(s,'readonly',o=>o.getAll());\n};\n// foldertrash-20261123: 휴지통 항목은 화면에서 제외\nconst getAll=async s=>{const all=await getAllRaw(s);return Array.isArray(all)?all.filter(x=>!x?.trashedAt):all};\nconst put="),
    ("const [savedFolders,savedPosts]=await Promise.all([getAll('folders'),getAll('posts')]);",
     "const [savedFolders,savedPosts]=await Promise.all([getAllRaw('folders'),getAllRaw('posts')]);"),
    (OLD_DEL, NEW_DEL), (OLD_DELPOST, NEW_DELPOST), (OLD_SYNC, NEW_SYNC),
    ("function folderOptionHtml(", TRASH_JS + "function folderOptionHtml("),
    ('<button class="btn" id="exportBtn">Backup_Export</button>', '<button class="btn" id="exportBtn">Backup_Export</button><button class="btn" id="backupTrashBtn" type="button">휴지통</button>'),
    ('./archive-menu.js?v=guestsync-20261123', './archive-menu.js?v=' + MARK),
    ('./guest-json-export.js?v=1"', './guest-json-export.js?v=' + MARK + '"'),
    ('./github-direct-publish.js?v=1"', './github-direct-publish.js?v=' + MARK + '"'),
    ('</head>', CSS + '</head>'),
]
JS_REPL = {
    menu: [("if (el.id === 'openFolderCreate') return;", "if (el.id === 'openFolderCreate' || el.id === 'openFolderDelete') return;")],
    gje: [("""        const [folders, posts] = await Promise.all([
          window.scrapSync.getAll('folders'),
          window.scrapSync.getAll('posts')
        ]);""", """        const [allFolders, allPosts] = await Promise.all([
          window.scrapSync.getAll('folders'),
          window.scrapSync.getAll('posts')
        ]);
        // foldertrash-20261123: 휴지통 항목은 공개용 JSON에서 제외
        const folders = Array.isArray(allFolders) ? allFolders.filter(x => !x?.trashedAt) : allFolders;
        const posts = Array.isArray(allPosts) ? allPosts.filter(x => !x?.trashedAt) : allPosts;""")],
    gdp: [("""    const [folders, posts] = await Promise.all([
      window.scrapSync.getAll('folders'),
      window.scrapSync.getAll('posts')
    ]);""", """    const [allFolders, allPosts] = await Promise.all([
      window.scrapSync.getAll('folders'),
      window.scrapSync.getAll('posts')
    ]);
    // foldertrash-20261123: 휴지통 항목은 게시 데이터에서 제외
    const folders = Array.isArray(allFolders) ? allFolders.filter(x => !x?.trashedAt) : allFolders;
    const posts = Array.isArray(allPosts) ? allPosts.filter(x => !x?.trashedAt) : allPosts;""")],
}
if MARK not in s:
    for old, new in REPL:
        assert s.count(old) == 1, 'index.html에서 바꿀 위치를 찾지 못했습니다 → ' + old[:60] + ' … 중단합니다.'
    texts = {p: p.read_text(encoding='utf-8') for p in JS_REPL}
    for p, pairs in JS_REPL.items():
        for old, new in pairs:
            assert texts[p].count(old) == 1, f'{p}에서 바꿀 위치를 찾지 못했습니다. 중단합니다.'
    shutil.copy(idx, f'index.html.before-foldertrash-{stamp}.bak')
    for old, new in REPL:
        s = s.replace(old, new)
    idx.write_text(s, encoding='utf-8'); changed.append('index.html')
    for p, pairs in JS_REPL.items():
        shutil.copy(p, f'{p.name}.before-foldertrash-{stamp}.bak')
        t = texts[p]
        for old, new in pairs:
            t = t.replace(old, new)
        p.write_text(t, encoding='utf-8'); changed.append(p.name)

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
GUEST_HEAD = f'''<!-- {MARK}: 이 파일은 index.html에서 자동 생성됩니다 (foldertrash.py). 게스트 전용 부분 외에는 index.html과 같습니다. -->
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
    shutil.copy(guest, f'guest-app.html.before-foldertrash-{stamp}.bak')
    guest.write_text(g, encoding='utf-8')
    changed.append('guest-app.html')
print('적용 완료:', ', '.join(changed) if changed else '변경 없음 (이미 최신)')
