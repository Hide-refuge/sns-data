# 상위 폴더 생성: 오른쪽 상시 블록 → 상단 '+ 폴더 생성' 버튼 + 중앙 팝업 (top-folder-create-modal-v1)
# + 모바일 버튼 정렬·높이 통일 (top-folder-create-mobile-v1). 이미 적용된 부분은 건너뜁니다.
import pathlib, sys, shutil, datetime
root = pathlib.Path('.')
idx, menu = root / 'index.html', root / 'archive-menu.js'
s, m = idx.read_text(encoding='utf-8'), menu.read_text(encoding='utf-8')
need_v1 = 'top-folder-create-modal-v1' not in s
need_mobile = 'top-folder-create-mobile-v1' not in s
if not (need_v1 or need_mobile):
    sys.exit('이미 모두 적용되어 있습니다. 변경 없음.')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy(idx, f'index.html.before-top-folder-modal-{stamp}.bak')
shutil.copy(menu, f'archive-menu.js.before-top-folder-modal-{stamp}.bak')

if need_v1:
    # 1) 플랫폼 폴더 화면의 오른쪽 '+ 새 폴더' 블록 제거 (폴더 목록만 표시)
    a = s.index('<div class="split"><div>${fs.length?')
    b = s.index('</aside></div>', a) + len('</aside></div>')
    seg = s[a:b]
    grid = seg[seg.index('${fs.length?'):seg.index("</div>'}</div><aside") + len("</div>'}")]
    grid = grid.replace('아직 폴더가 없습니다. 오른쪽에서 만들어 보세요.', '아직 폴더가 없습니다. 상단의 + 폴더 생성 버튼으로 만들어 보세요.')
    s = s[:a] + '<div class="folder-list-wrap">' + grid + '</div>' + s[b:]

    # 2) 화면이 바뀔 때마다 상단 버튼 표시 여부 갱신
    old = 'function render(){queueMicrotask(()=>window.scrapFontApply?.());'
    assert s.count(old) == 1, 'render 위치를 찾지 못함'
    s = s.replace(old, old + 'queueMicrotask(syncFolderCreateButton);')

    # 3) 팝업에서 저장하면 저장 완료 후 팝업 닫기 (기존 저장 로직 그대로)
    old = "await put('folders',{id:uid(),platform:route.platform,parentId:route.folder||null,name,description,...style,createdAt:today()});await refresh()});"
    assert s.count(old) == 1, '폴더 저장 로직 위치를 찾지 못함'
    s = s.replace(old, "const inModal=Boolean(e.target.closest('#modalRoot'));" + old.replace('await refresh()});', 'await refresh();if(inModal)closeModal()});'))

    # 4) 상단 버튼 + 중앙 팝업 (기존 입력 항목: 폴더명·테두리 색상·아이콘·설명)
    block = r'''// top-folder-create-modal-v1: 상위 폴더 생성을 상단 버튼 + 중앙 팝업으로 전환
function syncFolderCreateButton(){
  const show=Boolean(route.platform&&!route.folder);
  let btn=document.getElementById('openFolderCreate');
  if(!show){if(btn)btn.remove();return}
  const actions=document.querySelector('header.top .actions');
  if(!actions)return;
  if(!btn){btn=document.createElement('button');btn.type='button';btn.id='openFolderCreate';btn.className='btn primary';btn.textContent='+ 폴더 생성'}
  const toggle=document.getElementById('archiveMenuToggle');
  if(toggle&&toggle.parentElement===actions){if(btn.nextElementSibling!==toggle)actions.insertBefore(btn,toggle)}
  else if(btn.parentElement!==actions)actions.appendChild(btn);
}
function openFolderCreateModal(){
  if(!route.platform||route.folder)return;
  modal(`<h2>새 폴더 생성</h2><form id="folderForm"><div class="field"><label for="folderName">폴더명 / 정보 종류</label><input id="folderName" maxlength="70" required placeholder="예: 디자인 레퍼런스"></div>${folderStyleFields()}<div class="field"><label for="folderDesc">설정 정보 메모</label><textarea id="folderDesc" placeholder="이 폴더에 저장할 자료의 기준"></textarea></div><div class="actions" style="justify-content:flex-end"><button class="btn" type="button" data-close>취소</button><button class="btn primary" type="submit">폴더 생성</button></div></form>`);
  initFolderStyleControls($('modalRoot'));
  setTimeout(()=>$('folderName')?.focus(),0);
}
document.addEventListener('click',e=>{if(e.target.closest('#openFolderCreate'))openFolderCreateModal()});
'''
    anchor = '// subfolder-modal-button-v1\n'
    assert s.count(anchor) == 1, '하위 폴더 팝업 코드 위치를 찾지 못함'
    s = s.replace(anchor, block + anchor)

    # 5) 메뉴 스크립트 새 버전 불러오기 (브라우저 캐시 방지)
    old = './archive-menu.js?v=menu-20261121-01'
    assert s.count(old) == 1, 'archive-menu.js 스크립트 태그를 찾지 못함'
    s = s.replace(old, './archive-menu.js?v=menu-20261123-folder-create')

    # 6) 햄버거 메뉴가 새 버튼을 메뉴 안으로 옮기지 않도록 예외 추가
    old = "      if (el === toggle || el.tagName === 'INPUT') return;"
    assert m.count(old) == 1, 'archive-menu.js 이동 규칙을 찾지 못함'
    m = m.replace(old, old + "\n      // top-folder-create-modal-v1: 상단 '+ 폴더 생성' 버튼은 헤더에 유지\n      if (el.id === 'openFolderCreate') return;")


# 7) 모바일: '+ 폴더 생성' 왼쪽 끝, ☰ 오른쪽 끝, 두 버튼 높이 42px 통일
if need_mobile:
    css = """<!-- top-folder-create-mobile-v1 -->
<style>
@media (max-width:760px){
  header.top .actions{width:100%;display:flex;align-items:center;justify-content:space-between;flex-wrap:nowrap;gap:10px}
  header.top .actions #openFolderCreate,
  header.top .actions #archiveMenuToggle{height:42px!important;min-height:42px!important;padding-top:0!important;padding-bottom:0!important;box-sizing:border-box!important}
  header.top .actions #openFolderCreate{display:inline-flex;align-items:center;justify-content:center;font-size:14px;line-height:1;padding-left:16px;padding-right:16px;white-space:nowrap}
  header.top .actions #archiveMenuToggle{margin-left:auto}
}
</style>
"""
    assert s.count('</head>') == 1, '</head> 위치를 찾지 못함'
    s = s.replace('</head>', css + '</head>')

idx.write_text(s, encoding='utf-8'); menu.write_text(m, encoding='utf-8')
print('적용 완료:', '상단 버튼·팝업' if need_v1 else '', '모바일 버튼 정렬·높이' if need_mobile else '', '(백업 파일 2개 생성)')
