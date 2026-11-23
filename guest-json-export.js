
(() => {
  'use strict';

  function init() {
    if (window.SCRAP_GUEST_MODE) return;

    const backupBtn = document.getElementById('exportBtn');
    if (!backupBtn || document.getElementById('guestJsonExportBtn')) {
      return;
    }

    const button = document.createElement('button');
    button.id = 'guestJsonExportBtn';
    button.type = 'button';
    button.className = backupBtn.className;
    button.textContent = '게스트 JSON 내보내기';
    button.title = '현재 관리자 데이터를 공개용 JSON으로 저장합니다.';

    backupBtn.insertAdjacentElement('afterend', button);

    button.addEventListener('click', async () => {
      if (button.disabled) return;

      const originalText = button.textContent;
      button.disabled = true;
      button.textContent = 'JSON 생성 중...';

      try {
        if (!window.scrapSync?.getAll) {
          throw new Error('Google Drive 동기화 연결을 확인해 주세요.');
        }

        const [allFolders, allPosts] = await Promise.all([
          window.scrapSync.getAll('folders'),
          window.scrapSync.getAll('posts')
        ]);
        // foldertrash-20261123: 휴지통 항목은 공개용 JSON에서 제외
        const folders = Array.isArray(allFolders) ? allFolders.filter(x => !x?.trashedAt) : allFolders;
        const posts = Array.isArray(allPosts) ? allPosts.filter(x => !x?.trashedAt) : allPosts;

        if (!Array.isArray(folders) || !Array.isArray(posts)) {
          throw new Error('폴더 또는 스크랩 데이터를 읽지 못했습니다.');
        }

        const payload = {
          version: 1,
          folders,
          posts
        };

        const message =
          '게스트 페이지에 공개할 데이터입니다.\n\n' +
          '폴더: ' + folders.length + '개\n' +
          '스크랩: ' + posts.length + '개\n\n' +
          '개인정보나 비공개 자료가 포함되지 않았는지 ' +
          '반드시 확인한 후 GitHub에 업로드해 주세요.\n\n' +
          'JSON 파일을 다운로드하시겠습니까?';

        if (!window.confirm(message)) return;

        const blob = new Blob(
          [JSON.stringify(payload, null, 2)],
          { type: 'application/json;charset=utf-8' }
        );

        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'guest-data.json';

        document.body.appendChild(link);
        link.click();
        link.remove();

        setTimeout(() => URL.revokeObjectURL(url), 30000);

      } catch (error) {
        alert(
          '게스트 JSON 생성 실패:\n' +
          (error?.message || String(error))
        );
      } finally {
        button.disabled = false;
        button.textContent = originalText;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
