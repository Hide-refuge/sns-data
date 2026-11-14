/* Curated by Hide — folder emoji picker v2. Existing folder records are unchanged. */
(()=>{
'use strict';
const CDN='https://cdn.jsdelivr.net/npm/emoji-picker-element@1.28.1/+esm';
let loading;
const css=document.createElement('style');
css.textContent=`
.folder-emoji-options[hidden]{display:none!important}
.cbh-emoji-launch{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:8px 0}
.cbh-emoji-current{font-size:30px;min-width:42px;text-align:center}
.cbh-emoji-dialog{border:0;border-radius:16px;padding:18px;width:min(450px,calc(100vw - 20px));max-height:90dvh;box-shadow:0 18px 55px #0004;background:white;color:#293142}
.cbh-emoji-dialog::backdrop{background:#11182799}
.cbh-emoji-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px}
.cbh-emoji-dialog emoji-picker{width:100%;height:min(520px,65dvh);--emoji-size:1.65rem;--num-columns:8}
@media(max-width:420px){.cbh-emoji-dialog emoji-picker{--num-columns:7}}
`;
document.head.append(css);
function enhance(options){
 if(options.dataset.cbhEnhanced)return;
 const field=options.closest('.field'),input=field?.querySelector('input[name="icon"]');
 if(!field||!input)return;
 options.dataset.cbhEnhanced='yes';
 const launch=document.createElement('div');launch.className='cbh-emoji-launch';
 const current=document.createElement('span');current.className='cbh-emoji-current';current.textContent=input.value||'📁';
 const button=document.createElement('button');button.type='button';button.className='btn';button.textContent='전체 이모지 검색 · 카테고리 선택';
 launch.append(current,button);options.before(launch);
 options.hidden=true;
 let dialog=null;
 button.addEventListener('click',async()=>{
  if(!input.isConnected)return;
  if(!dialog){
   dialog=document.createElement('dialog');dialog.className='cbh-emoji-dialog';
   dialog.innerHTML='<div class="cbh-emoji-head"><strong>폴더 아이콘 선택</strong><button type="button" class="btn" data-close-emoji>닫기</button></div><div data-emoji-host>이모지 목록을 불러오는 중…</div><p class="hint">검색창 또는 카테고리에서 이모지를 선택하세요.</p>';
   document.body.append(dialog);
   dialog.querySelector('[data-close-emoji]').onclick=()=>dialog.close();
   dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  }
  dialog.showModal();
  const host=dialog.querySelector('[data-emoji-host]');
  if(host.querySelector('emoji-picker'))return;
  host.textContent='이모지 목록을 불러오는 중…';
  try{
   loading ||= import(CDN).catch(err=>{loading=null;throw err});
   await loading;
   if(!dialog.open||!input.isConnected)return;
   const picker=document.createElement('emoji-picker');
   picker.setAttribute('locale','ko');
   picker.addEventListener('emoji-click',event=>{
    const emoji=event.detail?.unicode;if(!emoji)return;
    input.value=emoji;current.textContent=emoji;
    const preview=input.closest('form')?.querySelector('[data-preview-icon]');if(preview)preview.textContent=emoji;
    options.querySelectorAll('[data-emoji]').forEach(b=>b.classList.toggle('selected',b.dataset.emoji===emoji));
    dialog.close();
   });
   host.replaceChildren(picker);
  }catch(err){
   console.error('Emoji picker load error',err);
   host.textContent='전체 이모지 목록을 불러오지 못했습니다. 네트워크를 확인하거나 아래 기본 이모지 목록을 사용해 주세요.';
   options.hidden=false;
  }
 });
}
function scan(){document.querySelectorAll('.folder-emoji-options').forEach(enhance)}
let queued=false;
const observer=new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;scan()})});
function start(){scan();observer.observe(document.getElementById('view')||document.body,{childList:true,subtree:true});observer.observe(document.getElementById('modalRoot')||document.body,{childList:true,subtree:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
