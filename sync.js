/* SNS 스크랩 허브 Supabase 동기화 모듈. 기존 IndexedDB는 로그아웃 시 그대로 사용됩니다. */
(() => {
  'use strict';
  const config = window.SCRAP_SUPABASE_CONFIG || {};
  const table = {folders:'scrap_folders',posts:'scrap_posts'};
  const valid = /^https:\/\//.test(config.url||'') && /^(sb_publishable_|eyJ)/.test(config.publishableKey||'');
  let client=null, user=null, busy=false, lastSync=0;
  const sync={active:false}; window.scrapSync=sync;
  const $ = id => document.getElementById(id);
  const msg = (s) => {if($('syncStatus')) $('syncStatus').textContent=s;};
  const errText = e => (e && e.message) || String(e);
  const localAll = store => new Promise((resolve,reject)=>{
    const req=indexedDB.open('personal-scrap-hub-v1',1);
    req.onerror=()=>reject(req.error);
    req.onsuccess=()=>{
      const d=req.result;
      const tx=d.transaction(store,'readonly');const r=tx.objectStore(store).getAll();
      r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);
      tx.oncomplete=()=>d.close();
    };
  });
  function errorCheck({error,data}){if(error)throw error;return data;}
  async function fetchAll(store){
    const out=[];let from=0;
    while(true){
      const batch=errorCheck(await client.from(table[store]).select('id,data').eq('user_id',user.id).order('id').range(from,from+499));
      out.push(...batch.map(x=>x.data));
      if(batch.length<500)break;
      from+=500;
    }
    return out;
  }
  sync.getAll=async store=>{
    if(!sync.active)throw Error('로그인되지 않았습니다.');
    return fetchAll(store);
  };
  sync.put=async(store,record)=>{
    if(!sync.active)throw Error('로그인되지 않았습니다.');
    errorCheck(await client.from(table[store]).upsert({id:record.id,user_id:user.id,data:record,updated_at:new Date().toISOString()},{onConflict:'user_id,id'}));
    return record.id;
  };
  sync.del=async(store,id)=>{
    if(!sync.active)throw Error('로그인되지 않았습니다.');
    errorCheck(await client.from(table[store]).delete().eq('user_id',user.id).eq('id',id));
  };
  async function update(){
    if(!sync.active||busy||document.hidden)return;
    busy=true;
    try{
      const [f,p]=await Promise.all([fetchAll('folders'),fetchAll('posts')]);
      // 기존 페이지의 전역 상태를 건드리지 않고 기존 refresh()를 통해 갱신합니다.
      // 입력 중인 대화상자가 있으면 화면 재구성을 피합니다.
      const signature=JSON.stringify([f,p]);
      if(signature!==sync.lastSignature){
        sync.lastSignature=signature;
        if(!document.querySelector('#modalRoot .overlay') && !document.querySelector('#folderForm:focus-within')){
          await window.scrapRefresh?.();
        }
      }
      lastSync=Date.now();msg('클라우드 연결됨 · 마지막 확인 '+new Date(lastSync).toLocaleTimeString('ko-KR'));
    }catch(e){msg('동기화 확인 실패: '+errText(e));}
    finally{busy=false;}
  }
  async function setSession(session){
    user=session?.user||null;sync.active=!!user;
    sync.lastSignature=null;
    draw();
    if(sync.active){msg('로그인됨: '+user.email+' · 클라우드 데이터 불러오는 중');await window.scrapRefresh?.();}
    else{msg(valid?'로그아웃 상태 · 이 기기의 IndexedDB 사용':'연결 설정 필요: sync-config.js의 Publishable key를 입력하세요.');await window.scrapRefresh?.();}
  }
  function draw(){
    const root=$('syncControls');if(!root)return;
    if(!valid){root.innerHTML='<p class="warning">sync-config.js 파일에 Supabase Publishable key를 입력한 뒤 GitHub에 업로드하세요. 비밀키는 절대 사용하지 마세요.</p>';return;}
    if(user){
      root.innerHTML=`<div class="actions"><button class="btn" id="syncNow">지금 동기화</button><button class="btn" id="migrateLocal">iPad 로컬 자료를 클라우드로 복사</button><button class="btn" id="syncLogout">로그아웃</button></div><p class="hint">로그인 중에는 클라우드에 저장됩니다. 기존 로컬 자료는 자동으로 삭제되지 않습니다. 로컬 자료 이전은 최초 1회만 실행하세요.</p>`;
      $('syncNow').onclick=()=>{sync.lastSignature=null;update()};
      $('syncLogout').onclick=async()=>{try{errorCheck(await client.auth.signOut())}catch(e){alert(errText(e))}};
      $('migrateLocal').onclick=migrate;
    }else{
      root.innerHTML=`<form id="syncLogin"><div class="field"><label>이메일</label><input name="email" type="email" autocomplete="email" required></div><div class="field"><label>비밀번호 (6자 이상)</label><input name="password" type="password" minlength="6" autocomplete="current-password" required></div><div class="actions"><button class="btn primary" type="submit">로그인</button><button class="btn" type="button" id="syncSignup">계정 생성</button></div></form><p class="hint">Supabase 인증 계정으로 두 기기에서 동일하게 로그인하세요. 계정 생성 시 이메일 확인이 필요할 수 있습니다.</p>`;
      $('syncLogin').onsubmit=async e=>{e.preventDefault();const fd=new FormData(e.target);try{const result=await client.auth.signInWithPassword({email:String(fd.get('email')),password:String(fd.get('password'))});errorCheck(result);await setSession(result.data.session)}catch(err){alert('로그인 실패: '+errText(err))}};
      $('syncSignup').onclick=async()=>{const fd=new FormData($('syncLogin'));const email=String(fd.get('email')),password=String(fd.get('password'));if(!email||password.length<6){alert('이메일과 6자 이상의 비밀번호를 입력하세요.');return}try{const result=await client.auth.signUp({email,password});errorCheck(result);alert(result.data.session?'계정이 생성되었습니다.':'계정 생성 요청이 완료되었습니다. 이메일 인증 메시지를 확인한 후 로그인하세요.');if(result.data.session)await setSession(result.data.session)}catch(err){alert('계정 생성 실패: '+errText(err))}};
    }
  }
  async function migrate(){
    if(!sync.active)return;
    const localFolders=await localAll('folders'),localPosts=await localAll('posts');
    if(!localFolders.length&&!localPosts.length){alert('이 기기에 이전할 로컬 자료가 없습니다.');return;}
    if(!confirm(`로컬 폴더 ${localFolders.length}개, 스크랩 ${localPosts.length}개를 현재 로그인 계정으로 복사합니다. 클라우드에 같은 ID가 있으면 기존 클라우드 항목을 유지합니다. 계속하시겠습니까?`))return;
    const button=$('migrateLocal');button.disabled=true;
    try{
      let count=0;
      for(const [store,records] of [['folders',localFolders],['posts',localPosts]]){
        for(const r of records){
          const {error}=await client.from(table[store]).insert({id:r.id,user_id:user.id,data:r});
          if(error && error.code!=='23505')throw error;
          if(!error)count++;
        }
      }
      alert(`이전 완료: 신규 ${count}개 항목을 복사했습니다. 로컬 원본은 그대로 남아 있습니다.`);
      await window.scrapRefresh?.();
    }catch(e){alert('일부 자료 이전 실패: '+errText(e)+'\n다시 실행해도 같은 ID의 기존 자료는 덮어쓰지 않습니다. 이미지가 크면 용량을 줄여주세요.');}
    finally{if(button.isConnected)button.disabled=false;}
  }
  async function init(){
    // 기존 스크립트의 refresh 함수를 외부 모듈에서 안전하게 호출할 수 있게 연결
    if(typeof window.scrapRefresh!=='function'){
      setTimeout(init,100);return;
    }
    if(!valid||!window.supabase?.createClient){draw();msg(valid?'Supabase 라이브러리를 불러오지 못했습니다. 인터넷 연결을 확인하세요.':'Publishable key를 설정해야 합니다.');return;}
    client=window.supabase.createClient(config.url,config.publishableKey,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
    const {data,error}=await client.auth.getSession();if(error)msg('세션 확인 오류: '+errText(error));
    await setSession(data?.session);
    client.auth.onAuthStateChange((event,session)=>{
      if(event==='SIGNED_IN' && user?.id!==session?.user?.id) setTimeout(()=>setSession(session),0);
      if(event==='SIGNED_OUT')setTimeout(()=>setSession(null),0);
    });
    setInterval(update,15000);
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)update()});
  }
  window.addEventListener('load',init);
})();
