/* Curated by Hide — Unicode emoji picker add-on. No folder data migration. */
(()=>{
'use strict';
const PICKER_URL='https://cdn.jsdelivr.net/npm/emoji-picker-element@1.28.1/+esm';
let pickerPromise=null;
const loadPicker=()=>pickerPromise||(pickerPromise=import(PICKER_URL).then(m=>m.default||m.Picker).catch(e=>{pickerPromise=null;throw e}));
const style=document.createElement('style');
style.textContent=`
.cbh-emoji-launch{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:8px 0}
.cbh-emoji-current{font-size:30px;line-height:1.5;min-width:42px;text-align:center}
.cbh-emoji-dialog{border:0;border-radius:16px;padding:18px;width:min(430px,calc(100vw - 24px));max-height:92dvh;box-shadow:0 18px 55px #0004;background:#fff;color:#293142}
.cbh-emoji-dialog::backdrop{background:#11182799}
.cbh-emoji-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px}
.cbh-emoji-dialog emoji-picker{width:100%;height:min(520px,68dvh);--emoji-size:1.65rem;--num-columns:8}
.cbh-emoji-fallback{font-size:12px;color:#7d4c00;margin-top:8px}
@media(max-width:420px){.cbh-emoji-dialog emoji-picker{--num-columns:7}}
`;
document.head.appendChild(style);
function enhance(options){
 if(options.dataset.cbhEnhanced)return;
 const field=options.closest('.field');const input=field?.querySelector('input[name="icon"]');
 if(!field||!input)return;
 options.dataset.cbhEnhanced='1';
 const launch=document.createElement('div');launch.className='cbh-emoji-launch';
 const current=document.createElement('span');current.className='cbh-emoji-current';current.textContent=input.value||'📁';
 const button=document.createElement('button');button.type='button';button.className='btn';button.textContent='전체 이모지 검색 · 카테고리 선택';
 launch.append(current,button);
 const note=document.createElement('div');note.className='hint';note.textContent='Unicode 이모지 전체 목록에서 선택합니다. 기기에 따라 일부 이모지 모양이 다를 수 있습니다.';
 options.before(launch,note);
 // Keep the original 24 buttons as a working fallback if the picker CDN is unavailable.
 options.hidden=true;
 const dialog=document.createElement('dialog');dialog.className='cbh-emoji-dialog';
 dialog.innerHTML='<div class="cbh-emoji-head"><strong>폴더 아이콘 선택</strong><button type="button" class="btn" data-cbh-close>닫기</button></div><div data-cbh-picker-host></div><p class="hint">검색창에서 이름을 검색하거나 카테고리를 선택해 주세요.</p>';
 document.body.appendChild(dialog);
 const close=()=>dialog.close();dialog.querySelector('[data-cbh-close]').addEventListener('click',close);
 dialog.addEventListener('click',e=>{if(e.target===dialog)close()});
 button.addEventListener('click',async()=>{
  if(!input.isConnected){dialog.remove();return}
  dialog.showModal();const host=dialog.querySelector('[data-cbh-picker-host]');
  if(host.firstElementChild)return;
  host.textContent='이모지 목록 불러오는 중…';
  try{
   const Picker=await loadPicker();
   if(!dialog.open)return;
   const picker=new Picker({locale:'ko'});
   picker.addEventListener('emoji-click',event=>{
    const emoji=event.detail?.unicode;if(!emoji)return;
    input.value=emoji;current.textContent=emoji;
    const form=input.closest('form');
    const preview=form?.querySelector('[data-preview-icon]');if(preview)preview.textContent=emoji;
    options.querySelectorAll('[data-emoji]').forEach(b=>b.classList.toggle('selected',b.dataset.emoji===emoji));
    close();
   });
   host.replaceChildren(picker);
  }catch(e){
   console.warn('Emoji picker unavailable:',e);
   host.textContent='전체 목록을 불러오지 못했습니다. 네트워크 연결을 확인해 주세요. 아래 기본 이모지 목록은 사용할 수 있습니다.';
   options.hidden=false;
  }
 });
 const observer=new MutationObserver(()=>{if(!input.isConnected){dialog.remove();observer.disconnect()}});
 observer.observe(document.getElementById('view')||document.body,{childList:true,subtree:true});
}
function scan(){document.querySelectorAll('.folder-emoji-options').forEach(enhance)}
const observer=new MutationObserver(scan);
function start(){scan();observer.observe(document.body,{childList:true,subtree:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
