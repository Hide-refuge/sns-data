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
// Session-only token cache: survives refresh in this tab, never localStorage.
const TOKEN_KEY='curated-drive-token-session-v2';
function saveSessionToken(value,expiresIn){
 try{const ttl=Math.min(Math.max(Number(expiresIn)||3000,60),3600);sessionStorage.setItem(TOKEN_KEY,JSON.stringify({token:value,expiresAt:Date.now()+ttl*1000-60000}));}catch{}
}
function readSessionToken(){
 try{const data=JSON.parse(sessionStorage.getItem(TOKEN_KEY)||'null');if(data?.token&&Date.now()<data.expiresAt)return data.token;}catch{}
 clearSessionToken();return '';
}
function clearSessionToken(){try{sessionStorage.removeItem(TOKEN_KEY)}catch{}}

const loggedOutHere=()=>{try{return sessionStorage.getItem(LOGOUT_KEY)==='1'}catch{return false}};
const setLoggedOutHere=value=>{try{if(value)sessionStorage.setItem(LOGOUT_KEY,'1');else sessionStorage.removeItem(LOGOUT_KEY)}catch{}};
let snapshot={version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
// CBH_LOCAL_FIRST_V1: 원격 기준 버전과 미전송 변경은 같은 IndexedDB 트랜잭션에 보존합니다.
let dirty=false, baseRevision=null, localReady=false;
function syncState(){
 const el=$('cbhLocalSyncState');if(!el)return;
 el.textContent=dirty?'이 기기에 Google Drive 미동기화 변경 사항이 있습니다. 지금 동기화를 눌러 업로드하세요.':'Google Drive 미동기화 변경 사항 없음';
}
function ensureSyncState(){
 let el=$('cbhLocalSyncState');if(el)return syncState();
 const parent=$('syncPanel');if(!parent)return;
 el=document.createElement('p');el.id='cbhLocalSyncState';el.className='hint';el.setAttribute('aria-live','polite');
 parent.insertBefore(el,$('syncControls')||null);syncState();
}


// Cloud snapshot cache uses a separate IndexedDB database: original local data stays untouched.
const CACHE_DB='curated-drive-offline-cache-v1';
function cacheDB(){return new Promise((resolve,reject)=>{
 const r=indexedDB.open(CACHE_DB,1);
 r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('snapshots'))r.result.createObjectStore('snapshots')};
 r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);
})}
async function cacheRead(){const d=await cacheDB();try{return await new Promise((resolve,reject)=>{
 const tx=d.transaction('snapshots','readonly');const r=tx.objectStore('snapshots').get('latest');
 r.onsuccess=()=>resolve(r.result||null);r.onerror=()=>reject(r.error);
})}finally{d.close()}}
async function cacheWrite(data){const d=await cacheDB();try{await new Promise((resolve,reject)=>{
 const tx=d.transaction('snapshots','readwrite');tx.objectStore('snapshots').put(clone(data),'latest');
 tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);
})}finally{d.close()}}
sync.offlineGetAll=async store=>{
 if(!['folders','posts'].includes(store))throw Error('지원하지 않는 저장소');
 const cached=await cacheRead();return cached?clone(validate(cached.snapshot||cached)[store]):null;
};
sync.hasOfflineCache=async()=>Boolean(await cacheRead());
async function rememberSnapshot(){
 try{await cacheWrite({snapshot:clone(snapshot),dirty,baseRevision})}
 catch(e){msg('로컬 저장 실패: '+errorText(e));throw e}
}
async function loadLocalState(){
 const saved=await cacheRead();
 if(saved&&saved.snapshot){snapshot=validate(saved.snapshot);dirty=Boolean(saved.dirty);baseRevision=saved.baseRevision??null;localReady=true;return true}
 if(saved){snapshot=validate(saved);dirty=false;baseRevision=null;localReady=true;return true}
 return false;
}
async function localEdit(fn){
 if(!localReady)await loadLocalState();
 if(!localReady)throw Error('로컬 데이터가 아직 준비되지 않았습니다. Google 로그인 후 데이터를 불러와 주세요.');
 const before=clone(snapshot),oldDirty=dirty,oldBase=baseRevision;
 if(!dirty)baseRevision=revision;
 fn(snapshot);dirty=true;
 try{await rememberSnapshot();syncState();info()}
 catch(e){snapshot=before;dirty=oldDirty;baseRevision=oldBase;syncState();throw e}
}


// CBH_DRIVE_TIMING_V1: 저장 단계별 진단 전용. 토큰과 데이터 내용은 기록하지 않습니다.
const timing=window.scrapDriveTiming={last:null,history:[]};
const clock=()=>performance.now();
const elapsed=(start)=>Math.round((clock()-start)*10)/10;
function timingDone(entry){
 timing.last=entry;timing.history.push(entry);if(timing.history.length>30)timing.history.shift();
 console.table(entry.steps.map(x=>({step:x.step,ms:x.ms})));
 console.info('[Drive 저장 진단] 총 '+entry.totalMs+'ms / '+entry.status+' / '+entry.operation);
 // CBH_DRIVE_TIMING_IPAD_V1: 개발자 도구 없이 측정 결과 표시
 showTimingOnPage(entry);

}
function showTimingOnPage(entry){
 try{
  let panel=document.getElementById('cbhDriveTimingPanel');
  if(!panel){
   panel=document.createElement('section');panel.id='cbhDriveTimingPanel';
   panel.style.cssText='margin:12px 0;padding:14px;border:1px solid #cbd5e1;border-radius:10px;background:var(--panel,#fff);color:inherit;overflow-wrap:anywhere';
   const parent=document.getElementById('syncPanel')||document.getElementById('syncControls')?.parentElement||document.querySelector('main');
   if(!parent)return;
   parent.appendChild(panel);
  }
  panel.replaceChildren();
  const title=document.createElement('strong');title.textContent='Google Drive 저장 속도 진단';panel.appendChild(title);
  const summary=document.createElement('p');summary.textContent=entry.operation+' · '+entry.status+' · 총 '+entry.totalMs+'ms ('+(entry.totalMs/1000).toFixed(2)+'초)';panel.appendChild(summary);
  const table=document.createElement('table');table.style.cssText='width:100%;font-size:13px;border-collapse:collapse';
  for(const step of entry.steps){const tr=document.createElement('tr'),a=document.createElement('td'),b=document.createElement('td');a.textContent=step.step;b.textContent=step.ms+'ms';b.style.textAlign='right';a.style.padding='4px';b.style.padding='4px';tr.append(a,b);table.appendChild(tr)}
  panel.appendChild(table);
  const button=document.createElement('button');button.type='button';button.className='btn';button.textContent='측정 결과 복사';button.style.marginTop='10px';
  button.onclick=async()=>{
   const report=['Google Drive 저장 속도 진단',entry.operation+' / '+entry.status,'전체: '+entry.totalMs+'ms',...entry.steps.map(x=>x.step+': '+x.ms+'ms')].join('\n');
   try{await navigator.clipboard.writeText(report);button.textContent='복사 완료'}
   catch(e){const input=document.createElement('textarea');input.value=report;input.readOnly=true;input.style.cssText='display:block;width:100%;min-height:120px;margin-top:8px';panel.appendChild(input);input.focus();input.select();button.textContent='아래 텍스트를 길게 눌러 복사해 주세요'}
  };
  panel.appendChild(button);
 }catch(e){console.warn('저장 속도 진단 패널 표시 실패',e)}
}
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
 // 미동기화 변경 사항은 서버 다운로드보다 우선하여 보호합니다.
 if(!localReady)await loadLocalState();
 if(dirty){
  await locate();loaded=true;info();syncState();
  msg('미동기화 로컬 변경 사항이 있어 Drive 데이터로 덮어쓰지 않았습니다.');return;
 }
 await locate();
 const next=remoteId?validate(await request(API+'/'+encodeURIComponent(remoteId)+'?alt=media')):{version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
 const previous=clone(snapshot),oldBase=baseRevision;
 snapshot=next;baseRevision=revision;localReady=true;loaded=true;
 try{await rememberSnapshot()}catch(e){snapshot=previous;baseRevision=oldBase;throw e}
 info();syncState();
}
async function checkRevision(){
 if(!remoteId){await locate();if(remoteId)throw Error('다른 기기에서 저장 파일이 생성되었습니다. 먼저 지금 동기화를 눌러 주세요.');return}
 const meta=await request(API+'/'+encodeURIComponent(remoteId)+'?fields=id,version');
 if(String(meta.version)!==String(revision))throw Error('다른 기기에서 데이터가 변경되었습니다. 현재 편집 내용이 덮어써지지 않도록 저장을 중단했습니다. 먼저 백업 후 지금 동기화를 눌러 주세요.');
}
async function upload(next,operation='저장'){
 const t0=clock(),entry={operation,status:'진행 중',steps:[],totalMs:0};
 const mark=(step,start)=>entry.steps.push({step,ms:elapsed(start)});
 try{
 if(!loaded)throw Error('클라우드 데이터를 아직 불러오지 못했습니다.');
 const tRevision=clock();await checkRevision();mark('저장 전 버전 확인',tRevision);
 const data=validate({...next,modifiedAt:stamp()});
 if(bytes(data)>20*1024*1024)throw Error('Drive 데이터가 20MB를 초과했습니다. 이미지 분리 저장 방식이 필요합니다. 기존 Drive 데이터는 변경하지 않았습니다.');
 const tEncode=clock();
 const boundary='scraphub_'+Math.random().toString(36).slice(2);
 const meta=remoteId?{}:{name:FILE,parents:['appDataFolder'],mimeType:'application/json'};
 const body='--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(meta)+'\r\n--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(data)+'\r\n--'+boundary+'--';
 const url='https://www.googleapis.com/upload/drive/v3/files'+(remoteId?'/'+encodeURIComponent(remoteId):'')+'?uploadType=multipart&fields=id,version';
 mark('JSON 직렬화 및 업로드 준비',tEncode);
 const tUpload=clock();const result=await request(url,{method:remoteId?'PATCH':'POST',headers:{'Content-Type':'multipart/related; boundary='+boundary},body});mark('Google Drive 업로드',tUpload);
 remoteId=result.id;
 // Fetch the authoritative Drive revision after each successful upload.
 const tAfter=clock();const current=await request(API+'/'+encodeURIComponent(remoteId)+'?fields=id,version');mark('업로드 후 버전 재조회',tAfter);
 if(!current?.version)throw Error('Drive 저장은 완료되었지만 최신 버전을 확인하지 못했습니다. 지금 동기화 후 다시 시도해 주세요.');
 revision=current.version;snapshot=data;info();const tCache=clock();await rememberSnapshot();mark('오프라인 사본 저장',tCache);
 entry.status='성공';
 }catch(e){entry.status='실패';throw e}finally{entry.totalMs=elapsed(t0);timingDone(entry)}
}
sync.getAll=async store=>{if(!loaded&&!localReady)throw Error('Drive 데이터 로딩 중입니다.');if(!['folders','posts'].includes(store))throw Error('지원하지 않는 저장소');return clone(snapshot[store])};
sync.put=(store,record)=>enqueue(async()=>{
 if(!['folders','posts'].includes(store)||!record?.id)throw Error('저장 항목이 잘못되었습니다.');
 await localEdit(data=>{const list=data[store],i=list.findIndex(x=>x.id===record.id);if(i<0)list.push(clone(record));else list[i]=clone(record)});
 return record.id;
});
sync.del=(store,id)=>enqueue(async()=>{
 if(!['folders','posts'].includes(store))throw Error('지원하지 않는 저장소');
 await localEdit(data=>{data[store]=data[store].filter(x=>x.id!==id)});
});
sync.fontUser=async()=>sync.active?'google-drive-account':null;
sync.fontGet=async()=>{if(!localReady)await loadLocalState();if(!localReady)throw Error('데이터 로딩 중입니다.');return clone(snapshot.fontSettings)};
sync.fontPut=value=>enqueue(async()=>{await localEdit(data=>{data.fontSettings=clone(value)})});
async function uploadPending(){
 if(!sync.active)throw Error('Google 로그인 후 동기화해 주세요.');
 if(!localReady)await loadLocalState();
 if(!dirty)return false;
 // 변경 시작 시점의 버전을 반드시 비교합니다. 기존 upload()도 현재 revision을 재검사합니다.
 await locate();
 if(String(revision??'')!==String(baseRevision??''))throw Error('다른 기기에서 Drive 데이터가 변경되었습니다. 로컬 자료는 보존했습니다. 자동 덮어쓰기를 중단합니다.');
 await upload(clone(snapshot),'수동 동기화');
 dirty=false;baseRevision=revision;
 // 업로드 성공 뒤 로컬 완료 표시 저장이 실패해도 다음 시도에서 덮어쓰지 않도록 알립니다.
 await rememberSnapshot();syncState();return true;
}
async function reload(){
 if(busy)return;busy=true;
 try{
  await work;
  if(dirty){await enqueue(uploadPending);msg('Google Drive 업로드 완료 · '+new Date().toLocaleTimeString('ko-KR'))}
  else{await download();msg('Google Drive 최신 데이터 확인 완료 · '+new Date().toLocaleTimeString('ko-KR'))}
  await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();syncState();
 }catch(e){msg('동기화 중단: '+errorText(e));alert('동기화 중단: '+errorText(e)+'\n로컬 변경 사항은 유지됩니다.')}
 finally{busy=false}
}
function localAll(store){return new Promise((resolve,reject)=>{
 const r=indexedDB.open('personal-scrap-hub-v1',1);r.onerror=()=>reject(r.error);r.onsuccess=()=>{
 const d=r.result,tx=d.transaction(store,'readonly'),q=tx.objectStore(store).getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);tx.oncomplete=()=>d.close();};
})}
async function migrateLocal(){
 if(!sync.active)return;
 if(dirty){alert('미동기화 변경 사항이 있습니다. 먼저 지금 동기화를 진행해 주세요.');return}
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
 if(dirty){alert('미동기화 변경 사항이 있습니다. 먼저 지금 동기화를 진행해 주세요.');return}
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
 $('syncNow').onclick=reload;$('migrateLocal').onclick=migrateLocal;$('importMigration').onclick=()=>$('migrationFile').click();$('migrationFile').onchange=importMigration;$('syncLogout').onclick=()=>{setLoggedOutHere(true);clearSessionToken();token='';sync.active=false;loaded=false;remoteId=null;revision=null;draw();syncState();msg('로그아웃 상태 · 마지막 Drive 사본 표시(있는 경우, 읽기 전용)');window.scrapRefresh?.();window.scrapFontCloudRefresh?.()};
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
 saveSessionToken(response.access_token,response.expires_in);
 token=response.access_token;sync.active=true;loaded=false;draw();msg('Google Drive 데이터를 불러오는 중…');
 try{await download();await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();msg('Google Drive 연결됨 · 폴더 '+snapshot.folders.length+'개 · 스크랩 '+snapshot.posts.length+'개')}
 catch(e){sync.active=false;token='';loaded=false;clearSessionToken();draw();msg('연결 실패: '+errorText(e));alert('Google Drive 연결 실패: '+errorText(e))}
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
 if(loggedOutHere()){clearSessionToken();msg('이 탭에서 로그아웃했습니다. 다시 연결하려면 Google 로그인 버튼을 눌러 주세요.');return}
 const restored=readSessionToken();
 if(restored){
  token=restored;sync.active=true;draw();msg('이 탭의 Google Drive 연결을 복원하는 중…');
  (async()=>{try{await download();await window.scrapRefresh?.();await window.scrapFontCloudRefresh?.();msg('Google Drive 연결 복원됨 · 폴더 '+snapshot.folders.length+'개 · 스크랩 '+snapshot.posts.length+'개')}
   catch(e){token='';sync.active=false;loaded=false;clearSessionToken();draw();msg('세션이 만료되었거나 연결이 실패했습니다. Google 로그인 버튼을 눌러 주세요.')}})();
  return;
 }
 // Safari may reject background token requests. Do not open an unwanted login popup.
 msg('Google Drive 연결 준비 완료 · Google 로그인 버튼을 눌러 주세요.');
}
function init(){
 if(typeof window.scrapRefresh!=='function'){setTimeout(init,100);return}
 draw();info();ensureSyncState();loadLocalState().then(()=>{syncState();window.scrapRefresh?.()}).catch(e=>msg('로컬 자료 읽기 실패: '+errorText(e)));
 const foot=document.querySelector('.footer');if(foot)foot.textContent='로그아웃 상태에서는 마지막 Drive 사본을 읽기 전용으로 표시합니다(사본이 없다면 기존 IndexedDB 사용). Google 로그인 상태에서는 Drive에 저장합니다. 중요한 자료는 정기적으로 백업하세요.';
 const panel=$('syncPanel');if(panel){const paragraphs=panel.querySelectorAll('p.hint');for(const p of paragraphs){if(p.textContent.includes('Supabase 공식 Egress'))p.textContent='표시 용량은 저장 데이터 JSON 크기의 추정값입니다. Google Drive 실제 네트워크 전송량과는 다를 수 있습니다.';}}
 if(!cfg.clientId)return;
 const s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.onload=initGIS;s.onerror=()=>msg('Google 로그인 라이브러리 로드 실패');document.head.appendChild(s);
}
window.addEventListener('load',init);
})();
