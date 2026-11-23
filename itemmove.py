# 추가 작업 (item-move-20261123): 스크랩·폴더 길게 눌러 순서 변경 / 다른 폴더로 이동
# - 스크랩: 길게 누른 채 끌어서 ① 다른 스크랩 위에 놓으면 순서 변경(정렬 '직접 정렬'로 전환)
#                              ② 하위 폴더 카드나 위쪽 경로(상위 폴더)에 놓으면 그 폴더로 이동
#          길게 누르고 손을 떼면 → 터치로 위치 지정 또는 [다른 폴더로 이동] 선택 창
# - 폴더: 기존 길게 눌러 순서 변경 유지 + 길게 누르고 떼면 [다른 폴더로 이동] 선택 창 추가
# 사용: 사이트 폴더에서 python3 itemmove.py   (이미 적용되어 있으면 아무것도 바꾸지 않음)
import pathlib, shutil, sys, datetime

idx = pathlib.Path('index.html')
s = idx.read_text(encoding='utf-8')
MARK = 'item-move-20261123'
if MARK in s:
    sys.exit('이미 적용되어 있습니다. 변경 없음.')
if 'menu-platforms-20261123' not in s:
    sys.exit('먼저 메뉴·플랫폼 작업(menu platforms)이 적용되어 있어야 합니다.')


def rep(old, new):
    global s
    assert s.count(old) == 1, f'바꿀 위치를 찾지 못함 → {old[:70]}'
    s = s.replace(old, new)


# 1) 화면 표시용 CSS
rep('</style><!-- mobile-popup-layer-fix:start -->', '''/* item-move-20261123: 스크랩 끌어서 이동 */
#postList .note.item-dragging{opacity:.4}
#postList .note.item-selected{outline:3px solid #185DFF;outline-offset:2px;background:#edf3ff}
#postList .note.item-drop-before{box-shadow:0 -4px 0 #185DFF}
#postList .note.item-drop-after{box-shadow:0 4px 0 #185DFF}
#postList.folder-post-grid .note.item-drop-before{box-shadow:-4px 0 0 #185DFF}
#postList.folder-post-grid .note.item-drop-after{box-shadow:4px 0 0 #185DFF}
.item-drop-into{box-shadow:inset 0 0 0 3px #185DFF!important;background:#edf3ff!important}
.item-move-hint{font-size:12px;color:#8c91a0;font-weight:400;margin-left:8px}
.folder-reorder-tip button+button{margin-left:6px}
@media (hover:none){#postList .note{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}}
</style><!-- mobile-popup-layer-fix:start -->''')

# 2) 정렬에 '직접 정렬' 추가 + 화면 안내 문구
rep('<option value="name">가나다순</option></select><select id="display"',
    '<option value="name">가나다순</option><option value="manual">직접 정렬</option></select><select id="display"')
rep('<h3>현재 폴더의 스크랩</h3>', '<h3>현재 폴더의 스크랩<span class="item-move-hint">길게 눌러 순서 변경 · 다른 폴더로 이동</span></h3>')
rep('<h3>하위 폴더</h3>', '<h3>하위 폴더<span class="item-move-hint">길게 눌러 순서 변경 · 다른 폴더로 이동</span></h3>')
rep("list.sort((a,b)=>sort==='name'?", "list.sort((a,b)=>sort==='manual'?manualPostCompare(a,b):sort==='name'?")
# 순서를 직접 바꾼 적이 있는 폴더는 처음부터 '직접 정렬'로 표시
rep("toggle.setAttribute('aria-expanded',String(!emoji.hidden))}}updatePostList()}",
    "toggle.setAttribute('aria-expanded',String(!emoji.hidden))}}if($('sort')&&posts.some(p=>p.folderId===f.id&&Number.isFinite(p.sortOrder)))$('sort').value='manual';updatePostList()}")

# 3) 기존 폴더 길게 누르기: 안내창에 [다른 폴더로 이동] 버튼
rep("tip.innerHTML='이동할 위치의 다른 폴더를 터치하세요. <button type=\"button\" id=\"folderReorderCancel\">취소</button>';",
    "tip.innerHTML='순서를 바꿀 위치의 폴더를 터치하세요. <button type=\"button\" id=\"folderMoveOpen\">다른 폴더로 이동</button><button type=\"button\" id=\"folderReorderCancel\">취소</button>';")
rep("if(e.target.closest?.('#folderReorderCancel')){e.preventDefault();e.stopImmediatePropagation();stopSelection();return}",
    "if(e.target.closest?.('#folderMoveOpen')){e.preventDefault();e.stopImmediatePropagation();const id=selected?.dataset.folder;stopSelection();blockClickUntil=0;if(id)window.openItemMoveDialog?.('folder',id);return}"
    "if(e.target.closest?.('#folderReorderCancel')){e.preventDefault();e.stopImmediatePropagation();stopSelection();return}")

# 3-1) 기존 버그 수정: 마우스로 길게 누르고 떼면 바로 뒤따르는 클릭 때문에 선택이 즉시 취소되던 문제
rep("if(selected&&target){e.preventDefault();e.stopImmediatePropagation();void saveSelection(target);return}",
    "if(selected&&target){e.preventDefault();e.stopImmediatePropagation();if(target===selected&&Date.now()<blockClickUntil)return;void saveSelection(target);return}")

# 4) 스크랩 끌어서 이동 + 이동 선택 창
MODULE = r'''
/* item-move-20261123: 스크랩 길게 눌러 순서 변경 · 다른 폴더로 이동, 폴더 이동 선택 창 */
function manualPostCompare(a,b){const ao=Number.isFinite(a.sortOrder)?a.sortOrder:-1,bo=Number.isFinite(b.sortOrder)?b.sortOrder:-1;if(ao===-1&&bo===-1)return String(b.createdAt||'').localeCompare(String(a.createdAt||''));return ao-bo}
(()=>{
 const LONG=420,TOL=9,EDGE=70;
 let pending=null,active=null,selected=null,blockClickUntil=0,scrollRaf=0;
 const noteOf=n=>n?.closest?.('#postList .note[data-font-post]');
 const folderCardOf=n=>n?.closest?.('#view .folders .folder[data-folder]');
 const crumbOf=n=>n?.closest?.('#crumb button[data-folder]');
 const isControl=n=>n?.closest?.('a,button,select,input,textarea,label,img,.thumb');
 const postById=id=>posts.find(p=>p.id===id);
 const clearPending=()=>{if(pending?.timer)clearTimeout(pending.timer);pending=null};
 const searching=()=>Boolean($('search')?.value.trim());
 function toast(msg){let t=document.getElementById('itemMoveToast');if(!t){t=document.createElement('div');t.id='itemMoveToast';t.className='folder-reorder-tip';document.body.appendChild(t)}t.textContent=msg;clearTimeout(t._h);t._h=setTimeout(()=>t.remove(),2600)}
 async function movePost(p,folderId){
   if(!p||!folderId||p.folderId===folderId)return false;
   const dest=folders.find(f=>f.id===folderId);if(!dest)return false;
   const rec={...p,folderId,updatedAt:today()};delete rec.sortOrder;
   await put('posts',rec);toast(`‘${p.title||'제목 없음'}’ → ‘${dest.name}’ 폴더로 이동했습니다.`);return true;
 }
 async function moveFolder(f,parentId){
   parentId=parentId||null;
   if(!f||folderParent(f)===parentId)return false;
   if(parentId&&(parentId===f.id||folderDescendants(f.id).has?.(parentId)||[...folderDescendants(f.id)].includes(parentId)))throw Error('자기 자신이나 하위 폴더 안으로는 옮길 수 없습니다.');
   const sib=folderChildren(parentId,f.platform).filter(x=>x.id!==f.id);
   const next=sib.reduce((m,x)=>Number.isFinite(x.sortOrder)?Math.max(m,x.sortOrder+1):m,sib.length);
   await put('folders',{...f,parentId,sortOrder:next});
   const dest=parentId?folders.find(x=>x.id===parentId)?.name:'최상위';toast(`‘${f.name}’ → ‘${dest}’(으)로 이동했습니다.`);return true;
 }
 async function reorderPost(dragId,targetId,after){
   const ids=[...document.querySelectorAll('#postList .note[data-font-post]')].map(n=>n.dataset.fontPost);
   const from=ids.indexOf(dragId);if(from<0||!ids.includes(targetId)||dragId===targetId)return;
   ids.splice(from,1);let to=ids.indexOf(targetId)+(after?1:0);ids.splice(to,0,dragId);
   for(let i=0;i<ids.length;i++){const p=postById(ids[i]);if(p&&p.sortOrder!==i)await put('posts',{...p,sortOrder:i})}
   toast('스크랩 순서를 바꿨습니다. (정렬: 직접 정렬)');
 }
 async function run(job){try{await job()}catch(err){alert('이동 실패: '+(err?.message||err))}await refresh()}
 window.openItemMoveDialog=(kind,id)=>{
   const isFolder=kind==='folder',item=isFolder?folders.find(f=>f.id===id):postById(id);if(!item)return;
   const current=isFolder?folderParent(item):item.folderId;
   const opts=isFolder?`<option value="" ${current?'':'selected'}>최상위 (${escapeHtml(platforms[item.platform]?.name||'플랫폼')} 바로 아래)</option>`+folderOptionHtml(item.platform,current,item.id):folderOptionHtml(item.platform,current);
   modal(`<h2>${isFolder?'폴더':'스크랩'} 이동</h2><form id="itemMoveForm"><p class="hint">‘${escapeHtml(isFolder?item.name:(item.title||'제목 없음'))}’을(를) 옮길 위치를 고르세요.</p><div class="field"><label for="itemMoveTarget">이동할 폴더</label><select id="itemMoveTarget">${opts}</select></div><div class="actions" style="justify-content:flex-end"><button class="btn" type="button" data-close>취소</button><button class="btn primary" type="submit">이동</button></div></form>`);
   $('itemMoveForm').onsubmit=async e=>{e.preventDefault();const v=$('itemMoveTarget').value;closeModal();await run(()=>isFolder?moveFolder(item,v||null):movePost(item,v))};
 };
 // ── 끌기
 function dropTargetAt(x,y,d){
   const el=document.elementFromPoint(x,y);
   const n=noteOf(el);
   if(n&&n!==d.el){if(searching())return null;const r=n.getBoundingClientRect(),grid=$('postList')?.classList.contains('folder-post-grid');return {kind:'note',el:n,after:grid?x>r.left+r.width/2:y>r.top+r.height/2}}
   const fc=folderCardOf(el);if(fc&&fc.dataset.folder!==route.folder)return {kind:'folder',el:fc};
   const cb=crumbOf(el);if(cb&&cb.dataset.folder!==route.folder)return {kind:'folder',el:cb};
   return null;
 }
 function paint(d,t){
   d.target?.el.classList.remove('item-drop-before','item-drop-after','item-drop-into');d.target=t;
   if(t)t.el.classList.add(t.kind==='note'?(t.after?'item-drop-after':'item-drop-before'):'item-drop-into');
 }
 function startDrag(el,x,y){
   if(selected||!el.isConnected)return;
   const b=el.getBoundingClientRect(),ghost=el.cloneNode(true);
   ghost.removeAttribute('data-font-post');
   Object.assign(ghost.style,{position:'fixed',left:b.left+'px',top:b.top+'px',width:b.width+'px',height:Math.min(b.height,220)+'px',overflow:'hidden',margin:'0',zIndex:'99999',pointerEvents:'none',opacity:'.95',boxShadow:'0 12px 30px #1d33603b',background:'#fff'});
   document.body.appendChild(ghost);
   active={el,ghost,dx:x-b.left,dy:y-b.top,x,y,target:null};
   el.classList.add('item-dragging');blockClickUntil=Date.now()+450;
   const loop=()=>{if(!active)return;const d=active;let dy=d.y<EDGE?-14:d.y>innerHeight-EDGE?14:0;if(dy){scrollBy(0,dy);paint(d,dropTargetAt(d.x,d.y,d))}scrollRaf=requestAnimationFrame(loop)};scrollRaf=requestAnimationFrame(loop);
 }
 function moveDrag(x,y){if(!active)return;const d=active;d.x=x;d.y=y;d.ghost.style.left=(x-d.dx)+'px';d.ghost.style.top=(y-d.dy)+'px';paint(d,dropTargetAt(x,y,d))}
 async function finishDrag(cancel){
   clearPending();if(!active)return;
   const d=active;active=null;cancelAnimationFrame(scrollRaf);blockClickUntil=Date.now()+450;
   d.ghost.remove();d.el.classList.remove('item-dragging');const t=d.target;paint(d,null);
   if(cancel)return;
   const id=d.el.dataset.fontPost;
   if(!t){select(d.el);return}
   if(t.kind==='note')await run(()=>reorderPost(id,t.el.dataset.fontPost,t.after));
   else await run(()=>movePost(postById(id),t.el.dataset.folder));
 }
 // ── 길게 누르고 뗐을 때: 선택 모드
 function select(el){
   selected=el;el.classList.add('item-selected');
   let tip=document.getElementById('itemMoveTip');if(!tip){tip=document.createElement('div');tip.id='itemMoveTip';tip.className='folder-reorder-tip';document.body.appendChild(tip)}
   tip.innerHTML=(searching()?'하위 폴더를 터치하면 그 폴더로 옮깁니다.':'옮길 위치의 스크랩이나 하위 폴더를 터치하세요.')+' <button type="button" id="itemMoveOpen">다른 폴더로 이동</button><button type="button" id="itemMoveCancel">취소</button>';
 }
 function unselect(){selected?.classList.remove('item-selected');selected=null;document.getElementById('itemMoveTip')?.remove()}
 document.addEventListener('click',e=>{
   if(e.target.closest?.('#itemMoveOpen')){e.preventDefault();e.stopImmediatePropagation();const id=selected?.dataset.fontPost;unselect();if(id)window.openItemMoveDialog('post',id);return}
   if(e.target.closest?.('#itemMoveCancel')){e.preventDefault();e.stopImmediatePropagation();unselect();return}
   if(selected){
     const id=selected.dataset.fontPost,n=noteOf(e.target),fc=folderCardOf(e.target)||crumbOf(e.target);
     if(n&&n!==selected&&!searching()){e.preventDefault();e.stopImmediatePropagation();const ids=[...document.querySelectorAll('#postList .note[data-font-post]')].map(x=>x.dataset.fontPost);const after=ids.indexOf(n.dataset.fontPost)>ids.indexOf(id);unselect();void run(()=>reorderPost(id,n.dataset.fontPost,after));return}
     if(fc&&fc.dataset.folder!==route.folder){e.preventDefault();e.stopImmediatePropagation();unselect();void run(()=>movePost(postById(id),fc.dataset.folder));return}
     if(n===selected){e.preventDefault();e.stopImmediatePropagation();return}
     unselect();return;
   }
   if(Date.now()<blockClickUntil&&noteOf(e.target)){e.preventDefault();e.stopImmediatePropagation()}
 },true);
 // ── 터치·마우스 입력 (폴더 길게 누르기와 같은 방식)
 const begin=(target,x,y)=>{if(active||selected)return;const el=noteOf(target);if(!el||isControl(target))return;clearPending();const timer=setTimeout(()=>{if(pending?.timer===timer){pending=null;startDrag(el,x,y)}},LONG);pending={timer,x,y}};
 document.addEventListener('touchstart',e=>{if(e.touches.length===1){const t=e.touches[0];begin(e.target,t.clientX,t.clientY)}},{capture:true,passive:true});
 document.addEventListener('touchmove',e=>{const t=e.touches[0];if(!t)return;if(active){if(e.cancelable)e.preventDefault();moveDrag(t.clientX,t.clientY)}else if(pending&&Math.hypot(t.clientX-pending.x,t.clientY-pending.y)>TOL)clearPending()},{capture:true,passive:false});
 document.addEventListener('touchend',e=>{if(active){const t=e.changedTouches[0];if(t)moveDrag(t.clientX,t.clientY);void finishDrag(false)}else clearPending()},{capture:true});
 document.addEventListener('touchcancel',()=>{if(active)void finishDrag(true);else clearPending()},{capture:true});
 document.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'||e.button!==0)return;begin(e.target,e.clientX,e.clientY)},true);
 document.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;if(active){moveDrag(e.clientX,e.clientY);e.preventDefault()}else if(pending&&Math.hypot(e.clientX-pending.x,e.clientY-pending.y)>TOL)clearPending()},true);
 document.addEventListener('pointerup',e=>{if(e.pointerType!=='touch'){if(active)void finishDrag(false);else clearPending()}},true);
 document.addEventListener('pointercancel',e=>{if(e.pointerType!=='touch'){if(active)void finishDrag(true);else clearPending()}},true);
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(active)void finishDrag(true);if(selected)unselect()}});
})();
'''
rep("\n})();\ndocument.addEventListener('click',async e=>{const t=e.target.closest('button,a,img');",
    "\n})();" + MODULE + "document.addEventListener('click',async e=>{const t=e.target.closest('button,a,img');")

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy(idx, f'index.html.before-itemmove-{stamp}.bak')
idx.write_text(s, encoding='utf-8')
print(f'적용 완료: index.html (백업: index.html.before-itemmove-{stamp}.bak)')
