/* Curated by Hide: Google Drive appDataFolder sync. Local IndexedDB remains untouched. */
(()=>{
'use strict';
const cfg=window.SCRAP_GOOGLE_CONFIG||{};
const FILE='curated-by-hide-v1.json';
const API='https://www.googleapis.com/drive/v3/files';
const $=id=>document.getElementById(id);
const msg=s=>{if($('syncStatus'))$('syncStatus').textContent=s};
const errorText=e=>e?.message||String(e);
const sync={active:false};window.scrapSync=sync;
let token='',tokenClient=null,remoteId=null,revision=null,loaded=false,busy=false;
// Only a logout preference is stored; Google access tokens are never persisted.
const LOGOUT_KEY='curated-drive-manual-logout-v1';
let silentAttempt=false;
const loggedOutHere=()=>{try{return sessionStorage.getItem(LOGOUT_KEY)==='1'}catch{return false}};
const setLoggedOutHere=value=>{try{if(value)sessionStorage.setItem(LOGOUT_KEY,'1');else sessionStorage.removeItem(LOGOUT_KEY)}catch{}};
let snapshot={version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
let work=Promise.resolve();
const clone=v=>JSON.parse(JSON.stringify(v));
const bytes=v=>new TextEncoder().encode(JSON.stringify(v)).byteLength;
const fmt=n=>n<1024?n+' B':n<1048576?(n/1024).toFixed(1)+' KB':(n/1048576).toFixed(2)+' MB';
const stamp=()=>new Date().toISOString();
function info(){
 if($('syncModeInfo'))$('syncModeInfo').textContent='Google Drive 앱 전용 저장소 · 수동 새로고침 · 저장 시 업로드';
 if($('syncUsageInfo'))$('syncUsageInfo').textContent='현재 데이터 크기(추정): '+fmt(bytes(snapshot));
}
sync.usageRefresh=info;
function enqueue(fn){const task=work.then(fn);work=task.catch(()=>{});return task}
async function request(url,options={}){
 if(!token)throw Error('Google 계정으로 로그인해 주세요.');
 const headers=new Headers(options.headers||{});headers.set('Authorization','Bearer '+token);
 const response=await fetch(url,{...options,headers});
 if(!response.ok){let body='';try{body=await response.text()}catch{}
 if(response.status===401){msg('Google 인증이 만료되었습니다. 다시 로그인해 주세요.');throw Error('Google 인증 만료: 다시 로그인해 주세요.')}
 if(response.status===403)throw Error('Google Drive 접근 거부: API 활성화와 drive.appdata 권한을 확인하세요. '+body.slice(0,200));
 throw Error('Drive HTTP '+response.status+': '+body.slice(0,300));}
 if(response.status===204)return null;
 const t=await response.text();return t?JSON.parse(t):null;
}
async function locate(){
 const q=encodeURIComponent("name='"+FILE+"' and trashed=false");
 const url=API+'?spaces=appDataFolder&q='+q+'&fields=nextPageToken,files(id,name,version,modifiedTime)&page_size=100';
 const result=await request(url);
 const found=(result.files||[]).sort((a,b)=>String(b.modifiedTime||'').localeCompare(String(a.modifiedTime||'')))[0];
 remoteId=found?.id||null;revision=found?.version||null;
}
function validate(data){
 if(!data||data.version!==1||!Array.isArray(data.folders)||!Array.isArray(data.posts))throw Error('Drive 저장 파일 형식이 올바르지 않습니다. 기존 데이터를 덮어쓰지 않았습니다.');
 if(data.folders.some(x=>!x||typeof x.id!=='string')||data.posts.some(x=>!x||typeof x.id!=='string'))throw Error('저장 데이터의 ID가 잘못되었습니다.');
 return {version:1,folders:data.folders,posts:data.posts,fontSettings:data.fontSettings??null,modifiedAt:data.modifiedAt??null};
}
async function download(){
 await locate();
 if(!remoteId){snapshot={version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};loaded=true;info();return}
 const result=await request(API+'/'+encodeURIComponent(remoteId)+'?alt=media');
 snapshot=validate(result);loaded=true;info();
}
async function checkRevision(){
 if(!remoteId){await locate();if(remoteId)throw Error('다른 기기에서 저장 파일이 생성되었습니다. 먼저 지금 동기화를 눌러 주세요.');return}
 const meta=await request(API+'/'+encodeURIComponent(remoteId)+'?fields=id,version');
 if(String(meta.version)!==String(revision))throw Error('다른 기기에서 데이터가 변경되었습니다. 현재 편집 내용이 덮어써지지 않도록 저장을 중단했습니다. 먼저 백업 후 지금 동기화를 눌러 주세요.');
}
async function upload(next){
 if(!loaded)throw Error('클라우드 데이터를 아직 불러오지 못했습니다.');
 await checkRevision();
 const data=validate({...next,modifiedAt:stamp()});
 if(bytes(data)>20*1024*1024)throw Error('Drive 데이터가 20MB를 초과했습니다. 이미지 분리 저장 방식이 필요합니다. 기존 Drive 데이터는 변경하지 않았습니다.');
 const boundary='scraphub_'+Math.random().toString(36).slice(2);
 const meta=remoteId?{}:{name:FILE,parents:['appDataFolder'],mimeType:'application/json'};
 const body='--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(meta)+'\r\n--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(data)+'\r\n--'+boundary+'--';
 const url='https://www.googleapis.com/upload/drive/v3/files'+(remoteId?'/'+encodeURIComponent(remoteId):'')+'?uploadType=multipart&fields=id,version';
 const result=await request(url,{method:remoteId?'PATCH':'POST',headers:{'Content-Type':'multipart/related; boundary='+boundary},body});
 remoteId=result.id;revision=result.version;snapshot=data;info();
}
sync.getAll=async store=>{if(!loaded)throw Error('Drive 데이터 로딩 중입니다.');if(!['folders','posts'].includes(store))throw Error('지원하지 않는 저장소');return clone(snapshot[store])};
sync.put=(store,record)=>enqueue(async()=>{
 if(!sync.active)throw Error('로그인이 필요합니다.');if(!['folders','posts'].includes(store)||!record?.id)throw Error('저장 항목이 잘못되었습니다.');
 const next=clone(snapshot),index=next[store].findIndex(x=>x.id===record.id);
 if(index<0)next[store].push(clone(record));else next[store][index]=clone(record);
 await upload(next);return record.id;
});
sync.del=(store,id)=>enqueue(async()=>{
 if(!sync.active)throw Error('로그인이 필요합니다.');if(!['folders','posts'].includes(store))throw Error('지원하지 않는 저장소');
 const next=clone(snapshot);next[store]=next[store].filter(x=>x.id!==id);await upload(next);
});
sync.fontUser=async()=>sync.active?'google-drive-account':null;
sync.fontGet=async()=>{if(!sync.active)throw Error('로그인이 필요합니다.');return clone(snapshot.fontSettings)};
sync.fontPut=value=>enqueue(async()=>{if(!sync.active)throw Error('로그인이 필요합니다.');await upload({...clone(snapshot),fontSettings:clone(value)})});
async function reload(){
 if(busy)return;busy=true;
 try{await work;await download();await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();msg('Google Drive 동기화 완료 · '+new Date().toLocaleTimeString('ko-KR'))}
 catch(e){msg('동기화 실패: '+errorText(e));alert('Google Drive 동기화 실패: '+errorText(e))}
 finally{busy=false}
}
function localAll(store){return new Promise((resolve,reject)=>{
 const r=indexedDB.open('personal-scrap-hub-v1',1);r.onerror=()=>reject(r.error);r.onsuccess=()=>{
 const d=r.result,tx=d.transaction(store,'readonly'),q=tx.objectStore(store).getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);tx.oncomplete=()=>d.close();};
})}
async function migrateLocal(){
 if(!sync.active)return;
 const localFolders=await localAll('folders'),localPosts=await localAll('posts');
 if(!localFolders.length&&!localPosts.length){alert('이 기기의 IndexedDB에 이전할 자료가 없습니다. 기존 Supabase 자료는 별도로 Backup_Export가 필요합니다.');return}
 if(!confirm(`로컬 폴더 ${localFolders.length}개, 스크랩 ${localPosts.length}개를 Drive에 추가합니다. 같은 ID는 기존 Drive 자료를 유지합니다. 진행하시겠습니까?`))return;
 try{await enqueue(async()=>{
 const next=clone(snapshot);
 for(const store of ['folders','posts'])for(const record of store==='folders'?localFolders:localPosts){if(!next[store].some(x=>x.id===record.id))next[store].push(record)}
 await upload(next);
 });await window.scrapRefresh?.();alert('로컬 자료 이전 완료. 원본 IndexedDB는 유지됩니다.')}
 catch(e){alert('이전 실패: '+errorText(e))}
}
function parseMigrationFile(raw){
 if(!raw||raw.format!=='curated-by-hide-drive-migration'||raw.version!==1||!raw.tables)throw Error('Curated by Hide 통합 백업 JSON 형식이 아닙니다.');
 const folders=raw.tables.scrap_folders,posts=raw.tables.scrap_posts,fonts=raw.tables.scrap_font_settings;
 if(!Array.isArray(folders)||!Array.isArray(posts)||!Array.isArray(fonts)||fonts.length!==1)throw Error('백업에 필요한 폴더/스크랩/폰트 설정 테이블이 없습니다.');
 const unpack=(row)=>{const v=typeof row?.data==='string'?JSON.parse(row.data):row?.data;if(!v||typeof v!=='object'||Array.isArray(v))throw Error('백업 행의 data 항목이 잘못되었습니다.');return v};
 const folderData=folders.map(unpack),postData=posts.map(unpack),fontData=unpack(fonts[0]);
 const unique=(arr,name)=>{const ids=arr.map(x=>x.id);if(ids.some(x=>typeof x!=='string'||!x))throw Error(name+' ID가 잘못되었습니다.');if(new Set(ids).size!==ids.length)throw Error(name+' ID가 중복되었습니다.')};
 unique(folderData,'폴더');unique(postData,'스크랩');
 if(!Array.isArray(fontData.fonts)||!fontData.rules||typeof fontData.rules!=='object')throw Error('폰트 설정의 형식이 올바르지 않습니다.');
 return validate({version:1,folders:folderData,posts:postData,fontSettings:fontData,modifiedAt:null});
}
async function importMigration(event){
 const input=event.target,file=input.files?.[0];input.value='';if(!file||!sync.active)return;
 if(file.size>25*1024*1024){alert('선택한 JSON 파일이 25MB를 초과합니다.');return}
 try{
  const parsed=parseMigrationFile(JSON.parse(await file.text()));
  const summary=`복원 파일: 폴더 ${parsed.folders.length}개, 스크랩 ${parsed.posts.length}개, 폰트 ${parsed.fontSettings.fonts.length}개\n현재 Drive: 폴더 ${snapshot.folders.length}개, 스크랩 ${snapshot.posts.length}개\n\n복원하면 현재 Google Drive 저장 파일의 폴더·스크랩·폰트 설정을 이 백업으로 교체합니다. 기존 Supabase와 원본 JSON은 유지됩니다.\n\n계속하시겠습니까?`;
  if(!confirm(summary))return;
  if(!confirm('최종 확인: Google Drive에 이미 저장된 데이터는 이 백업으로 교체됩니다. 진행하시겠습니까?'))return;
  await enqueue(()=>upload(parsed));await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();
  msg('JSON 복원 완료 · 폴더 '+snapshot.folders.length+'개 · 스크랩 '+snapshot.posts.length+'개');
  alert('Google Drive 복원 완료. 폴더·스크랩·폰트 설정을 화면에서 확인해 주세요.');
 }catch(e){msg('JSON 복원 실패: '+errorText(e));alert('복원 실패: '+errorText(e))}
}
function draw(){const root=$('syncControls');if(!root)return;
 if(!cfg.clientId){root.innerHTML='<p class="warning">Google OAuth 클라이언트 ID 설정이 없습니다.</p>';return}
 if(sync.active){root.innerHTML='<div class="actions"><button class="btn" id="syncNow">지금 동기화</button><button class="btn" id="migrateLocal">이 기기 로컬 자료 복사</button><button class="btn" id="importMigration">통합 JSON 복원</button><input type="file" id="migrationFile" accept=".json,application/json" style="display:none"><button class="btn" id="syncLogout">Google 로그아웃</button></div><p class="hint">Drive의 앱 전용 숨김 저장소에 저장합니다. 다른 기기의 수정이 있다면 작업 전 지금 동기화를 누르세요. 기존 Supabase는 삭제하지 않았습니다.</p>';
 $('syncNow').onclick=reload;$('migrateLocal').onclick=migrateLocal;$('importMigration').onclick=()=>$('migrationFile').click();$('migrationFile').onchange=importMigration;$('syncLogout').onclick=()=>{setLoggedOutHere(true);token='';sync.active=false;loaded=false;remoteId=null;revision=null;draw();msg('로그아웃 상태 · IndexedDB 사용');window.scrapRefresh?.();window.scrapFontCloudRefresh?.()};
 }else{root.innerHTML='<div class="actions"><button class="btn primary" id="googleLogin">Google 계정으로 로그인</button></div><p class="hint">저장용 Google 계정으로 로그인하세요. 최초 로그인 시 Drive 권한을 승인해야 합니다.</p>';
 $('googleLogin').onclick=()=>{
 if(!tokenClient){alert('Google 로그인 모듈을 불러오는 중입니다. 잠시 후 다시 시도해 주세요.');return}
 silentAttempt=false;
 tokenClient.requestAccessToken({prompt:'consent'});
 };
 }
}
async function onToken(response){
 if(response.error){
  if(silentAttempt){silentAttempt=false;draw();msg('자동 연결을 완료하지 못했습니다. Google 로그인 버튼을 눌러 주세요.');return}
  msg('Google 로그인 오류: '+response.error);return
 }
 if(!response.access_token){msg('Google 인증 토큰을 받지 못했습니다. 다시 로그인해 주세요.');return}
 silentAttempt=false;setLoggedOutHere(false);
 token=response.access_token;sync.active=true;loaded=false;draw();msg('Google Drive 데이터를 불러오는 중…');
 try{await download();await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();msg('Google Drive 연결됨 · 폴더 '+snapshot.folders.length+'개 · 스크랩 '+snapshot.posts.length+'개')}
 catch(e){sync.active=false;token='';loaded=false;draw();msg('연결 실패: '+errorText(e));alert('Google Drive 연결 실패: '+errorText(e))}
}
function initGIS(){
 if(!window.google?.accounts?.oauth2){msg('Google 로그인 라이브러리를 불러오지 못했습니다.');return}
 tokenClient=google.accounts.oauth2.initTokenClient({
  client_id:cfg.clientId,
  scope:cfg.scope||'https://www.googleapis.com/auth/drive.appdata',
  callback:onToken,
  error_callback:()=>{
   if(silentAttempt){silentAttempt=false;draw();msg('자동 연결이 제한되었습니다. Google 로그인 버튼을 눌러 주세요.')}
   else msg('Google 로그인 창을 열지 못했습니다. 다시 시도해 주세요.');
  }
 });
 draw();
 if(loggedOutHere()){msg('이 탭에서 로그아웃했습니다. 다시 연결하려면 Google 로그인 버튼을 눌러 주세요.');return}
 // Browser may block a token request without user interaction. In that case, manual login remains available.
 silentAttempt=true;msg('Google Drive 자동 연결을 시도하는 중…');
 try{tokenClient.requestAccessToken({prompt:''})}
 catch(e){silentAttempt=false;draw();msg('자동 연결을 완료하지 못했습니다. Google 로그인 버튼을 눌러 주세요.')} 
}
function init(){
 if(typeof window.scrapRefresh!=='function'){setTimeout(init,100);return}
 draw();info();
 const foot=document.querySelector('.footer');if(foot)foot.textContent='로그아웃 상태에서는 이 기기의 IndexedDB를 사용합니다. Google 로그인 상태에서는 Google Drive 앱 전용 저장소에 저장합니다. 중요한 자료는 정기적으로 백업하세요.';
 const panel=$('syncPanel');if(panel){const paragraphs=panel.querySelectorAll('p.hint');for(const p of paragraphs){if(p.textContent.includes('Supabase 공식 Egress'))p.textContent='표시 용량은 저장 데이터 JSON 크기의 추정값입니다. Google Drive 실제 네트워크 전송량과는 다를 수 있습니다.';}}
 if(!cfg.clientId)return;
 const s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.onload=initGIS;s.onerror=()=>msg('Google 로그인 라이브러리 로드 실패');document.head.appendChild(s);
}
window.addEventListener('load',init);
})();
