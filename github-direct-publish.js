
(() => {
  'use strict';

  const OWNER = 'Hide-refuge';
  const REPO = 'sns-data';
  const BRANCH = 'main';
  const FILE = 'guest-data.json';
  const BUTTON_ID = 'githubDirectPublishBtn';

  function base64Utf8(text) {
    const bytes = new TextEncoder().encode(text);
    let binary = '';
    for (let i = 0; i < bytes.length; i += 8192) {
      binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
    }
    return btoa(binary);
  }

  async function githubRequest(url, token, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + token,
        'X-GitHub-Api-Version': '2022-11-28',
        ...(options.headers || {})
      },
      cache: 'no-store'
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      const messages = {
        401: '토큰이 유효하지 않습니다.',
        403: 'GitHub 접근 권한이 부족하거나 요청이 제한되었습니다.',
        404: '저장소 또는 파일에 접근할 수 없습니다. 토큰 권한을 확인하세요.',
        409: 'GitHub 파일이 변경되었습니다. 새로 확인한 후 다시 게시하세요.',
        422: 'GitHub가 변경 요청을 거부했습니다. 파일 상태를 확인하세요.'
      };
      throw new Error(messages[response.status] ||
        result.message || 'HTTP ' + response.status);
    }

    return result;
  }

  async function readLocalData() {
    if (!window.scrapSync?.getAll) {
      throw new Error('데이터 동기화 연결을 확인해 주세요.');
    }

    const [folders, posts] = await Promise.all([
      window.scrapSync.getAll('folders'),
      window.scrapSync.getAll('posts')
    ]);

    if (!Array.isArray(folders) || !Array.isArray(posts)) {
      throw new Error('폴더 또는 스크랩 데이터를 읽지 못했습니다.');
    }

    return { version: 1, folders, posts };
  }


  function requestGitHubToken() {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.style.cssText =
        'position:fixed;inset:0;z-index:2147483647;' +
        'background:rgba(0,0,0,.5);display:flex;' +
        'align-items:center;justify-content:center;padding:20px;';

      const panel = document.createElement('div');
      panel.style.cssText =
        'background:#fff;color:#222;border-radius:14px;' +
        'padding:24px;width:min(100%,420px);box-sizing:border-box;' +
        'box-shadow:0 12px 40px rgba(0,0,0,.2);';

      const title = document.createElement('h3');
      title.textContent = 'GitHub 게시 인증';
      title.style.margin = '0 0 12px';

      const description = document.createElement('p');
      description.textContent =
        'Hide-refuge/sns-data의 main 브랜치에 guest-data.json을 게시합니다. ' +
        'GitHub 토큰은 게시할 때마다 입력하며 저장하지 않습니다.';
      description.style.cssText =
        'font-size:13px;line-height:1.6;margin:0 0 16px;';

      const input = document.createElement('input');
      input.type = 'password';
      input.placeholder = 'GitHub Personal Access Token';
      input.autocomplete = 'off';
      input.spellcheck = false;
      input.style.cssText =
        'width:100%;box-sizing:border-box;padding:12px;' +
        'border:1px solid #aaa;border-radius:8px;font-size:14px;';

      const actions = document.createElement('div');
      actions.style.cssText =
        'display:flex;justify-content:flex-end;gap:10px;margin-top:18px;';

      const cancel = document.createElement('button');
      cancel.type = 'button';
      cancel.textContent = '취소';

      const confirm = document.createElement('button');
      confirm.type = 'button';
      confirm.textContent = '게시 진행';

      for (const button of [cancel, confirm]) {
        button.style.cssText =
          'padding:10px 15px;border-radius:8px;' +
          'border:1px solid #aaa;cursor:pointer;';
      }

      confirm.style.background = '#455abf';
      confirm.style.color = '#fff';

      let finished = false;

      function finish(value) {
        if (finished) return;
        finished = true;
        document.removeEventListener('keydown', onKeydown);
        input.value = '';
        overlay.remove();
        resolve(value);
      }

      function onKeydown(event) {
        if (event.key === 'Escape') {
          event.preventDefault();
          finish('');
        }
      }

      cancel.addEventListener('click', () => finish(''));

      confirm.addEventListener('click', () => {
        const value = input.value.trim();
        if (!value) {
          input.focus();
          return;
        }
        finish(value);
      });

      input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          event.preventDefault();
          confirm.click();
        }
      });

      document.addEventListener('keydown', onKeydown);

      actions.append(cancel, confirm);
      panel.append(title, description, input, actions);
      overlay.appendChild(panel);
      document.body.appendChild(overlay);
      input.focus();
    });
  }

  async function publish(button) {
    const originalText = button.textContent;
    let token = '';

    button.disabled = true;
    button.textContent = '게시 준비 중...';

    try {
      const payload = await readLocalData();

      if (!confirm(
        'GitHub 공개 게시를 준비합니다.\n\n' +
        '대상: ' + OWNER + '/' + REPO + '\n' +
        '브랜치: ' + BRANCH + '\n' +
        '파일: ' + FILE + '\n\n' +
        '폴더: ' + payload.folders.length + '개\n' +
        '스크랩: ' + payload.posts.length + '개\n\n' +
        '스크랩의 제목, 링크, 설명, 이미지 및 기타 정보가 ' +
        '공개될 수 있습니다.\n\n계속하시겠습니까?'
      )) return;

      token = await requestGitHubToken();
      if (!token) return;

      token = token.trim();
      if (!token) return;

      button.textContent = 'GitHub 파일 확인 중...';

      const apiUrl =
        'https://api.github.com/repos/' +
        encodeURIComponent(OWNER) + '/' +
        encodeURIComponent(REPO) +
        '/contents/' + FILE;

      const current = await githubRequest(
        apiUrl + '?ref=' + encodeURIComponent(BRANCH),
        token
      );

      if (!current.sha || current.type !== 'file') {
        throw new Error('기존 GitHub 파일 정보를 확인하지 못했습니다.');
      }

      if (!confirm(
        '최종 게시 확인\n\n' +
        '현재 GitHub 파일을 새로운 공개 데이터로 교체합니다.\n' +
        '폴더 ' + payload.folders.length + '개 / ' +
        '스크랩 ' + payload.posts.length + '개\n\n' +
        '기존 공개 데이터는 새 데이터로 대체됩니다.\n' +
        '게시하시겠습니까?'
      )) return;

      button.textContent = 'GitHub에 게시 중...';

      const content = base64Utf8(
        JSON.stringify(payload, null, 2) + '\n'
      );

      const result = await githubRequest(apiUrl, token, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Update guest archive data from admin page',
          content,
          sha: current.sha,
          branch: BRANCH
        })
      });

      if (!result.commit?.sha) {
        throw new Error('게시 결과에서 커밋 정보를 확인하지 못했습니다.');
      }

      alert(
        'GitHub 게시 완료\n\n' +
        '폴더: ' + payload.folders.length + '개\n' +
        '스크랩: ' + payload.posts.length + '개\n' +
        '커밋: ' + result.commit.sha.slice(0, 7) + '\n\n' +
        '공개 페이지 반영에는 시간이 걸릴 수 있습니다.'
      );

    } catch (error) {
      alert('GitHub 게시 실패:\n' + (error.message || String(error)));
    } finally {
      token = '';
      button.disabled = false;
      button.textContent = originalText;
    }
  }

  function init() {
    if (window.SCRAP_GUEST_MODE === true) return;

    const backupBtn = document.getElementById('exportBtn');
    if (!backupBtn || document.getElementById(BUTTON_ID)) return;

    const button = document.createElement('button');
    button.id = BUTTON_ID;
    button.type = 'button';
    button.className = backupBtn.className;
    button.textContent = 'GitHub에 게시';
    button.title = '현재 데이터를 GitHub 공개 파일에 게시합니다.';

    backupBtn.insertAdjacentElement('afterend', button);
    button.addEventListener('click', () => publish(button));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
