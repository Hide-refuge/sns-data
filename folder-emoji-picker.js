/* Curated by Hide — Folder emoji selector v3. Does not modify stored folder data. */
(()=>{
'use strict';
const URL='https://cdn.jsdelivr.net/npm/emoji-picker-element@1.28.1/+esm';
let loading=null;
const style=document.createElement('style');
style.textContent=`
.folder-emoji-options.cbh-old-emojis{display:none!important}
.cbh-emoji-ui{margin:8px 0 12px;min-width:0}
.cbh-emoji-button{display:flex;align-items:center;gap:8px;width:100%;justify-content:center;white-space:normal;text-align:center}
.cbh-emoji-selected{font-size:27px}
.cbh-emoji-panel{margin-top:10px;border:1px solid #dfe3ed;border-radius:12px;padding:8px;background:#fff;min-width:0}
.cbh-emoji-panel[hidden]{display:none!important}
.cbh-emoji-panel emoji-picker{display:block;width:100%;height:420px;max-height:60vh;--emoji-size:1.45rem;--num-columns:7}
.cbh-emoji-fallback{display:flex;flex-wrap:wrap;gap:5px}
.cbh-emoji-fallback button{min-width:40px;min-height:40px;font-size:23px}
`;
document.head.appendChild(style);
function enhance(options){
 if(options.dataset.cbhV3)return;
 const field=options.closest('.field');
 const input=field?.querySelector('input[name="icon"]');
 if(!input)return;
 options.dataset.cbhV3='1';
 options.classList.add('cbh-old-emojis');
 options.style.setProperty('display','none','important');
 const ui=document.createElement('div');ui.className='cbh-emoji-ui';
 const button=document.createElement('button');button.type='button';button.className='btn cbh-emoji-button';
 const selected=document.createElement('span');selected.className='cbh-emoji-selected';selected.textContent=input.value||'📁';
 const label=document.createElement('span');label.textContent='전체 이모지 검색 · 카테고리 선택';
 button.append(selected,label);
 const panel=document.createElement('div');panel.className='cbh-emoji-panel';panel.hidden=true;
 ui.append(button,panel);options.before(ui);
 const select=(emoji)=>{
  input.value=emoji;selected.textContent=emoji;
  const preview=input.closest('form')?.querySelector('[data-preview-icon]');if(preview)preview.textContent=emoji;
  options.querySelectorAll('[data-emoji]').forEach(x=>x.classList.toggle('selected',x.dataset.emoji===emoji));
  panel.hidden=true;button.setAttribute('aria-expanded','false');
 };
 button.setAttribute('aria-expanded','false');
 button.addEventListener('click',async()=>{
  panel.hidden=!panel.hidden;
  button.setAttribute('aria-expanded',String(!panel.hidden));
  if(panel.hidden||panel.dataset.ready)return;
  panel.textContent='이모지 검색 목록을 불러오는 중…';
  try{
   loading ||= import(URL).catch(err=>{loading=null;throw err});
   await loading;
   if(!panel.isConnected)return;
   const picker=document.createElement('emoji-picker');picker.setAttribute('locale','ko');
   picker.addEventListener('emoji-click',e=>{if(e.detail?.unicode)select(e.detail.unicode)});
   panel.replaceChildren(picker);panel.dataset.ready='1';
  }catch(err){
   console.error('Emoji library unavailable:',err);
   const notice=document.createElement('p');notice.className='hint';notice.textContent='전체 이모지 라이브러리를 불러오지 못했습니다. 네트워크 연결을 확인해 주세요. 아래 기본 아이콘을 선택할 수 있습니다.';
   const fallback=document.createElement('div');fallback.className='cbh-emoji-fallback';
   options.querySelectorAll('[data-emoji]').forEach(old=>{
    const b=document.createElement('button');b.type='button';b.className='btn';b.textContent=old.dataset.emoji;
    b.addEventListener('click',()=>select(old.dataset.emoji));fallback.append(b);
   });
   panel.replaceChildren(notice,fallback);panel.dataset.ready='fallback';
  }
 });
}
function scan(){document.querySelectorAll('.folder-emoji-options').forEach(enhance)}
let queued=false;
const observer=new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;scan()})});
function start(){scan();observer.observe(document.body,{childList:true,subtree:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
