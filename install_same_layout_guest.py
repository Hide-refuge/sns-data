#!/usr/bin/env python3
"""Create a read-only guest site from the existing admin UI without modifying admin data."""
from pathlib import Path
import re, sys, shutil
root=Path(__file__).resolve().parent
index=root/'index.html'; font=root/'font-settings.js'; entry=root/'guest-entry.js'; data=root/'guest-data.json'
for p in (index,font,entry,data):
    if not p.is_file(): sys.exit(f'필수 파일이 없습니다: {p.name}')
html=index.read_text(encoding='utf-8'); f=font.read_text(encoding='utf-8'); e=entry.read_text(encoding='utf-8')
if 'GUEST_SAME_LAYOUT_V1' in html: sys.exit('index.html에서 예상하지 못한 게스트 수정 표시가 발견되었습니다. 작업 중단.')
def replace_once(s, old, new, name):
    n=s.count(old)
    if n!=1: sys.exit(f'파일 버전 불일치: {name} (일치 {n}개). 파일을 수정하지 않았습니다.')
    return s.replace(old,new,1)
# Replace the cloud scripts only in the guest copy. Admin index.html remains unchanged.
html=replace_once(html,'<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script><script src="./sync-config.js"></script><script src="./sync.js?v=local-first-20261118-01"></script>', '<script>window.SCRAP_GUEST_MODE=true;</script>', '관리자 클라우드 스크립트 분리')
# Keep the exact rendering functions; use only the public snapshot for guest data.
start=html.index('function openDB(){'); end=html.index('function archiveLocalDay(',start)
html=html[:start]+'''// GUEST_SAME_LAYOUT_V1: public snapshot, no IndexedDB, no Drive, no mutations.
let guestSnapshot={folders:[],posts:[]};
const getAll=async store=>guestSnapshot[store]||[];
const put=async()=>{throw Error('게스트 모드에서는 변경할 수 없습니다.')};
const del=async()=>{throw Error('게스트 모드에서는 삭제할 수 없습니다.')};
'''+html[end:]
html=replace_once(html,"openDB().then(d=>{db=d;window.scrapRefresh=refresh;refresh()}).catch(err=>{$('view').innerHTML=`<div class=\"warning\">브라우저 저장소를 열지 못했습니다. 일반 브라우저에서 열거나 로컬 서버를 이용하세요. ${escapeHtml(err.message)}</div>`});",'''fetch('./guest-data.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(data=>{
 if(!Array.isArray(data.folders)||!Array.isArray(data.posts))throw Error('공개 데이터 형식 오류');
 guestSnapshot={folders:data.folders,posts:data.posts};window.scrapRefresh=refresh;return refresh();
}).catch(err=>{$('view').innerHTML='<div class="warning">게스트 데이터 불러오기 실패: '+escapeHtml(err.message)+'</div>'});''','게스트 초기화')
html=replace_once(html,'<script src="./font-settings.js?v=font-category-cachifix-20261111-02"></script>','<script src="./guest-font-settings.js?v=1"></script>','게스트 폰트 스크립트')
html=html.replace('<script src="./api-settings.js?v=api-key-only-04"></script>','')
# Eliminate buttons that can mutate data. Preserve read-only browsing, search, sort, gallery and font controls.
block='''<style id="guest-readonly-style">
#syncPanel,#importBtn,#exportBtn,#apiSettingsBtn,#addPost,#editFolder,#deleteFolder,
#folderForm,.subfolder-create,[data-editpost],[data-delpost],[data-search-edit],
[data-search-edit-post],[data-folder-reorder],.folder-reorder-handle,
#folderReorderBtn,#folderReorderCancel,#folderReorderSave {display:none!important}
</style>
<script>
document.addEventListener('DOMContentLoaded',()=>{
 const footer=document.querySelector('footer.footer');if(footer)footer.textContent='게스트 체험 모드 · 공개용 스크랩 열람 전용 · 변경 사항은 저장되지 않습니다.';
 const hdr=document.querySelector('header');if(hdr){const b=document.createElement('span');b.textContent='GUEST · 읽기 전용';b.style.cssText='font-size:12px;color:#455abf;font-weight:700;margin-left:8px';hdr.append(b)}
 const hide=()=>{
   document.querySelectorAll('#syncPanel,#importBtn,#exportBtn,#apiSettingsBtn,#addPost,#editFolder,#deleteFolder,#folderForm,[data-editpost],[data-delpost],[data-search-edit],[data-search-edit-post],[data-folder-reorder],.folder-reorder-handle,#folderReorderBtn,#folderReorderCancel,#folderReorderSave').forEach(x=>{x.hidden=true;x.style.display='none'});
   document.querySelectorAll('#view button').forEach(x=>{if(/^(추가|수정|삭제|편집|저장|폴더 생성|스크랩 추가)$/.test(x.textContent.trim())){x.hidden=true;x.style.display='none'}});
 };
 const view=document.getElementById('view');if(view)new MutationObserver(hide).observe(view,{childList:true,subtree:true});hide();
}, {once:true});
document.addEventListener('submit',e=>{if(e.target.closest('#view,#modalRoot')&&!e.target.closest('.font-dialog')){e.preventDefault();e.stopImmediatePropagation();alert('게스트 모드에서는 데이터를 변경할 수 없습니다.')}},true);
document.addEventListener('click',e=>{
 const t=e.target.closest('button');if(!t)return;
 if(t.matches('#addPost,#editFolder,#deleteFolder,[data-editpost],[data-delpost],[data-search-edit],[data-search-edit-post],[data-folder-reorder],#folderReorderBtn,#folderReorderSave,#folderReorderCancel')){e.preventDefault();e.stopImmediatePropagation()}
},true);
</script>'''
html=replace_once(html,'</head>',block+'</head>','읽기 전용 가드')
# Guest font module uses same UI/algorithms, but never localStorage or cloud.
f=replace_once(f,"function loadLocal(){try{const v=JSON.parse(localStorage.getItem(KEY)||'null');return sanitize(v)}catch{return structuredClone(defaults)}}","function loadLocal(){return structuredClone(defaults)}",'폰트 로컬 저장소 읽기 차단')
f=replace_once(f,'function snapshot(v){','function snapshot(v){if(window.SCRAP_GUEST_MODE)return;','폰트 복구 사본 쓰기 차단')
a=f.index('async function save(){');b=f.index('function chooseFontHTML(',a)
f=f[:a]+'''async function save(){
 // Guest-only in-memory changes: no localStorage, IndexedDB or cloud writes.
 rerender();apply();return true;
}
'''+f[b:]
f=replace_once(f,'function reloadCloud(){','function reloadCloud(){if(window.SCRAP_GUEST_MODE)return;','폰트 클라우드 동기화 차단')
f=replace_once(f,"showFontSection(0);\nfor(const pre of ['range','post'])", """showFontSection(0);
if(window.SCRAP_GUEST_MODE){
  tabButtons.slice(2).forEach(b=>b.hidden=true);
  tabRows[1].hidden=true;
  sections.slice(2).forEach(s=>s.hidden=true);
  const notice=document.createElement('p');notice.className='hint';notice.textContent='게스트 체험: 변경 사항은 현재 화면에서만 적용되며 저장되지 않습니다.';
  dialog.querySelector('.font-head').after(notice);
  const a=document.getElementById('fontRangeSave'),b=document.getElementById('fontPostSave');
  if(a)a.textContent='임시 적용';if(b)b.textContent='선택 스크랩에 임시 적용';
}
for(const pre of ['range','post'])""",'폰트 관리 탭 제한')
# Make in-memory rules active on render, preserving existing rule inheritance.
f=f.replace("alert('폰트 설정을 저장했습니다.')","alert(window.SCRAP_GUEST_MODE?'폰트가 임시 적용되었습니다. 새로고침하면 초기화됩니다.':'폰트 설정을 저장했습니다.')")
f=f.replace("alert(selected.size+'개 스크랩의 폰트 설정을 저장했습니다.')","alert(window.SCRAP_GUEST_MODE?'선택한 스크랩에 폰트를 임시 적용했습니다.':selected.size+'개 스크랩의 폰트 설정을 저장했습니다.')")
# Keep the admin entry button, but redirect only guest login to matching-layout page.
e=replace_once(e,"const GUEST_URL = './guest.html';","const GUEST_URL = './guest-app.html';",'게스트 이동 경로')
outputs={'guest-app.html':html,'guest-font-settings.js':f,'guest-entry.js':e}
for name,content in outputs.items():
    p=root/name
    if p.exists():
        bak=root/(name+'.before-same-layout.bak')
        if not bak.exists(): shutil.copy2(p,bak)
    p.write_text(content,encoding='utf-8')
print('생성 완료: guest-app.html, guest-font-settings.js, guest-entry.js')
print('관리자 index.html / sync.js / font-settings.js는 변경하지 않았습니다.')
print('브라우저에서 /guest-app.html 을 열어 공개 데이터와 레이아웃을 확인하세요.')
