/* Guest entry button: navigation gate only, NOT server authentication. */
(() => {
  'use strict';
  const GUEST_URL = './guest.html';
  const LOGIN_ID = 'guestEntryButton';
  const MODAL_ID = 'guestLoginDialog';
  const css = document.createElement('style');
  css.textContent = `
    #${MODAL_ID}{border:0;border-radius:16px;max-width:min(420px,calc(100vw - 32px));width:100%;padding:0;box-shadow:0 22px 75px #17203855;color:#293142;background:white}
    #${MODAL_ID}::backdrop{background:rgba(15,23,42,.58)}
    #${MODAL_ID} form{padding:24px;display:grid;gap:12px}
    #${MODAL_ID} h2{font-size:21px;margin:0 0 4px}
    #${MODAL_ID} label{display:grid;gap:6px;font-size:14px;font-weight:600}
    #${MODAL_ID} input{padding:11px;border:1px solid #cbd5e1;border-radius:9px;width:100%;font-size:16px}
    #${MODAL_ID} .guest-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:8px}
    #${MODAL_ID} .guest-actions button{border:1px solid #d6deeb;border-radius:9px;padding:10px 16px;background:white}
    #${MODAL_ID} .guest-actions button[type=submit]{background:#435bc0;color:white;border-color:#435bc0}
    #${MODAL_ID} .guest-error{min-height:20px;color:#b42318;font-size:13px;margin:0}
    #${LOGIN_ID}{margin-left:8px}
  `;
  document.head.append(css);
  const modal = document.createElement('dialog');
  modal.id = MODAL_ID;
  modal.innerHTML = `<form method="dialog" id="guestLoginForm" autocomplete="off">
    <h2>게스트 로그인</h2>
    <p style="margin:0;color:#64748b;font-size:13px">공개용 스크랩 열람 · 읽기 전용</p>
    <label for="guestUsername">계정<input id="guestUsername" name="username" autocomplete="username" required></label>
    <label for="guestPassword">비밀번호<input id="guestPassword" name="password" type="password" autocomplete="off" required></label>
    <p class="guest-error" id="guestLoginError" role="alert" aria-live="polite"></p>
    <div class="guest-actions"><button type="button" id="guestCancel">취소</button><button type="submit">로그인</button></div>
  </form>`;
  document.body.append(modal);
  const form = modal.querySelector('form');
  const error = modal.querySelector('#guestLoginError');
  modal.querySelector('#guestCancel').addEventListener('click', () => modal.close());
  modal.addEventListener('click', e => { if (e.target === modal) modal.close(); });
  form.addEventListener('submit', e => {
    e.preventDefault();
    const user = modal.querySelector('#guestUsername').value.trim();
    const pass = modal.querySelector('#guestPassword').value;
    // This is only a convenience gate. All guest files remain public.
    if (user === 'guest' && pass === '1234') {
      form.reset();
      modal.close();
      window.location.assign(GUEST_URL);
    } else {
      error.textContent = '계정 또는 비밀번호가 일치하지 않습니다.';
      modal.querySelector('#guestPassword').value = '';
      modal.querySelector('#guestPassword').focus();
    }
  });
  function addButton() {
    const google = document.getElementById('googleLogin');
    const root = google?.parentElement || document.getElementById('syncControls');
    if (!root) return;
    let button = document.getElementById(LOGIN_ID);
    if (button && button.parentElement === root) return;
    if (button) button.remove();
    button = document.createElement('button');
    button.id = LOGIN_ID;
    button.type = 'button';
    button.className = 'btn';
    button.textContent = '게스트 로그인';
    button.addEventListener('click', () => {
      error.textContent = '';
      form.reset();
      modal.showModal();
      modal.querySelector('#guestUsername').focus();
    });
    root.append(button);
  }
  addButton();
  const root = document.getElementById('syncControls');
  if (root) {
    let queued = false;
    new MutationObserver(() => {
      if (queued) return;
      queued = true;
      queueMicrotask(() => { queued = false; addButton(); });
    }).observe(root, {childList:true});
  }
})();
