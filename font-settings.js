/* Font settings extension for SNS Scrap Hub. No existing scrap records are changed. */
(()=>{'use strict';
const KEY='scrap-font-settings-v1';
const defaults={fonts:[{id:'system',name:'기본 글꼴',family:'system-ui',weights:[400,500,600,700]},{id:'noto',name:'Noto Sans KR',family:'Noto Sans KR',css:'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap',weights:[400,500,600,700]},{id:'nanum',name:'Nanum Gothic',family:'Nanum Gothic',css:'https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap',weights:[400,700]}],rules:[]};
let state=loadLocal(),activeUser=null,fetching=false,selected=new Set(),scope='all',dialogOpen=false;
const fontVersions=new Map();
function loadLocal(){try{const v=JSON.parse(localStorage.getItem(KEY)||'null');return sanitize(v)}catch{return structuredClone(defaults)}}
function sanitize(v){if(!v||typeof v!=='object')return structuredClone(defaults);const fonts=[...defaults.fonts];for(const f of Array.isArray(v.fonts)?v.fonts:[]){if(f&&typeof f.id==='string'&&f.id.startsWith('custom-')&&(validCSS(f.css)||validFontPath(f.path)||(Array.isArray(f.files)&&f.files.length>=2))&&typeof f.name==='string'&&typeof f.family==='string')fonts.push({id:f.id,name:f.name.slice(0,80),family:f.family.slice(0,100),css:validCSS(f.css)?f.css:undefined,path:validFontPath(f.path)?f.path:undefined,files:Array.isArray(f.files)?f.files.filter(x=>x&&validFontPath(x.path)&&[100,200,300,400,500,600,700,800,900].includes(Number(x.weight))).slice(0,9).map(x=>({path:x.path,weight:Number(x.weight)})):undefined,weights:validWeights(f.weights)})}const rules=(Array.isArray(v.rules)?v.rules:[]).filter(r=>r&&['all','platform','folder','keyword','post'].includes(r.scope)&&typeof r.fontId==='string'&&typeof r.target==='string').map(r=>({scope:r.scope,target:r.target,fontId:r.fontId,weight:Number(r.weight)||400,updated:Number(r.updated)||0}));return {fonts,rules}}
function validWeights(w){const allowed=[100,200,300,400,500,600,700,800,900];return [...new Set((Array.isArray(w)?w:[400]).map(Number).filter(n=>allowed.includes(n)))].sort((a,b)=>a-b).slice(0,9)}
function validCSS(u){try{const x=new URL(u);return x.protocol==='https:'&&['fonts.googleapis.com','cdn.jsdelivr.net','cdnjs.cloudflare.com'].includes(x.hostname)&&x.href.length<1400}catch{return false}}
// Files must be uploaded separately to the GitHub Pages repository's fonts/ folder.
// Reject traversal, external URLs and unsafe characters; only local webfont files are accepted.
function validFontPath(path){return typeof path==='string'&&/^(?:(?:[A-Za-z0-9_-]+)\/)+[A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:woff2|woff|ttf|otf)$/i.test(path)&&path.length<=200&&!path.split('/').some(x=>x==='.'||x==='..')}
function fontFormat(path){return path.toLowerCase().endsWith('.woff2')?'woff2':path.toLowerCase().endsWith('.woff')?'woff':path.toLowerCase().endsWith('.ttf')?'truetype':'opentype'}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function font(id){return state.fonts.find(f=>f.id===id)||state.fonts[0]}
function fileURL(path,id){const url=new URL(path,document.baseURI);const version=fontVersions.get(id);if(version)url.searchParams.set('fontrev',version);return url.href}
function installFonts(){
 document.querySelectorAll('link[data-scrap-font],style[data-scrap-font]').forEach(n=>n.remove());
 for(const f of state.fonts){
  if(Array.isArray(f.files)&&f.files.length>=2){for(const file of f.files){if(!validFontPath(file.path))continue;const st=document.createElement('style');st.dataset.scrapFont=f.id;st.textContent=`@font-face{font-family:${JSON.stringify(f.family)};src:url(${JSON.stringify(fileURL(file.path,f.id))}) format('${fontFormat(file.path)}');font-style:normal;font-weight:${file.weight};font-display:swap}`;document.head.append(st)}}else if(f.path&&validFontPath(f.path)){
   const style=document.createElement('style');style.dataset.scrapFont=f.id;
   const family=JSON.stringify(f.family),url=JSON.stringify(fileURL(f.path,f.id)),format=fontFormat(f.path);
   // Each registered file is assigned its declared weight. Variable font files can cover a range.
   const weights=f.weights.length>1?`${f.weights[0]} ${f.weights[f.weights.length-1]}`:String(f.weights[0]);
   style.textContent=`@font-face{font-family:${family};src:url(${url}) format('${format}');font-style:normal;font-weight:${weights};font-display:swap}`;
   document.head.append(style);
  }else if(f.css&&validCSS(f.css)){
   const l=document.createElement('link');l.rel='stylesheet';l.href=f.css;l.dataset.scrapFont=f.id;document.head.append(l);
  }
 }
}
function normalizedPlatform(v){const s=String(v||'').trim().toLowerCase();return s==='x'||s==='twitter'?'twitter':s==='instagram'?'instagram':s}
// Each save has an update timestamp. The most recently saved applicable ancestor
// wins, even when an older, more specific setting exists.
// Stable ordering: newest save wins; on an equal timestamp, broader scopes win.
const scopeTiePriority={all:5,platform:4,folder:3,keyword:2,post:1};
function newestRule(candidates){return candidates.filter(Boolean).sort((a,b)=>(Number(b.updated)||0)-(Number(a.updated)||0)||(scopeTiePriority[b.scope]||0)-(scopeTiePriority[a.scope]||0))[0]||null}
function nextRuleRevision(){return Math.max(Date.now(),...state.rules.map(r=>(Number(r.updated)||0)+1))}
function pickRule(type,target){return state.rules.filter(r=>r.scope===type&&String(r.target)===String(target)).sort((a,b)=>b.updated-a.updated)[0]||null}
function folderChain(folderId,byFolder){const chain=[],visited=new Set();let id=String(folderId||'');while(id&&byFolder.has(id)&&!visited.has(id)){visited.add(id);const folder=byFolder.get(id);chain.push(folder);id=String(folder.parentId||folder.parentFolderId||folder.parent_id||'')}return chain}
function branchRules(platform,folderId,byFolder){const chain=folderChain(folderId,byFolder);const actualPlatform=normalizedPlatform(platform||chain.find(f=>normalizedPlatform(f.platform))?.platform);return [pickRule('all','*'),actualPlatform&&pickRule('platform',actualPlatform),...chain.map(f=>pickRule('folder',f.id))]}
function matchingKeywords(p){const keys=Array.isArray(p.keywords)?p.keywords:[];return state.rules.filter(r=>r.scope==='keyword'&&keys.some(k=>String(k).trim().toLocaleLowerCase()===String(r.target).trim().toLocaleLowerCase()))}
function ruleFor(p,byFolder){return newestRule([...branchRules(p.platform,p.folderId,byFolder),...matchingKeywords(p),pickRule('post',p.id)])}
const FONT_CHILDREN='h1,h2,h3,h4,h5,h6,p,span,strong,small,div,a,button,input,textarea,select,label,li,article,section';
function clearFont(el){if(!el)return;for(const n of [el,...el.querySelectorAll(FONT_CHILDREN)]){n.style.removeProperty('font-family');n.style.removeProperty('font-weight')}}
function setFont(el,r){if(!el||!r)return;const f=font(r.fontId),family=JSON.stringify(f.family)+',system-ui,sans-serif';const weight=String(f.weights.includes(Number(r.weight))?r.weight:(f.weights[0]||400));for(const n of [el,...el.querySelectorAll(FONT_CHILDREN)]){n.style.setProperty('font-family',family,'important');n.style.setProperty('font-weight',weight,'important')}}
function apply(){
 const posts=window.scrapFontData?.()||window.scrapFontPosts?.()||[];
 const byId=new Map(posts.map(p=>[String(p.id),p]));
 const folders=window.scrapFontFolders?.()||[];
 const byFolder=new Map(folders.map(f=>[String(f.id),f]));
 const route=window.scrapFontRoute?.()||{};
 const routeRule=newestRule(branchRules(route.platform,route.folder,byFolder));
 const root=document.documentElement,body=document.body,view=document.getElementById('view'),app=document.querySelector('main.app');
 for(const el of [root,body]){el.style.removeProperty('font-family');el.style.removeProperty('font-weight')}
 if(app)clearFont(app);else if(view)clearFont(view);
 const crumb=document.getElementById('crumb');if(crumb)clearFont(crumb);
 // The page itself inherits the selected platform or folder font.
 const pageRule=routeRule||pickRule('all','*');
 if(pageRule){setFont(root,pageRule);setFont(body,pageRule);if(app)setFont(app,pageRule);else if(view)setFont(view,pageRule);if(crumb)setFont(crumb,pageRule)}
 // Home: each platform card uses its own branch. Platform: each folder card
 // uses its own branch. A newer ancestor overrides older descendants.
 if(view)for(const el of view.querySelectorAll('[data-platform],[data-folder]')){
  const folderId=el.dataset.folder;
  const folder=folderId?byFolder.get(String(folderId)):null;
  const r=newestRule(branchRules(el.dataset.platform||folder?.platform||route.platform,folderId||route.folder,byFolder));
  if(r)setFont(el,r);
 }
 // Individual scrap cards are re-applied after page-level styling, so they
 // inherit the latest applicable platform/folder rule unless overridden later.
 for(const el of document.querySelectorAll('#view [data-font-post]')){
  const p=byId.get(String(el.dataset.fontPost));
  if(p){const r=ruleFor(p,byFolder);if(r)setFont(el,r)}
 }
}
function rerender(){installFonts();apply()}
async function reloadCloud(){if(!window.scrapSync?.active){if(activeUser){activeUser=null;state=loadLocal();rerender()}return}if(!window.scrapSync.fontGet||fetching)return;fetching=true;try{const user=await window.scrapSync.fontUser();if(!user)return;if(activeUser!==user){activeUser=user;state=structuredClone(defaults)}const remote=await window.scrapSync.fontGet();state=remote?sanitize(remote):structuredClone(defaults);rerender()}catch(e){console.warn('Font cloud sync:',e.message)}finally{fetching=false}}
async function save(){try{if(window.scrapSync?.active){if(!window.scrapSync.fontPut)throw Error('sync.js 파일을 새 버전으로 교체해 주세요.');await window.scrapSync.fontPut(state)}else localStorage.setItem(KEY,JSON.stringify(state));rerender();return true}catch(e){alert('폰트 설정 저장 실패: '+e.message);return false}}
function chooseFontHTML(prefix){return `<div class="field"><label>선택 폰트</label><select id="${prefix}Font">${state.fonts.map(f=>`<option value="${esc(f.id)}">${esc(f.name)}</option>`).join('')}</select></div><div class="field"><label>굵기</label><select id="${prefix}Weight"></select></div>`}
function updateWeight(prefix){const f=font(document.getElementById(prefix+'Font')?.value);const el=document.getElementById(prefix+'Weight');if(el)el.innerHTML=f.weights.map(w=>`<option value="${w}">${w}${w===400?' · Regular':w===700?' · Bold':''}</option>`).join('')}
function renderFolderOptions(){const folders=window.scrapFontFolders?.()||[];return folders.map(f=>`<option value="${esc(f.id)}">${esc(f.platform==='instagram'?'Instagram':'X')} / ${esc(f.name)}</option>`).join('')}
function open(){dialogOpen=true;selected.clear();const root=document.getElementById('modalRoot');if(!root)return;root.innerHTML=`<div class="overlay" id="overlay"><div class="dialog font-dialog" role="dialog" aria-modal="true" aria-label="폰트 설정"><div class="font-head"><h2>Font Settings</h2><button type="button" class="btn" data-close>닫기 ×</button></div><section class="font-section"><h3>1 · 범위별 폰트 설정</h3><div class="font-radio"><label><input type="radio" name="fontScope" value="all" checked> 전체 페이지</label><label><input type="radio" name="fontScope" value="platform"> 플랫폼</label><label><input type="radio" name="fontScope" value="folder"> 폴더</label><label><input type="radio" name="fontScope" value="keyword"> 키워드</label></div><div id="fontScopeExtra"></div><p class="hint" id="fontScopeInfo">선택 범위: 전체 페이지</p>${chooseFontHTML('range')}<div class="font-save"><button class="btn primary" id="fontRangeSave">설정 저장</button></div></section><hr><section class="font-section"><h3>2 · 개별 스크랩 설정</h3><div class="field"><label>스크랩 검색 (제목·키워드)</label><input id="fontPostSearch" type="search" placeholder="검색어 입력"></div>${chooseFontHTML('post')}<div class="font-result-head"><span id="fontSelectionCount">0개 선택</span><button type="button" class="btn" id="fontSelectVisible">검색 결과 전체 선택</button></div><div id="fontPostResults" class="font-post-results"></div><div class="font-save"><button class="btn primary" id="fontPostSave">선택 스크랩 저장</button></div></section><hr><section class="font-section"><h3>3 · GitHub 폰트 파일 등록</h3><div class="font-radio" id="fontRegisterMode"><label><input type="radio" name="fontRegMode" value="single" checked> 단일 폰트 등록</label><label><input type="radio" name="fontRegMode" value="multi"> 다중 폰트 등록</label></div><p class="hint">먼저 GitHub 저장소의 fonts 폴더에 WOFF2 등의 폰트 파일을 업로드하세요. 업로드 후 파일 경로를 아래에 등록합니다. 폰트 재배포·웹 사용 라이선스를 확인하세요. 기존에 등록된 폰트 설정은 유지됩니다.</p><div class="field"><label>표시 이름</label><input id="fontCustomName" maxlength="80" placeholder="예: 내 웹폰트"></div><div class="field"><label>폰트 식별 이름 (영문 권장)</label><input id="fontCustomFamily" maxlength="100" placeholder="예: My Font"></div><div id="fontSingleFields"><div class="field"><label>GitHub 폰트 파일 경로</label><input id="fontCustomPath" type="text" maxlength="200" placeholder="fonts/GriunXHangeul_Banguri-Rg.ttf"><div class="hint">예: fonts/GriunXHangeul_Banguri-Rg.ttf (GitHub 주소 전체 입력 불필요)</div></div><div class="field"><label>파일에서 지원하는 굵기 (쉼표 구분)</label><input id="fontCustomWeights" value="400" placeholder="예: 400 또는 400,700"></div></div><div id="fontMultiFields" hidden><details id="fontMultiCountDetails" class="font-count-accordion"><summary>등록할 폰트 수량 선택 · <span id="fontMultiCountLabel">2개</span></summary><div class="font-count-options" id="fontMultiCountOptions"></div></details><div id="fontMultiRows"></div><p class="hint">각 굵기에 해당하는 실제 폰트 파일 경로를 입력해 주세요. 최소 2개, 최대 9개입니다.</p></div><div class="font-save"><button class="btn primary" id="fontCustomSave">GitHub 폰트 등록</button></div><div id="fontCustomList" class="hint"></div></section><hr><section class="font-section"><h3>4 · 폰트 정보 수정</h3><p class="hint">등록한 사용자 폰트의 정보를 수정하면 실제 폰트 선택 목록과 화면 적용에 반영됩니다.</p><div class="field"><label>수정할 폰트 선택</label><details id="fontEditAccordion" class="font-count-accordion"><summary id="fontEditAccordionLabel">수정할 폰트를 선택하세요</summary><div id="fontEditAccordionOptions" class="font-edit-options"></div></details><select id="fontEditSelect" aria-label="수정할 폰트 선택" hidden><option value="">수정할 폰트를 선택하세요</option></select></div><div id="fontEditFields" hidden><div class="field"><label>표시 이름</label><input id="fontEditName" maxlength="80"></div><div class="field"><label>폰트 식별 이름</label><input id="fontEditFamily" maxlength="100"></div><div id="fontEditFileFields"></div><div class="font-save"><button type="button" class="btn primary" id="fontEditSave">변경 사항 저장 및 적용</button></div><p id="fontEditStatus" class="hint" role="status" aria-live="polite"></p></div></section><hr><section class="font-section"><h3>5 · 등록된 폰트 삭제</h3><p class="hint">직접 등록한 폰트만 삭제할 수 있습니다. 해당 폰트를 사용하는 설정도 함께 해제되며, GitHub에 업로드된 실제 폰트 파일은 삭제되지 않습니다.</p><div id="fontDeleteList" class="font-delete-list"></div></section></div></div>`;
for(const pre of ['range','post']){updateWeight(pre);document.getElementById(pre+'Font').onchange=()=>updateWeight(pre)}
root.querySelectorAll('[name=fontScope]').forEach(r=>r.onchange=()=>{scope=r.value;scopeUI()});scope='all';scopeUI();document.getElementById('fontPostSearch').oninput=drawPosts;document.getElementById('fontSelectVisible').onclick=()=>{for(const p of searchPosts())selected.add(p.id);drawPosts()};document.getElementById('fontRangeSave').onclick=saveRange;document.getElementById('fontPostSave').onclick=savePosts;document.getElementById('fontCustomSave').onclick=saveCustom;initMultiFields();drawPosts();drawCustom();drawDeleteList();initFontEdit()}
function scopeUI(){const el=document.getElementById('fontScopeExtra');if(!el)return;el.innerHTML=scope==='platform'?`<div class="field"><label>플랫폼 선택</label><select id="fontPlatformSelect"><option value="">플랫폼을 선택하세요</option><option value="instagram">Instagram</option><option value="twitter">X</option></select></div>`:scope==='folder'?`<div class="field"><label>폴더 선택</label><select id="fontFolderSelect"><option value="">폴더를 선택하세요</option>${renderFolderOptions()}</select></div>`:scope==='keyword'?`<div class="field"><label>키워드 (정확히 일치)</label><input id="fontKeyword" maxlength="100" placeholder="키워드 입력"></div>`:'';const info=document.getElementById('fontScopeInfo');const update=()=>{info.textContent=scope==='all'?'선택 범위: 전체 페이지':scope==='platform'?'선택 범위: '+(document.getElementById('fontPlatformSelect')?.selectedOptions[0]?.textContent||'플랫폼 미선택'):scope==='folder'?'선택 범위: '+(document.getElementById('fontFolderSelect')?.selectedOptions[0]?.textContent||'폴더 미선택'):'선택 범위: 키워드 '+(document.getElementById('fontKeyword')?.value||'미입력')};el.querySelectorAll('select,input').forEach(x=>x.addEventListener('input',update));update()}
function searchPosts(){const q=(document.getElementById('fontPostSearch')?.value||'').trim().toLocaleLowerCase();return q?(window.scrapFontData?.()||[]).filter(p=>[p.title,...(p.keywords||[])].join(' ').toLocaleLowerCase().includes(q)).slice(0,250):[]}
function drawPosts(){const el=document.getElementById('fontPostResults');if(!el)return;const ps=searchPosts();const hasQuery=!!(document.getElementById('fontPostSearch')?.value||'').trim();el.style.display=hasQuery?'':'none';document.getElementById('fontSelectVisible').disabled=!hasQuery||!ps.length;el.innerHTML=ps.length?ps.map(p=>`<label class="font-post-option"><input type="checkbox" data-font-check="${esc(p.id)}" ${selected.has(p.id)?'checked':''}><span><strong>${esc(p.title)}</strong><small>${esc((window.scrapFontFolders?.()||[]).find(f=>f.id===p.folderId)?.name||'폴더 없음')} · ${esc(p.platform)}</small></span></label>`).join(''):hasQuery?'<p class="hint">검색 결과가 없습니다.</p>':'';el.querySelectorAll('[data-font-check]').forEach(c=>c.onchange=()=>{if(c.checked)selected.add(c.dataset.fontCheck);else selected.delete(c.dataset.fontCheck);document.getElementById('fontSelectionCount').textContent=selected.size+'개 선택'});document.getElementById('fontSelectionCount').textContent=selected.size+'개 선택'}
async function saveRange(){let target='*';if(scope==='platform'){target=document.getElementById('fontPlatformSelect')?.value;if(!target)return alert('플랫폼을 선택해 주세요.')}if(scope==='folder'){target=document.getElementById('fontFolderSelect')?.value;if(!target)return alert('폴더를 선택해 주세요.')}if(scope==='keyword'){target=document.getElementById('fontKeyword')?.value.trim();if(!target)return alert('키워드를 입력해 주세요.')}const fontId=document.getElementById('rangeFont').value,weight=Number(document.getElementById('rangeWeight').value);const before=structuredClone(state);state.rules=state.rules.filter(r=>!(r.scope===scope&&r.target===target));state.rules.push({scope,target,fontId,weight,updated:nextRuleRevision()});if(await save())alert('폰트 설정을 저장했습니다.');else state=before}
async function savePosts(){if(!selected.size)return alert('스크랩을 선택해 주세요.');const before=structuredClone(state),fontId=document.getElementById('postFont').value,weight=Number(document.getElementById('postWeight').value),updated=nextRuleRevision();state.rules=state.rules.filter(r=>!(r.scope==='post'&&selected.has(r.target)));for(const target of selected)state.rules.push({scope:'post',target,fontId,weight,updated});if(await save())alert(selected.size+'개 스크랩의 폰트 설정을 저장했습니다.');else state=before}

let fontRegMode='single',multiCount=2;
function initMultiFields(){
 const opts=document.getElementById('fontMultiCountOptions');
 opts.innerHTML=Array.from({length:8},(_,i)=>`<button type="button" class="btn font-count-btn" data-count="${i+2}">${i+2}개</button>`).join('');
 opts.querySelectorAll('[data-count]').forEach(b=>b.onclick=()=>{multiCount=Number(b.dataset.count);document.getElementById('fontMultiCountLabel').textContent=multiCount+'개';document.getElementById('fontMultiCountDetails').open=false;renderMultiRows()});
 document.querySelectorAll('[name=fontRegMode]').forEach(r=>r.onchange=()=>{fontRegMode=r.value;document.getElementById('fontSingleFields').hidden=fontRegMode!=='single';document.getElementById('fontMultiFields').hidden=fontRegMode!=='multi'});
 renderMultiRows();
}
function renderMultiRows(){
 const el=document.getElementById('fontMultiRows');if(!el)return;
 const old=Array.from(el.querySelectorAll('.font-multi-row')).map(row=>({path:row.querySelector('[data-multi-path]').value,weight:row.querySelector('[data-multi-weight]').value}));
 const preset=[400,700,300,500,600,800,900,100,200];
 el.innerHTML=Array.from({length:multiCount},(_,i)=>`<div class="font-multi-row"><strong>폰트 파일 ${i+1}</strong><div class="field"><label>GitHub 폰트 파일 경로</label><input data-multi-path type="text" maxlength="200" placeholder="fonts/MyFont/MyFont-${i+1}.ttf" value="${esc(old[i]?.path||'')}"></div><div class="field"><label>굵기</label><select data-multi-weight>${[100,200,300,400,500,600,700,800,900].map(w=>`<option value="${w}" ${w===Number(old[i]?.weight||preset[i])?'selected':''}>${w}</option>`).join('')}</select></div></div>`).join('');
}
async function verifyPaths(paths){for(const path of paths){try{const res=await fetch(new URL('./'+path,document.baseURI),{method:'GET',cache:'no-store'});if(!res.ok)throw Error('HTTP '+res.status);if((res.headers.get('content-type')||'').includes('text/html'))throw Error('HTML 응답')}catch(e){if(!confirm('GitHub Pages에서 '+path+' 파일을 확인하지 못했습니다 ('+e.message+').\n배포 후 등록하는 것이 좋습니다. 그래도 저장하시겠습니까?'))return false}}return true}

async function saveCustom(){
 const name=document.getElementById('fontCustomName').value.trim(),family=document.getElementById('fontCustomFamily').value.trim();
 if(!name||!family)return alert('표시 이름과 폰트 식별 이름을 입력해 주세요.');
 if(state.fonts.some(f=>f.name.toLocaleLowerCase()===name.toLocaleLowerCase()))return alert('같은 이름의 폰트가 있습니다.');
 if(state.fonts.some(f=>f.family===family))return alert('같은 폰트 식별 이름이 있습니다.');
 let entry;
 if(fontRegMode==='multi'){
  const files=Array.from(document.querySelectorAll('.font-multi-row')).map(row=>({path:row.querySelector('[data-multi-path]').value.trim(),weight:Number(row.querySelector('[data-multi-weight]').value)}));
  if(files.length<2||files.length>9||files.some(f=>!validFontPath(f.path)))return alert('2~9개의 유효한 GitHub 폰트 파일 경로를 입력해 주세요.');
  if(new Set(files.map(f=>f.weight)).size!==files.length)return alert('서로 다른 굵기를 선택해 주세요.');
  if(new Set(files.map(f=>f.path)).size!==files.length)return alert('중복된 파일 경로가 있습니다.');
  entry={id:'custom-'+crypto.randomUUID(),name,family,files,weights:validWeights(files.map(f=>f.weight))};
 }else{
  const path=document.getElementById('fontCustomPath').value.trim(),weights=validWeights(document.getElementById('fontCustomWeights').value.split(',').map(x=>x.trim()));
  if(!validFontPath(path)||!weights.length)return alert('폰트 파일 경로와 굵기를 확인해 주세요.');
  entry={id:'custom-'+crypto.randomUUID(),name,family,path,weights};
 }
 if(!await verifyPaths(entry.files?entry.files.map(f=>f.path):[entry.path]))return;
 const before=structuredClone(state);state.fonts.push(entry);
 if(await save()){alert('GitHub 폰트가 등록되었습니다.');open()}else state=before;
}
function drawCustom(){const el=document.getElementById('fontCustomList');if(el)el.textContent='등록한 사용자 폰트: '+(state.fonts.filter(f=>f.id.startsWith('custom-')).map(f=>f.name).join(', ')||'없음')}
function initFontEdit(){
 const sel=document.getElementById('fontEditSelect');if(!sel)return;
 sel.innerHTML='<option value="">수정할 폰트를 선택하세요</option>'+state.fonts.filter(f=>f.id.startsWith('custom-')).map(f=>`<option value="${esc(f.id)}">${esc(f.name)}</option>`).join('');
 const options=document.getElementById('fontEditAccordionOptions');
 options.innerHTML=state.fonts.filter(f=>f.id.startsWith('custom-')).map(f=>`<button type="button" class="btn font-edit-option" data-edit-font="${esc(f.id)}">${esc(f.name)}</button>`).join('')||'<p class="hint">등록된 사용자 폰트가 없습니다.</p>';
 options.querySelectorAll('[data-edit-font]').forEach(button=>button.onclick=()=>{sel.value=button.dataset.editFont;document.getElementById('fontEditAccordionLabel').textContent=state.fonts.find(f=>f.id===sel.value)?.name||'수정할 폰트를 선택하세요';document.getElementById('fontEditAccordion').open=false;drawFontEdit()});
 sel.onchange=drawFontEdit;document.getElementById('fontEditSave').onclick=saveFontEdit;drawFontEdit();
}
function drawFontEdit(){
 const id=document.getElementById('fontEditSelect')?.value;
 const f=state.fonts.find(x=>x.id===id&&x.id.startsWith('custom-'));
 const wrap=document.getElementById('fontEditFields');if(!wrap)return;wrap.hidden=!f;if(!f)return;
 document.getElementById('fontEditName').value=f.name;
 document.getElementById('fontEditFamily').value=f.family;
 const files=Array.isArray(f.files)&&f.files.length>=2?f.files:null;
 const field=document.getElementById('fontEditFileFields');
 if(files){
  field.innerHTML='<p class="hint">다중 폰트는 각 파일의 GitHub 경로와 굵기를 개별 수정합니다.</p>'+files.map((file,i)=>`<div class="font-multi-row"><strong>폰트 파일 ${i+1}</strong><div class="field"><label>GitHub 폰트 파일 경로</label><input data-edit-path maxlength="200" value="${esc(file.path)}"></div><div class="field"><label>파일에서 지원하는 굵기 (쉼표 구분)</label><input data-edit-weights value="${esc(file.weight)}" placeholder="예: 400"></div></div>`).join('');
 }else{
  field.innerHTML=`<div class="field"><label>GitHub 폰트 파일 경로</label><input id="fontEditPath" maxlength="200" value="${esc(f.path||'')}" placeholder="fonts/MyFont-Regular.ttf"></div><div class="field"><label>파일에서 지원하는 굵기 (쉼표 구분)</label><input id="fontEditWeights" value="${esc((f.weights||[400]).join(', '))}" placeholder="400, 700"></div>`;
 }
}
function parseEditWeights(value){
 const parts=value.split(',').map(x=>x.trim());
 if(!parts.length||parts.some(x=>!/^\d+$/.test(x)))return null;
 const weights=validWeights(parts.map(Number));
 return weights.length===parts.length?weights:null;
}
function editStatus(message,isError=false){const el=document.getElementById('fontEditStatus');if(el){el.textContent=message;el.style.color=isError?'#b42318':''}if(isError)alert(message)}
function pathURL(path){return new URL(path,document.baseURI)}
async function checkFontFile(path,family,weight){
 const url=pathURL(path);
 if(url.origin!==location.origin)throw Error('GitHub Pages 사이트 내부 경로만 입력할 수 있습니다.');
 const requestURL=new URL(url.href);requestURL.searchParams.set('fontcheck',String(Date.now()));
 const response=await fetch(requestURL.href,{method:'GET',cache:'no-store'});
 if(!response.ok)throw Error(`${path}: HTTP ${response.status} — GitHub Pages 배포 파일을 확인해 주세요.`);
 const type=(response.headers.get('content-type')||'').toLowerCase();
 if(type.includes('text/html'))throw Error(`${path}: 폰트 대신 HTML이 반환되었습니다.`);
 const bytes=await response.arrayBuffer();
 if(bytes.byteLength<4)throw Error(`${path}: 빈 파일입니다.`);
 const b=new Uint8Array(bytes,0,4);
 const sig=String.fromCharCode(...b);
 if(!['wOF2','wOFF','OTTO'].includes(sig)&&!(b[0]===0&&b[1]===1&&b[2]===0&&b[3]===0))throw Error(`${path}: 올바른 웹폰트 파일이 아닙니다.`);
 const testFamily='FontEditCheck_'+Math.random().toString(36).slice(2);
 const face=new FontFace(testFamily,bytes,{style:'normal',weight:String(weight)});
 try{await face.load()}catch{throw Error(`${path}: 브라우저가 폰트 파일을 읽지 못했습니다.`)}
 return true;
}
async function saveFontEdit(){
 const button=document.getElementById('fontEditSave');if(button?.disabled)return;
 const id=document.getElementById('fontEditSelect')?.value;
 const original=state.fonts.find(f=>f.id===id&&f.id.startsWith('custom-'));
 if(!original)return editStatus('수정할 폰트를 선택해 주세요.',true);
 const name=document.getElementById('fontEditName').value.trim(),family=document.getElementById('fontEditFamily').value.trim();
 if(!name||!family||name.length>80||family.length>100)return editStatus('표시 이름과 폰트 식별 이름을 확인해 주세요.',true);
 if(/[\x00-\x1f]/.test(family))return editStatus('폰트 식별 이름에 제어 문자를 사용할 수 없습니다.',true);
 if(state.fonts.some(f=>f.id!==id&&f.name.toLocaleLowerCase()===name.toLocaleLowerCase()))return editStatus('이미 등록된 표시 이름입니다.',true);
 if(state.fonts.some(f=>f.id!==id&&f.family===family))return editStatus('이미 등록된 폰트 식별 이름입니다.',true);
 const entry={...original,name,family};let filesToCheck=[];
 if(Array.isArray(original.files)&&original.files.length>=2){
  const rows=[...document.querySelectorAll('#fontEditFileFields .font-multi-row')];const files=[];
  for(const row of rows){const path=row.querySelector('[data-edit-path]').value.trim(),weights=parseEditWeights(row.querySelector('[data-edit-weights]').value);
   if(!validFontPath(path)||!weights||weights.length!==1)return editStatus('다중 폰트의 각 파일에 유효한 경로와 굵기 1개를 입력해 주세요.',true);
   files.push({path,weight:weights[0]});}
  if(files.length<2||files.length>9||new Set(files.map(f=>f.path)).size!==files.length||new Set(files.map(f=>f.weight)).size!==files.length)return editStatus('다중 폰트의 파일 수, 경로 및 굵기 중복을 확인해 주세요.',true);
  entry.files=files;entry.weights=validWeights(files.map(f=>f.weight));delete entry.path;delete entry.css;
  filesToCheck=files;
 }else{
  const path=document.getElementById('fontEditPath').value.trim(),weights=parseEditWeights(document.getElementById('fontEditWeights').value);
  if(!validFontPath(path)||!weights||!weights.length)return editStatus('GitHub 폰트 경로 또는 굵기 정보를 확인해 주세요.',true);
  entry.path=path;entry.weights=weights;delete entry.files;delete entry.css;
  filesToCheck=[{path,weight:weights[0]}];
 }
 const before=structuredClone(state),oldVersion=fontVersions.get(id);
 button.disabled=true;button.textContent='파일 확인 및 저장 중…';editStatus('GitHub Pages 파일을 확인하고 있습니다.');
 try{
  for(const file of filesToCheck)await checkFontFile(file.path,family,file.weight);
  const index=state.fonts.findIndex(f=>f.id===id);state.fonts[index]=entry;
  // Stable font ID: existing scope rules still reference the same font.
  // Refresh weight selection when a previously selected weight is removed.
  for(const rule of state.rules){if(rule.fontId===id&&!entry.weights.includes(Number(rule.weight)))rule.weight=entry.weights.includes(400)?400:entry.weights[0]}
  const revision=String(Date.now());fontVersions.set(id,revision);
  if(!await save())throw Error('저장소에 폰트 정보를 저장하지 못했습니다.');
  // FontFace is tested before persistence; now refresh @font-face and all active views.
  installFonts();apply();
  open();const select=document.getElementById('fontEditSelect');if(select){select.value=id;const label=document.getElementById('fontEditAccordionLabel');if(label)label.textContent=entry.name;drawFontEdit()}
  editStatus('변경 사항을 저장하고 실제 화면에 적용했습니다.');
 }catch(error){state=before;if(oldVersion===undefined)fontVersions.delete(id);else fontVersions.set(id,oldVersion);rerender();editStatus('폰트 수정 실패: '+error.message,true)}
 finally{const current=document.getElementById('fontEditSave');if(current){current.disabled=false;current.textContent='변경 사항 저장 및 적용'}}
}

function drawDeleteList(){
 const el=document.getElementById('fontDeleteList');if(!el)return;
 const customs=state.fonts.filter(f=>f.id.startsWith('custom-'));
 if(!customs.length){el.innerHTML='<p class="hint">삭제할 사용자 등록 폰트가 없습니다.</p>';return}
 el.innerHTML=customs.map(f=>{
  const count=state.rules.filter(r=>r.fontId===f.id).length;
  const desc=Array.isArray(f.files)&&f.files.length?f.files.length+'개 파일':f.path?'단일 파일':'웹폰트 CSS';
  return `<div class="font-delete-row"><div><strong>${esc(f.name)}</strong><small>사용 중인 설정 ${count}개</small></div><button type="button" class="btn font-delete-btn" data-delete-font="${esc(f.id)}">삭제</button></div>`
 }).join('');
 el.querySelectorAll('[data-delete-font]').forEach(btn=>btn.onclick=()=>deleteCustomFont(btn.dataset.deleteFont));
}
async function deleteCustomFont(id){
 const f=state.fonts.find(x=>x.id===id&&x.id.startsWith('custom-'));if(!f)return;
 const affected=state.rules.filter(r=>r.fontId===id).length;
 const msg=`등록 폰트 “${f.name}”을(를) 삭제하시겠습니까?\n\n이 폰트를 사용하는 설정 ${affected}개도 해제됩니다. 해당 범위에는 남아 있는 다른 폰트 설정이 적용됩니다.\nGitHub의 실제 폰트 파일은 삭제되지 않습니다.`;
 if(!confirm(msg))return;
 const before=structuredClone(state);
 state.fonts=state.fonts.filter(x=>x.id!==id);
 state.rules=state.rules.filter(r=>r.fontId!==id);
 if(await save()){alert('등록된 폰트를 삭제했습니다.');open()}else{state=before;rerender()}
}
function style(){const s=document.createElement('style');s.textContent=`.font-dialog{width:min(760px,100%)}.font-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.font-head h2{margin:0}.font-section{padding:15px 0}.font-section h3{font-size:16px;margin:0 0 16px}.font-radio{display:flex;gap:15px;flex-wrap:wrap;margin-bottom:14px}.font-radio label{display:flex;gap:5px;align-items:center}.font-save{display:flex;justify-content:center;margin:18px 0 4px}.font-post-results{max-height:260px;overflow:auto;border:1px solid #e3e7f0;border-radius:10px}.font-post-option{display:flex;align-items:start;gap:10px;padding:10px 12px;border-bottom:1px solid #edf0f5}.font-post-option:last-child{border:0}.font-post-option span{display:grid;gap:4px}.font-post-option small{color:#7d8596}.font-result-head{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px}.font-result-head .btn{font-size:12px}.font-count-accordion{border:1px solid #e3e7f0;border-radius:10px;padding:12px;margin-bottom:14px}.font-count-accordion summary{cursor:pointer;font-weight:600}.font-count-options{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.font-multi-row{border:1px solid #e3e7f0;border-radius:10px;padding:12px;margin:10px 0}.font-multi-row strong{display:block;margin-bottom:10px}.font-edit-options{display:grid;gap:7px;margin-top:12px}.font-edit-option{text-align:left;width:100%;justify-content:flex-start}.font-delete-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px;border:1px solid #e3e7f0;border-radius:10px;margin:8px 0}.font-delete-row>div{display:grid;gap:5px;min-width:0;overflow-wrap:anywhere}.font-delete-row small{color:#7d8596}.font-delete-btn{flex-shrink:0}.font-dialog [hidden]{display:none!important}.font-dialog hr{border:0;border-top:1px solid #e4e8f0;margin:8px 0}`;document.head.append(s)}
function init(){style();const exportBtn=document.getElementById('exportBtn');if(!exportBtn)return;const btn=document.createElement('button');btn.className='btn';btn.id='fontSettingsBtn';btn.textContent='font ver.';const importBtn=document.getElementById('importBtn');exportBtn.textContent='Backup_Export';if(importBtn)importBtn.textContent='Backup_Upload';exportBtn.parentNode.insertBefore(btn,exportBtn);if(importBtn)exportBtn.parentNode.insertBefore(importBtn,exportBtn);btn.onclick=open;window.scrapFontData=()=>window.scrapFontPosts?.()||[];
const view=document.getElementById('view');
if(view){let scheduled=false;new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;apply()})}).observe(view,{childList:true,subtree:true})}
rerender();setTimeout(reloadCloud,1300);setInterval(()=>{if(window.scrapSync?.active)reloadCloud();else if(activeUser){activeUser=null;state=loadLocal();rerender()}},15000)}
window.scrapFontApply=apply;window.scrapFontCloudRefresh=reloadCloud;document.addEventListener('DOMContentLoaded',init);
})();
