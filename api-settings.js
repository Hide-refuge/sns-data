/* Curated by Hide — protected AI API settings (Google ID token + Cloudflare Worker). */
(()=>{
'use strict';
const WORKER_URL='https://curated-hide-ai-proxy.hide-refuge.workers.dev';
const CLIENT_ID=window.SCRAP_GOOGLE_CONFIG?.clientId||'';
let idToken='',provider='claude',lastResponse='';
const sessionKeys={claude:'',openai:''};
const css=document.createElement('style');css.textContent=`
.cbh-api-overlay{position:fixed;inset:0;background:#15203caa;z-index:100010;display:flex;align-items:center;justify-content:center;padding:14px}
.cbh-api-panel{background:#fff;color:#293142;border-radius:16px;width:min(560px,100%);max-height:92dvh;overflow:auto;padding:22px;box-shadow:0 16px 50px #0003}
.cbh-api-panel h2{margin:0 0 14px;font-size:20px}.cbh-api-panel label{display:block;font-weight:700;font-size:13px;margin:12px 0 6px}
.cbh-api-panel select,.cbh-api-panel textarea,.cbh-api-panel input[type=password]{width:100%;border:1px solid #dfe3ed;border-radius:9px;padding:10px;background:#fff;color:#293142}
.cbh-api-panel textarea{min-height:90px;resize:vertical}.cbh-api-actions{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.cbh-api-panel .cbh-api-help{font-size:12px;color:#667085;line-height:1.6}.cbh-api-status{font-size:13px;white-space:pre-wrap}
.cbh-api-output{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fc;border:1px solid #e4e7ef;border-radius:10px;padding:12px;max-height:240px;overflow:auto;font-size:13px}
`;document.head.append(css);
function waitGoogle(){return new Promise((resolve,reject)=>{if(window.google?.accounts?.id)return resolve();const old=document.querySelector('script[data-cbh-gis]');if(old){old.addEventListener('load',resolve,{once:true});old.addEventListener('error',reject,{once:true});return}const s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.dataset.cbhGis='1';s.onload=resolve;s.onerror=reject;document.head.append(s)})}
async function request(path,data={}){
 if(!idToken)throw Error('먼저 Google 관리자 인증을 진행해 주세요.');
 const response=await fetch(WORKER_URL.replace(/\/$/,'')+path,{method:'POST',headers:{'content-type':'application/json','authorization':'Bearer '+idToken},body:JSON.stringify(data),signal:AbortSignal.timeout(30000)});
 const result=await response.json().catch(()=>({error:'서버 응답을 해석할 수 없습니다.'}));
 if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
 return result;
}
function open(){
 if(document.getElementById('cbhApiOverlay'))return;
 const overlay=document.createElement('div');overlay.id='cbhApiOverlay';overlay.className='cbh-api-overlay';
 overlay.innerHTML=`<section class="cbh-api-panel" role="dialog" aria-modal="true" aria-labelledby="cbhApiTitle"><h2 id="cbhApiTitle">API Settings</h2>
 <p class="cbh-api-help">Claude와 OpenAI 모두 API 키를 직접 입력해야 합니다. Google 관리자 인증은 계속 필요합니다.</p>
 <div id="cbhGoogleSignIn"></div><p id="cbhApiStatus" class="cbh-api-status" role="status">${idToken?'관리자 인증 정보가 있습니다. 연결 상태를 확인해 주세요.':'Google 관리자 인증이 필요합니다.'}</p>
 <label for="cbhApiProvider">AI 서비스</label><select id="cbhApiProvider"><option value="claude">Claude (Anthropic)</option><option value="openai">OpenAI</option></select>
 <label for="cbhApiKey">선택한 서비스의 API 키 (필수)</label><input id="cbhApiKey" type="password" autocomplete="off" spellcheck="false" placeholder="API 키를 입력해 주세요">
 <div class="cbh-api-actions"><button class="btn primary" id="cbhApiSaveKey" type="button">키 적용</button><button class="btn" id="cbhApiClearKey" type="button">입력 키 해제</button></div>
 <p class="cbh-api-help" id="cbhApiKeyInfo">키는 현재 탭의 메모리에만 보관되며 새로고침하면 사라집니다. GitHub·Google Drive에 저장되지 않습니다.</p>
 <div class="cbh-api-actions"><button class="btn" id="cbhApiStatusBtn" type="button">서버 연결 확인</button><button class="btn" id="cbhApiTest" type="button">선택한 API 연결 테스트</button></div>
 <label for="cbhApiPrompt">AI 요청 (테스트용)</label><textarea id="cbhApiPrompt" maxlength="4000" placeholder="예: 이 문장을 한 문장으로 요약해 주세요."></textarea>
 <div class="cbh-api-actions"><button class="btn primary" id="cbhApiRun" type="button">AI 요청 실행</button><button class="btn" id="cbhApiLogout" type="button">관리자 인증 해제</button><button class="btn" id="cbhApiClose" type="button">닫기</button></div>
 <div id="cbhApiOutput" class="cbh-api-output" aria-live="polite">${lastResponse?'이전 응답은 팝업을 다시 열면 표시되지 않습니다.':'응답 대기 중'}</div>
 <p class="cbh-api-help">연결 테스트와 AI 요청은 실제 API 사용량으로 청구될 수 있습니다. 입력한 키는 관리자 인증 후 HTTPS로 Worker에 전송됩니다.</p></section>`;
 document.body.append(overlay);
 const $=s=>overlay.querySelector(s),status=$('#cbhApiStatus'),output=$('#cbhApiOutput');
 $('#cbhApiProvider').value=provider;
 const keyInput=$('#cbhApiKey'),keyInfo=$('#cbhApiKeyInfo');
 const updateKeyInfo=()=>{keyInfo.textContent=sessionKeys[provider]?'이 서비스의 임시 API 키가 적용되어 있습니다. (새로고침 시 초기화)':'API 키 미입력 — 테스트 및 요청 실행 불가'};
 updateKeyInfo();
 $('#cbhApiProvider').onchange=e=>{provider=e.target.value;keyInput.value='';updateKeyInfo()};
 $('#cbhApiSaveKey').onclick=()=>{const key=keyInput.value.trim();if(!key){status.textContent='적용할 API 키를 입력해 주세요.';return}sessionKeys[provider]=key;keyInput.value='';updateKeyInfo();status.textContent=provider+' 임시 키가 적용되었습니다. 연결 테스트를 진행해 주세요.'};
 $('#cbhApiClearKey').onclick=()=>{sessionKeys[provider]='';keyInput.value='';updateKeyInfo();status.textContent='임시 키를 해제했습니다. 다시 입력해야 API를 사용할 수 있습니다.'};
 const close=()=>overlay.remove();$('#cbhApiClose').onclick=close;overlay.addEventListener('click',e=>{if(e.target===overlay)close()});
 $('#cbhApiLogout').onclick=()=>{idToken='';window.google?.accounts?.id?.disableAutoSelect();status.textContent='관리자 인증 정보를 해제했습니다.'};
 async function run(path){if(path!=='/api/status'&&!sessionKeys[provider]){status.textContent='선택한 서비스의 API 키를 먼저 입력하고 적용해 주세요.';return}const buttons=[...overlay.querySelectorAll('button')];buttons.forEach(b=>b.disabled=true);status.textContent='서버에 요청하는 중…';try{const data=await request(path,{provider,prompt:$('#cbhApiPrompt').value,...(path!=='/api/status'?{apiKey:sessionKeys[provider]}:{})});status.textContent=path==='/api/status'?'서버 연결됨 · API 키 직접 입력 전용 모드':`${provider} API 요청 성공`;if(data.text){lastResponse=data.text;output.textContent=data.text}else if(path==='/api/test'){output.textContent='API 인증 및 테스트 요청 성공 (텍스트 응답 없음)'}}catch(err){status.textContent='오류: '+(err.name==='TimeoutError'?'서버 응답 시간이 초과되었습니다.':err.message)}finally{buttons.forEach(b=>b.disabled=false)}}
 $('#cbhApiStatusBtn').onclick=()=>run('/api/status');$('#cbhApiTest').onclick=()=>run('/api/test');$('#cbhApiRun').onclick=()=>run('/api/run');
 if(!CLIENT_ID){status.textContent='sync-config.js에 Google Client ID가 없습니다.';return}
 waitGoogle().then(()=>{
  if(!overlay.isConnected)return;
  window.google.accounts.id.initialize({client_id:CLIENT_ID,callback:({credential})=>{idToken=credential||'';status.textContent=idToken?'Google 인증 정보 수신. 서버 연결 확인을 눌러 관리자 권한을 검증해 주세요.':'Google 인증에 실패했습니다.';}});
  window.google.accounts.id.renderButton($('#cbhGoogleSignIn'),{theme:'outline',size:'large',text:'signin_with',width:250});
 }).catch(()=>{status.textContent='Google 로그인 버튼을 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.'});
}
function mount(){const font=document.getElementById('fontSettingsBtn');if(!font||document.getElementById('cbhApiSettingsBtn'))return;const btn=document.createElement('button');btn.type='button';btn.id='cbhApiSettingsBtn';btn.className='btn';btn.textContent='API Settings';btn.onclick=open;font.insertAdjacentElement('afterend',btn)}
mount();new MutationObserver(mount).observe(document.body,{childList:true,subtree:true});
})();
