/* Scrap Hub image gallery — independent enhancement, no data writes. */
(() => {
  'use strict';
  if (window.scrapImageGalleryInstalled) return;
  window.scrapImageGalleryInstalled = true;
  const style = document.createElement('style');
  style.textContent = `
    /* 간략형·제목형: 좌측에는 첫 번째 이미지 한 장만 표시 */
    .note.compact .note-cover,.note.titleonly .note-cover{overflow:hidden;margin:0;isolation:auto;}
    .note.compact .thumbs,.note.titleonly .thumbs,.note.compact .thumbs.gallery-thumbs-many,.note.titleonly .thumbs.gallery-thumbs-many{display:none!important;}
    .note-cover .cover-count.gallery-count{bottom:3px;right:3px;font-weight:700;font-size:11px;background:#1d2439dd;padding:3px 7px;}
    /* 3장 이상: 대표 사진 1장만 보이고 나머지는 확대 갤러리에서 탐색 */
    .note .thumbs.gallery-thumbs-many{position:relative;display:flex;flex-wrap:wrap;align-items:flex-start;gap:0;padding:6px 9px 0 2px;}
    .note .thumbs.gallery-thumbs-many .thumb{display:none;}
    .note .thumbs.gallery-thumbs-many .thumb:first-child{display:block;box-shadow:3px -3px 0 #f6f7fb,6px -6px 0 #cdd5e7;}
    .note .thumbs.gallery-thumbs-many .gallery-thumbs-count{flex-basis:100%;margin-top:7px;}
    .gallery-thumbs-count{display:block;width:100%;font-size:11px;color:#788092;font-weight:700;margin-top:2px;}
    .scrap-gallery-overlay{position:fixed;inset:0;z-index:10000;background:rgba(16,20,32,.93);display:flex;align-items:center;justify-content:center;padding:58px 58px 65px;}
    .scrap-gallery-stage{position:relative;display:flex;align-items:center;justify-content:center;width:100%;height:100%;min-height:0;}
    .scrap-gallery-photo{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;}
    .scrap-gallery-control{position:absolute;z-index:2;border:1px solid #ffffff66;background:#1f293bcc;color:white;border-radius:50%;width:44px;height:44px;font-size:27px;display:flex;align-items:center;justify-content:center;cursor:pointer;touch-action:manipulation;}
    .scrap-gallery-control:focus-visible{outline:3px solid #b9c3ff;outline-offset:3px;}
    .scrap-gallery-prev{left:-50px;top:50%;transform:translateY(-50%)}
    .scrap-gallery-next{right:-50px;top:50%;transform:translateY(-50%)}
    .scrap-gallery-close{right:12px;top:12px;font-size:25px;}
    .scrap-gallery-position{position:absolute;bottom:17px;left:50%;transform:translateX(-50%);color:white;font-size:14px;background:#182032b0;padding:6px 14px;border-radius:22px;white-space:nowrap;}
    @media(max-width:760px){.scrap-gallery-overlay{padding:60px 36px 66px}.scrap-gallery-control{width:36px;height:36px;font-size:23px}.scrap-gallery-prev{left:-34px}.scrap-gallery-next{right:-34px}}
  `;
  document.head.appendChild(style);
  let current = null;
  let priorFocus = null;
  function allPosts(){return typeof window.scrapFontPosts === 'function' ? window.scrapFontPosts() : [];}
  function decorate(){
    document.querySelectorAll('.note-cover').forEach(cover => {
      const img = cover.querySelector('img[data-image]');
      if(!img) return;
      const post = allPosts().find(p => String(p.id) === String(img.dataset.image));
      const count = Array.isArray(post?.images) ? post.images.length : 0;
      cover.classList.remove('gallery-stack');
      const label = cover.querySelector('.cover-count');
      if(label){const next=count >= 1 ? `${count}장` : '';if(label.textContent!==next)label.textContent=next;label.classList.toggle('gallery-count', count >= 1);}
      else if(count >= 1){const span = document.createElement('span');span.className='cover-count gallery-count';span.textContent=`${count}장`;cover.appendChild(span);}
    });
    document.querySelectorAll('.note .thumbs').forEach(group=>{
      const images=group.querySelectorAll('img[data-image]');
      group.classList.toggle('gallery-thumbs-many',images.length>=3);
      let badge=group.querySelector('.gallery-thumbs-count');
      if(images.length){
        if(!badge){badge=document.createElement('span');badge.className='gallery-thumbs-count';group.appendChild(badge);}
        const next=images.length+'장';if(badge.textContent!==next)badge.textContent=next;
      }else if(badge){badge.remove();}
    });
  }
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if(scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {scheduled=false;decorate();});
  });
  observer.observe(document.body,{childList:true,subtree:true});
  function close(){
    if(!current)return;
    document.getElementById('scrapGalleryOverlay')?.remove();
    current=null;
    priorFocus?.focus?.();priorFocus=null;
  }
  function paint(){
    if(!current)return;
    const overlay=document.getElementById('scrapGalleryOverlay');
    if(!overlay)return;
    const img=overlay.querySelector('.scrap-gallery-photo');
    img.src=current.images[current.index];
    img.alt=`확대 이미지 ${current.index+1} / ${current.images.length}`;
    overlay.querySelector('.scrap-gallery-position').textContent=`${current.index+1} / ${current.images.length}`;
    overlay.querySelectorAll('[data-gallery-step]').forEach(btn=>{btn.hidden=current.images.length<2;});
  }
  function step(delta){if(!current)return;current.index=(current.index+delta+current.images.length)%current.images.length;paint();}
  function open(postId,index){
    const post=allPosts().find(p=>String(p.id)===String(postId));
    if(!Array.isArray(post?.images)||post.images.length===0)return false;
    close();priorFocus=document.activeElement;
    current={images:post.images,index:Math.max(0,Math.min(Number(index)||0,post.images.length-1))};
    const overlay=document.createElement('div');overlay.className='scrap-gallery-overlay';overlay.id='scrapGalleryOverlay';
    overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label','스크랩 이미지 확대');
    overlay.innerHTML=`<button type="button" class="scrap-gallery-control scrap-gallery-close" aria-label="닫기" data-gallery-close>×</button><div class="scrap-gallery-stage"><button type="button" class="scrap-gallery-control scrap-gallery-prev" aria-label="이전 이미지" data-gallery-step="-1">‹</button><img class="scrap-gallery-photo" alt=""><button type="button" class="scrap-gallery-control scrap-gallery-next" aria-label="다음 이미지" data-gallery-step="1">›</button></div><div class="scrap-gallery-position" aria-live="polite"></div>`;
    overlay.addEventListener('click',e=>{const closeBtn=e.target.closest('[data-gallery-close]');const stepBtn=e.target.closest('[data-gallery-step]');if(closeBtn)close();else if(stepBtn)step(Number(stepBtn.dataset.galleryStep));else if(e.target===overlay)close();});
    let startX=null;
    overlay.addEventListener('touchstart',e=>{if(e.touches.length===1)startX=e.touches[0].clientX;},{passive:true});
    overlay.addEventListener('touchend',e=>{if(startX===null||e.changedTouches.length!==1)return;const dx=e.changedTouches[0].clientX-startX;startX=null;if(Math.abs(dx)>55)step(dx<0?1:-1);},{passive:true});
    document.body.appendChild(overlay);paint();overlay.querySelector('[data-gallery-close]').focus();return true;
  }
  document.addEventListener('click',e=>{
    const img=e.target.closest('[data-image]');
    if(img && open(img.dataset.image,img.dataset.index)){e.preventDefault();e.stopImmediatePropagation();}
  },true);
  document.addEventListener('keydown',e=>{
    if(current){if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();e.stopImmediatePropagation();step(e.key==='ArrowLeft'?-1:1);}else if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();close();}return;}
    if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-image]')){if(open(e.target.dataset.image,e.target.dataset.index)){e.preventDefault();e.stopImmediatePropagation();}}
  },true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',decorate,{once:true});else decorate();
})();
