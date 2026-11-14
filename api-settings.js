/* Curated by Hide: API Settings UI. Secrets remain in page memory only. */
(()=>{
'use strict';
let activeKey='',activeProvider='openai';
const style=document.createElement('style');
style.textContent=`.cbh-api-overlay{position:fixed;inset:0;background:#15203c99;z-index:100010;display:flex;align-items:center;justify-content:center;padding:18px}.cbh-api-panel{background:#fff;color:#293142;border-radius:16px;width:min(480px,100%);max-height:90dvh;overflow:auto;padding:22px;box-shadow:0 15px 50px #0003}.cbh-api-panel h2{margin:0 0 15px;font-size:20px}.cbh-api-panel label{display:block;font-weight:700;font-size:13px;margin:13px 0 6px}.cbh-api-panel input,.cbh-api-panel select{width:100%;border:1px solid #dfe3ed;border-radius:9px;padding:11px;background:white;color:#293142}.cbh-api-panel .cbh-api-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}.cbh-api-panel .cbh-api-help{font-size:12px;color:#667085;line-height:1.65;margin-top:12px}.cbh-api-panel .cbh-api-status{font-size:13px;margin-top:12px}.cbh-api-panel .cbh-api-reveal{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:400}.cbh-api-panel .cbh-api-reveal input{width:auto}`;
document.head.appendChild(style);
function open(){
 if(document.getElementById('cbhApiOverlay'))return;
 const overlay=document.createElement('div');overlay.id='cbhApiOverlay';overlay.className='cbh-api-overlay';
 overlay.innerHTML=`<section class="cbh-api-panel" role="dialog" aria-modal="true" aria-labelledby="cbhApiTitle"><h2 id="cbhApiTitle">API Settings</h2><form id="cbhApiForm"><label for="cbhApiProvider">API 제공 서비스</label><select id="cbhApiProvider"><option value="openai">OpenAI</option><option value="other">기타 (향후 연결)</option></select><label for="cbhApiKey">API 키</label><input id="cbhApiKey" type="password" autocomplete="off" spellcheck="false" placeholder="API 키를 입력해 주세요" required><label class="cbh-api-reveal"><input id="cbhApiReveal" type="checkbox"> 입력값 표시</label><p class="cbh-api-help">보안을 위해 키는 현재 열린 페이지의 메모리에만 유지됩니다. 새로고침·탭 종료 시 초기화되며 백업이나 클라우드 동기화에 포함되지 않습니다. 이 화면은 키 등록 UI이며, 에이전트 실행 API 연결 기능은 아직 포함하지 않습니다.</p><div class="cbh-api-actions"><button type="submit" class="btn primary">적용</button><button type="button" class="btn" id="cbhApiClear">키 해제</button><button type="button" class="btn" id="cbhApiClose">닫기</button></div><p class="cbh-api-status" id="cbhApiStatus" role="status"></p></form></section>`;
 document.body.appendChild(overlay);
 const provider=overlay.querySelector('#cbhApiProvider'),key=overlay.querySelector('#cbhApiKey'),status=overlay.querySelector('#cbhApiStatus');
 provider.value=activeProvider;
 status.textContent=activeKey?'현재 페이지에 API 키가 적용되어 있습니다.':'적용된 API 키가 없습니다.';
 const close=()=>{key.value='';overlay.remove()};
 overlay.querySelector('#cbhApiClose').onclick=close;
 overlay.addEventListener('click',e=>{if(e.target===overlay)close()});
 overlay.querySelector('#cbhApiReveal').onchange=e=>{key.type=e.target.checked?'text':'password'};
 overlay.querySelector('#cbhApiClear').onclick=()=>{activeKey='';key.value='';status.textContent='API 키를 해제했습니다.';updateButton()};
 overlay.querySelector('#cbhApiForm').onsubmit=e=>{e.preventDefault();const value=key.value.trim();if(!value){status.textContent='API 키를 입력해 주세요.';return}activeKey=value;activeProvider=provider.value;key.value='';status.textContent='현재 페이지에 API 키를 적용했습니다. 실제 에이전트 API 호출은 아직 연결되지 않았습니다.';updateButton()};
 const onKey=e=>{if(e.key==='Escape'){close();document.removeEventListener('keydown',onKey)}};document.addEventListener('keydown',onKey);
 }
function updateButton(){const btn=document.getElementById('cbhApiSettingsBtn');if(btn){btn.textContent=activeKey?'API Settings ✓':'API Settings';btn.title=activeKey?'현재 페이지에 API 키 적용됨':'API 키 설정'}}
function mount(){const font=document.getElementById('fontSettingsBtn');if(!font||document.getElementById('cbhApiSettingsBtn'))return;const btn=document.createElement('button');btn.type='button';btn.id='cbhApiSettingsBtn';btn.className='btn';btn.textContent='API Settings';btn.onclick=open;font.insertAdjacentElement('afterend',btn);updateButton()}
mount();const observer=new MutationObserver(mount);observer.observe(document.body,{childList:true,subtree:true});
})();
