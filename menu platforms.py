# 추가 작업 (menu-platforms-20261123)
# 1) 햄버거 메뉴: 사이트 설정(폰트·API) 팝업을 열어도 메뉴가 닫히지 않고, 팝업이 열린 동안만 비활성화 → 팝업을 닫으면 이어서 사용
# 2) 플랫폼 추가: YouTube · 네이버 블로그 (관리자·게스트 화면, 폰트 설정의 플랫폼 선택 포함). 하위 화면은 Twitter(X)와 같은 폴더 구조
# 사용: 사이트 폴더에서 python3 menu_platforms.py   (이미 적용되어 있으면 아무것도 바꾸지 않음)
import pathlib, shutil, sys, datetime

MARK = 'menu-platforms-20261123'
files = {n: pathlib.Path(n) for n in ['index.html', 'guest-app.html', 'guest.html', 'archive-menu.js',
                                     'api-settings.js', 'font-settings.js', 'guest-font-settings.js']}
text = {n: p.read_text(encoding='utf-8') for n, p in files.items()}
if MARK in text['archive-menu.js']:
    sys.exit('이미 적용되어 있습니다. 변경 없음.')


def rep(name, old, new, count=1):
    s = text[name]
    assert s.count(old) == count, f'{name}: 바꿀 위치를 찾지 못함 → {old[:60]}'
    text[name] = s.replace(old, new)


# ── 1) 메뉴가 저절로 닫히던 코드 3곳 제거 ──────────────────────────────
rep('archive-menu.js', """    // Close the mobile menu before opening Font Settings.
    drawer.addEventListener('click', event => {
      if (event.target.closest('#fontSettingsBtn')) {
        setOpen(false);
      }
    }, true);
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !drawer.hidden) setOpen(false);
    });""",
    """    // menu-platforms-20261123: 설정 팝업이 열려 있는 동안 메뉴는 닫지 않고 비활성화만 함
    const popupOpen = () => Boolean(document.querySelector('#modalRoot .overlay') || document.getElementById('cbhApiOverlay'));
    const syncInactive = () => {
      const inactive = !drawer.hidden && popupOpen();
      drawer.classList.toggle('archive-menu-inactive', inactive);
      if (inactive) drawer.setAttribute('inert', '');
      else drawer.removeAttribute('inert');
    };
    new MutationObserver(syncInactive).observe(document.body, {childList: true});
    const modalRoot = document.getElementById('modalRoot');
    if (modalRoot) new MutationObserver(syncInactive).observe(modalRoot, {childList: true});
    new MutationObserver(syncInactive).observe(drawer, {attributes: true, attributeFilter: ['hidden']});
    // Esc: 팝업이 열려 있으면 팝업만 닫히고 메뉴는 유지 (팝업 처리보다 먼저 상태 확인)
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !drawer.hidden && !popupOpen()) setOpen(false);
    }, true);""")
rep('archive-menu.js', ".archive-menu-backdrop[hidden],.archive-menu-drawer[hidden]{display:none!important}",
    ".archive-menu-backdrop[hidden],.archive-menu-drawer[hidden]{display:none!important}"
    ".archive-menu-drawer.archive-menu-inactive{opacity:.55;pointer-events:none;filter:grayscale(.3);transition:opacity .15s}"
    "@media(max-width:650px){html body.archive-menu-open .cbh-api-overlay{right:0!important;z-index:11020!important}"
    "html body.archive-menu-open .cbh-api-panel{max-width:calc(100vw - 28px)!important}}")
rep('api-settings.js', """ const drawer = document.getElementById('archiveMenuDrawer');
if (drawer && !drawer.hidden) {
  drawer.querySelector('.archive-menu-close')?.click();
}
""", " // menu-platforms-20261123: 메뉴를 닫지 않음 (팝업이 열린 동안 메뉴는 비활성화)\n")
rep('font-settings.js', """ const drawer=document.getElementById('archiveMenuDrawer');
 if(drawer && !drawer.hidden){
   drawer.querySelector('.archive-menu-close')?.click();
 }
""", " // menu-platforms-20261123: 메뉴를 닫지 않음 (팝업이 열린 동안 메뉴는 비활성화)\n")

# ── 2) 플랫폼 추가: YouTube · 네이버 블로그 ─────────────────────────────
OLD_P = "const platforms={instagram:{name:'Instagram',glyph:'◎'},twitter:{name:'Twitter (X)',glyph:'𝕏'}};"
NEW_P = ("const platforms={instagram:{name:'Instagram',glyph:'◎'},twitter:{name:'Twitter (X)',glyph:'𝕏'},"
         "youtube:{name:'YouTube',glyph:'▶'},naverblog:{name:'네이버 블로그',glyph:'N'}};")
OLD_TAG = "p.platform==='instagram'?'INSTAGRAM':p.platform==='twitter'?'TWITTER (X)':"
NEW_TAG = OLD_TAG + "p.platform==='youtube'?'YOUTUBE':p.platform==='naverblog'?'NAVER BLOG':"
OLD_URL = "if(platform==='twitter'&&/^[a-zA-Z0-9_]{1,15}$/.test(h))return 'https://x.com/'+encodeURIComponent(h);"
NEW_URL = (OLD_URL + "if(platform==='youtube'&&/^[a-zA-Z0-9._-]{3,30}$/.test(h))return 'https://www.youtube.com/@'+encodeURIComponent(h);"
           "if(platform==='naverblog'&&/^[a-zA-Z0-9_-]{2,30}$/.test(h))return 'https://blog.naver.com/'+encodeURIComponent(h);")
for n in ['index.html', 'guest-app.html']:
    rep(n, OLD_P, NEW_P)
    rep(n, OLD_TAG, NEW_TAG)
    rep(n, OLD_URL, NEW_URL)

OLD_OPT = '<option value="twitter">X</option>'
NEW_OPT = OLD_OPT + '<option value="youtube">YouTube</option><option value="naverblog">네이버 블로그</option>'
for n in ['guest.html', 'font-settings.js', 'guest-font-settings.js']:
    rep(n, OLD_OPT, NEW_OPT)
OLD_LBL = "esc(f.platform==='instagram'?'Instagram':'X')"
NEW_LBL = "esc(({instagram:'Instagram',twitter:'X',youtube:'YouTube',naverblog:'네이버 블로그'})[f.platform]||f.platform)"
for n in ['font-settings.js', 'guest-font-settings.js']:
    rep(n, OLD_LBL, NEW_LBL)

# ── 바뀐 스크립트를 브라우저가 새로 받도록 버전 표시 변경 ──────────────────
rep('index.html', './font-settings.js?v=font-modal-layer-fix-v2', './font-settings.js?v=menu-platforms-20261123')
rep('index.html', './api-settings.js?v=api-key-only-04', './api-settings.js?v=menu-platforms-20261123')
rep('index.html', './archive-menu.js?v=menu-20261123-folder-create', './archive-menu.js?v=menu-platforms-20261123')
rep('guest-app.html', './guest-font-settings.js?v=1', './guest-font-settings.js?v=menu-platforms-20261123')
rep('guest-app.html', './archive-menu.js?v=menu-20261121-01', './archive-menu.js?v=menu-platforms-20261123')

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
for n, p in files.items():
    shutil.copy(p, f'{n}.before-menu-platforms-{stamp}.bak')
    p.write_text(text[n], encoding='utf-8')
print(f'적용 완료: 파일 {len(files)}개 수정 (백업 파일 {len(files)}개 생성)')
