/* Curated by Hide: Google Drive appDataFolder sync. Local IndexedDB remains untouched. */
(()=>{
'use strict';
const cfg=window.SCRAP_GOOGLE_CONFIG||{};
const FILE='curated-by-hide-v1.json';
const API='https://www.googleapis.com/drive/v3/files';
const $=id=>document.getElementById(id);
const msg=s=>{if($('syncStatus')){$('syncStatus').style.whiteSpace='pre-line';$('syncStatus').textContent=s}};
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
// CBH_THREE_WAY_MERGE_V1: 로컬 편집 시작 전의 공통 조상 사본
let baseSnapshot=null;
function syncState(){
 const el=$('cbhLocalSyncState');if(!el)return;
 el.innerHTML=dirty?'이 기기에 Google Drive 미동기화 변경 사항이 있습니다. <br class="mbr">지금 동기화를 눌러 업로드하세요.':'Google Drive 미동기화 변경 사항 없음';
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
 try{await cacheWrite({snapshot:clone(snapshot),dirty,baseRevision,baseSnapshot:baseSnapshot?clone(baseSnapshot):null})}
 catch(e){msg('로컬 저장 실패: '+errorText(e));throw e}
}
async function loadLocalState(){
 const saved=await cacheRead();
 if(saved&&saved.snapshot){snapshot=validate(saved.snapshot);dirty=Boolean(saved.dirty);baseRevision=saved.baseRevision??null;baseSnapshot=saved.baseSnapshot?validate(saved.baseSnapshot):null;localReady=true;return true}
 if(saved){snapshot=validate(saved);dirty=false;baseRevision=null;baseSnapshot=null;localReady=true;return true}
 return false;
}
async function localEdit(fn){
 if(!localReady)await loadLocalState();
 // 새 미리보기 주소처럼 Drive 캐시가 없는 경우에도 첫 로컬 저장을 허용합니다.
 // 원격 버전은 아직 알 수 없으므로 null로 유지하고, 나중에 수동 동기화 시 충돌을 검사합니다.
 if(!localReady){
  snapshot={version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
  localReady=true;
  baseRevision=null;
 }
 const before=clone(snapshot),oldDirty=dirty,oldBase=baseRevision,oldBaseSnapshot=baseSnapshot?clone(baseSnapshot):null;
 if(!dirty){baseRevision=revision;baseSnapshot=clone(snapshot);}
 fn(snapshot);dirty=true;
 try{await rememberSnapshot();syncState();info()}
 catch(e){snapshot=before;dirty=oldDirty;baseRevision=oldBase;baseSnapshot=oldBaseSnapshot;syncState();throw e}
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
 snapshot=next;baseRevision=revision;baseSnapshot=null;localReady=true;loaded=true;
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
// Three-way merge: only changes relative to the saved common ancestor are applied.
function mergeThreeWay(base,local,remote){
 const merged=clone(remote),conflicts=[],stats={added:0,updated:0,deleted:0};
 const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 for(const store of ['folders','posts']){
  const a=new Map(base[store].map(x=>[x.id,x]));
  const l=new Map(local[store].map(x=>[x.id,x]));
  const r=new Map(remote[store].map(x=>[x.id,x]));
  for(const id of new Set([...a.keys(),...l.keys()])){
   const before=a.get(id),after=l.get(id),current=r.get(id);
   if(same(before,after))continue; // no local change
   if(same(before,current)){
    if(after===undefined){r.delete(id);stats.deleted++}
    else {r.set(id,clone(after));if(before===undefined)stats.added++;else stats.updated++}
   }else if(!same(after,current)){
    conflicts.push(store+' / '+id); // same item changed differently, or delete vs edit
   }
  }
  merged[store]=[...r.values()];
 }
 const bf=base.fontSettings,lf=local.fontSettings,rf=remote.fontSettings;
 if(!same(bf,lf)){
  if(same(bf,rf))merged.fontSettings=clone(lf);
  else if(!same(lf,rf))conflicts.push('fontSettings');
 }
 return {merged,conflicts,stats};
}
// CBH_CONFLICT_MODAL_V1: conflicts are resolved per record, never by overwriting the full local snapshot.
function chooseConflicts(conflicts,base,local,remote){
 return new Promise(resolve=>{
  const old=document.getElementById('cbhConflictModal');
  if(old){resolve(null);return}
  const shade=document.createElement('div');shade.id='cbhConflictModal';
  shade.style.cssText='position:fixed;inset:0;z-index:2147483647;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;padding:16px';
  const panel=document.createElement('section');panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','데이터 충돌 해결');
  panel.style.cssText='background:#fff;color:#17212b;border-radius:14px;padding:18px;width:min(620px,100%);max-height:85vh;overflow:auto;box-shadow:0 12px 40px #0005;font:14px/1.5 system-ui,sans-serif';
  const title=document.createElement('h2');title.textContent='데이터 충돌 해결';title.style.cssText='font-size:20px;margin:0 0 8px';panel.append(title);
  const help=document.createElement('p');help.textContent='각 항목마다 유지할 변경을 선택하세요. 미선택 상태에서는 업로드할 수 없습니다. 취소하면 로컬 변경은 그대로 유지됩니다.';panel.append(help);
  const picks=new Map(), controls=[];
  const mapOf=(data,store)=>new Map(data[store].map(x=>[x.id,x]));
  const pretty=(record,store)=>{
   if(record===undefined)return '삭제됨';
   const label=record.name||record.title||record.id||'항목';
   return String(label).slice(0,120);
  };
  const entries=conflicts.map((key,i)=>{
   if(key==='fontSettings')return {key,store:null,id:null,localValue:local.fontSettings,remoteValue:remote.fontSettings,baseValue:base.fontSettings};
   const sep=key.indexOf(' / ');if(sep<0)throw Error('알 수 없는 충돌 유형');
   const store=key.slice(0,sep),id=key.slice(sep+3);
   if(!['folders','posts'].includes(store))throw Error('알 수 없는 충돌 저장소');
   return {key,store,id,localValue:mapOf(local,store).get(id),remoteValue:mapOf(remote,store).get(id),baseValue:mapOf(base,store).get(id)};
  });
  for(const [i,item] of entries.entries()){
   const section=document.createElement('div');section.style.cssText='border:1px solid #cbd5e1;border-radius:10px;padding:12px;margin:12px 0';
   const heading=document.createElement('strong');heading.textContent=(i+1)+'. '+(item.store==='folders'?'폴더':item.store==='posts'?'스크랩':'폰트 설정')+' 충돌';section.append(heading);
   const baseLine=document.createElement('p');baseLine.style.cssText='font-size:12px;color:#475569;overflow-wrap:anywhere';
   baseLine.textContent='수정 전: '+(item.store?pretty(item.baseValue,item.store):'기존 폰트 설정');section.append(baseLine);
   const group=document.createElement('div');group.style.cssText='display:grid;gap:8px';
   const makeOption=(value,text)=>{
    const label=document.createElement('label');label.style.cssText='display:block;padding:10px;border:1px solid #cbd5e1;border-radius:8px;cursor:pointer;overflow-wrap:anywhere';
    const radio=document.createElement('input');radio.type='radio';radio.name='cbh_conflict_'+i;radio.value=value;radio.style.marginRight='8px';
    radio.onchange=()=>{picks.set(item.key,value);refresh()};label.append(radio,document.createTextNode(text));group.append(label);
   };
   const labelLocal=item.store?pretty(item.localValue,item.store):'이 기기의 폰트 설정';
   const labelRemote=item.store?pretty(item.remoteValue,item.store):'Google Drive 폰트 설정';
   makeOption('local','이 기기 변경 유지: '+labelLocal);
   makeOption('remote','Google Drive 변경 유지: '+labelRemote);
   section.append(group);
   if(item.store==='folders'&&(item.localValue===undefined||item.remoteValue===undefined)){
    const warning=document.createElement('p');warning.style.cssText='color:#9a3412;font-weight:600';warning.textContent='폴더 삭제를 선택하면 연결된 스크랩 표시나 분류에 영향이 있을 수 있습니다. 삭제 전에 관련 스크랩을 확인하세요.';section.append(warning);
   }
   if(item.store===null){const warning=document.createElement('p');warning.textContent='폰트 설정은 전체 설정 단위로 선택합니다. 개별 규칙 병합은 지원하지 않습니다.';section.append(warning)}
   panel.append(section);
  }
  const status=document.createElement('p');panel.append(status);
  const actions=document.createElement('div');actions.style.cssText='display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap';
  const cancel=document.createElement('button');cancel.type='button';cancel.textContent='나중에 결정';cancel.style.cssText='padding:10px 14px;border:1px solid #94a3b8;border-radius:8px;background:#fff;color:#17212b';
  const apply=document.createElement('button');apply.type='button';apply.textContent='선택 사항 확인';apply.style.cssText='padding:10px 14px;border:0;border-radius:8px;background:#174d85;color:white';
  actions.append(cancel,apply);panel.append(actions);shade.append(panel);document.body.append(shade);
  const previousFocus=document.activeElement;
  const finish=value=>{document.removeEventListener('keydown',onKey);shade.remove();try{previousFocus?.focus()}catch{}resolve(value)};
  const onKey=e=>{if(e.key==='Escape'){e.preventDefault();finish(null)}else if(e.key==='Tab'){
   const focusable=[...panel.querySelectorAll('input:not(:disabled),button:not(:disabled)')];if(!focusable.length)return;
   const first=focusable[0],last=focusable[focusable.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }};
  document.addEventListener('keydown',onKey);cancel.onclick=()=>finish(null);
  function refresh(){status.textContent='선택 완료: '+picks.size+' / '+entries.length;apply.disabled=picks.size!==entries.length;apply.style.opacity=apply.disabled?'.45':'1'}
  refresh();cancel.focus();
  apply.onclick=()=>{
   if(picks.size!==entries.length)return;
   const deletions=entries.filter(x=>picks.get(x.key)==='local'&&x.localValue===undefined||picks.get(x.key)==='remote'&&x.remoteValue===undefined);
   const summary=entries.map(x=>(x.store==='folders'?'폴더':x.store==='posts'?'스크랩':'폰트')+' · '+(picks.get(x.key)==='local'?'이 기기':'Google Drive')+' 유지').join('\n');
   if(deletions.length&&!confirm('삭제되는 충돌 항목 '+deletions.length+'개가 있습니다. 연결된 스크랩에 영향이 있을 수 있습니다. 계속하시겠습니까?'))return;
   if(!confirm('충돌 해결 최종 확인\n\n'+summary+'\n\n선택 사항을 병합 미리보기에 반영하시겠습니까?'))return;
   finish(Object.fromEntries(picks));
  };
 });
}

async function uploadPending(){
 if(!sync.active)throw Error('Google 로그인 후 동기화해 주세요.');
 if(!localReady)await loadLocalState();
 if(!dirty)return false;
 await locate();
 let next=clone(snapshot),operation='수동 동기화';
 if(String(revision??'')!==String(baseRevision??'')){
  if(!baseSnapshot){
   if(baseRevision!==null)throw Error('기준 사본이 없는 기존 미동기화 수정은 안전하게 자동 병합할 수 없습니다. 로컬 자료를 보존하고 동기화를 중단했습니다.');
   // 최초 추가 병합: 기존 항목 수정 및 삭제는 허용하지 않습니다.
   const remote=remoteId?validate(await request(API+'/'+encodeURIComponent(remoteId)+'?alt=media')):{version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
   const merged=clone(remote);let added=0;
   for(const store of ['folders','posts']){
    const m=new Map(remote[store].map(x=>[x.id,x]));
    for(const item of snapshot[store]){
     if(m.has(item.id)){
      if(JSON.stringify(m.get(item.id))!==JSON.stringify(item))throw Error('기존 항목과 다른 내용이 발견되어 최초 병합을 중단했습니다.');
     }else{merged[store].push(clone(item));added++}
    }
   }
   if(snapshot.fontSettings!=null){
    if(remote.fontSettings==null)merged.fontSettings=clone(snapshot.fontSettings);
    else if(JSON.stringify(snapshot.fontSettings)!==JSON.stringify(remote.fontSettings))throw Error('폰트 설정 충돌로 병합을 중단했습니다.');
   }
   if(!confirm('최초 추가 병합: 새 항목 '+added+'개 / 결과 폴더 '+merged.folders.length+'개, 스크랩 '+merged.posts.length+'개. 업로드하시겠습니까?'))return false;
   await upload(merged,'최초 추가 병합');dirty=false;baseRevision=revision;baseSnapshot=null;await rememberSnapshot();syncState();return true;
  }
  const remote=remoteId?validate(await request(API+'/'+encodeURIComponent(remoteId)+'?alt=media')):{version:1,folders:[],posts:[],fontSettings:null,modifiedAt:null};
  const result=mergeThreeWay(baseSnapshot,snapshot,remote);
  const conflictCount=result.conflicts.length;
  // CBH_CONFLICT_MODAL_V1: 각 충돌 항목을 로컬 또는 Drive 기준으로 선택합니다.
  if(result.conflicts.length){
   const decisions=await chooseConflicts(result.conflicts,baseSnapshot,snapshot,remote);
   if(!decisions){msg('충돌 해결 취소 · 로컬 변경 유지');return false}
   for(const key of result.conflicts){
    const selected=decisions[key];
    if(selected!=='local'&&selected!=='remote')throw Error('충돌 항목의 선택 값이 올바르지 않습니다.');
    if(key==='fontSettings'){
     result.merged.fontSettings=clone(selected==='local'?snapshot.fontSettings:remote.fontSettings);
     continue;
    }
    const sep=key.indexOf(' / '),store=key.slice(0,sep),id=key.slice(sep+3);
    if(!['folders','posts'].includes(store))throw Error('알 수 없는 충돌 유형');
    const source=selected==='local'?snapshot:remote;
    const record=source[store].find(x=>x.id===id);
    const list=result.merged[store],index=list.findIndex(x=>x.id===id);
    if(index>=0)list.splice(index,1);
    if(record!==undefined)list.push(clone(record));
   }
   result.conflicts.length=0;
  }
  const {added,updated,deleted}=result.stats;
  const ok=confirm('Google Drive 안전 병합 미리보기\n\n'
   +'Drive: 폴더 '+remote.folders.length+'개, 스크랩 '+remote.posts.length+'개\n'
   +'병합 후: 폴더 '+result.merged.folders.length+'개, 스크랩 '+result.merged.posts.length+'개\n'
   +'충돌 항목 선택: '+conflictCount+'건\n'+'충돌 없는 로컬 변경: 추가 '+added+' / 수정 '+updated+' / 삭제 '+deleted+'\n\n'
   +'다른 기기의 변경은 유지합니다. 업로드하시겠습니까?');
  if(!ok){msg('병합 취소 · 로컬 변경 유지');return false}
  next=result.merged;operation='항목별 안전 병합';
 }
 // upload() verifies the revision again immediately before upload.
 await upload(next,operation);
 dirty=false;baseRevision=revision;baseSnapshot=null;
 await rememberSnapshot();syncState();return true;
}
async function reload(){
 if(busy)return;busy=true;
 try{
  await work;
  if(dirty){const done=await enqueue(uploadPending);if(done)msg('Google Drive 업로드 완료 · '+new Date().toLocaleTimeString('ko-KR'))}
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
 }else{root.innerHTML='<div class="actions"><button class="btn primary" id="googleLogin">Google 계정으로 로그인</button></div><p class="hint">저장용 Google 계정으로 로그인하세요.<br>최초 로그인 시 Drive 권한을 승인해야 합니다.</p>';
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
 msg('Google Drive 연결 준비 완료\nGoogle 로그인 버튼을 눌러 주세요.');
}
function init(){
 if(typeof window.scrapRefresh!=='function'){setTimeout(init,100);return}
 draw();info();ensureSyncState();loadLocalState().then(()=>{syncState();window.scrapRefresh?.()}).catch(e=>msg('로컬 자료 읽기 실패: '+errorText(e)));
 const foot=document.querySelector('.footer');if(foot)foot.innerHTML='로그아웃 상태에서는 마지막 Drive 사본을 읽기 전용으로 표시합니다<br class="mbr">(사본이 없다면 기존 IndexedDB 사용). <br class="mbr">Google 로그인 상태에서는 Drive에 저장합니다. <br class="mbr">중요한 자료는 정기적으로 백업하세요.';
 const panel=$('syncPanel');if(panel){const paragraphs=panel.querySelectorAll('p.hint');for(const p of paragraphs){if(p.textContent.includes('Supabase 공식 Egress'))p.textContent='표시 용량은 저장 데이터 JSON 크기의 추정값입니다. Google Drive 실제 네트워크 전송량과는 다를 수 있습니다.';}}
 if(!cfg.clientId)return;
 const s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.onload=initGIS;s.onerror=()=>msg('Google 로그인 라이브러리 로드 실패');document.head.appendChild(s);
}
window.addEventListener('load',init);
})();
