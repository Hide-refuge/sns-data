/* Read-only export of existing admin font metadata/rules for approved public guest snapshot. */
(()=>{'use strict';
 const KEY='scrap-font-settings-v1';
 function init(){
   if(window.SCRAP_GUEST_MODE)return;
   if(document.getElementById('guestFontExportBtn'))return;
   const actions=document.querySelector('header .actions');if(!actions)return;
   const btn=document.createElement('button');btn.type='button';btn.className='btn';btn.id='guestFontExportBtn';
   btn.textContent='게스트 폰트 내보내기';btn.title='폰트 파일은 복사하지 않고 공개용 폰트 설정 정보만 JSON으로 저장합니다.';
   actions.append(btn);
   btn.addEventListener('click',async()=>{
     try{
       let state=null;
       if(window.scrapSync?.active&&typeof window.scrapSync.fontGet==='function'){
         state=await window.scrapSync.fontGet();
       }else{
         const raw=localStorage.getItem(KEY);if(raw)state=JSON.parse(raw);
       }
       if(!state||!Array.isArray(state.fonts)||!Array.isArray(state.rules)){
         alert('저장된 폰트 정보를 찾지 못했습니다. Google 로그인 후 클라우드 동기화가 완료되면 다시 시도해 주세요.');return;
       }
       const custom=state.fonts.filter(f=>typeof f?.id==='string'&&f.id.startsWith('custom-')).length;
       if(!confirm(`공개용 게스트 폰트 설정을 내보냅니다.\n사용자 등록 폰트 ${custom}개, 적용 규칙 ${state.rules.length}개가 포함됩니다.\n폰트 이름·경로·적용 대상 ID가 GitHub 공개 파일에 포함됩니다. 계속하시겠습니까?`))return;
       const blob=new Blob([JSON.stringify({fonts:state.fonts,rules:state.rules},null,2)],{type:'application/json'});
       const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='guest-fonts.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
     }catch(err){alert('폰트 정보 내보내기 실패: '+(err?.message||err))}
   });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
