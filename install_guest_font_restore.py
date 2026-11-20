#!/usr/bin/env python3
"""Safely install a public font settings export/import bridge. Never changes admin font data."""
from pathlib import Path
import shutil,sys
root=Path(__file__).resolve().parent
files=['index.html','guest-font-settings.js','guest-app.html']
for name in files:
    if not (root/name).is_file():sys.exit('필수 파일 없음: '+name+' (기존 동일 레이아웃 패치를 먼저 실행하세요)')
idx=(root/'index.html').read_text(encoding='utf8')
gf=(root/'guest-font-settings.js').read_text(encoding='utf8')
gh=(root/'guest-app.html').read_text(encoding='utf8')
mark='guest-font-public-export.js'
if mark not in idx:
    anchor='</body></html>'
    if idx.count(anchor)!=1:sys.exit('index.html 구조가 예상과 다릅니다. 변경 중단')
    idx=idx.replace(anchor,'<script src="./guest-font-public-export.js?v=1"></script>'+anchor,1)
# Import after module initialization: no localStorage or cloud access from guest.
needle='snapshot(state);rerender();setTimeout(reloadCloud,1300)'
replacement='''snapshot(state);rerender();setTimeout(reloadCloud,1300);
// PUBLIC_FONT_SNAPSHOT_V1: font metadata and saved rules, loaded from approved static file.
fetch('./guest-fonts.json',{cache:'no-store'}).then(async response=>{
 if(response.status===404)return null;
 if(!response.ok)throw Error('HTTP '+response.status);
 return response.json();
}).then(publicFonts=>{
 if(!publicFonts)return;
 if(!Array.isArray(publicFonts.fonts)||!Array.isArray(publicFonts.rules))throw Error('폰트 설정 형식 오류');
 state=sanitize(publicFonts);rerender();refreshFontLists();
}).catch(err=>console.warn('게스트 공개 폰트 설정 불러오기 실패:',err));'''
if 'PUBLIC_FONT_SNAPSHOT_V1' not in gf:
    if gf.count(needle)!=1:sys.exit('guest-font-settings.js 초기화 위치가 예상과 다릅니다. 변경 중단')
    gf=gf.replace(needle,replacement,1)
if 'guest-fonts.json' not in gh:
    anchor='</body>'
    if gh.count(anchor)!=1:sys.exit('guest-app.html 구조가 예상과 다릅니다. 변경 중단')
    gh=gh.replace(anchor,'''<script>
fetch('./guest-fonts.json',{method:'HEAD',cache:'no-store'}).then(r=>{
 if(r.status===404)console.info('게스트 폰트 정보는 아직 게시되지 않았습니다. 관리자 화면에서 폰트 설정 내보내기를 실행하세요.');
}).catch(()=>{});
</script></body>''',1)
new={'index.html':idx,'guest-font-settings.js':gf,'guest-app.html':gh}
for name,content in new.items():
    p=root/name
    if p.read_text(encoding='utf8')==content:continue
    backup=root/(name+'.before-guest-font-restore.bak')
    if not backup.exists():shutil.copy2(p,backup)
    p.write_text(content,encoding='utf8')
source=Path(__file__).with_name('guest-font-public-export.js')
if not source.is_file():sys.exit('guest-font-public-export.js 파일이 없습니다')
target=root/source.name
if source.resolve()!=target.resolve():shutil.copy2(source,target)
print('완료: 기존 관리자 폰트 설정을 변경하지 않았습니다.')
print('관리자 페이지 새로고침 → 게스트 폰트 내보내기 → 다운로드된 guest-fonts.json을 개발 브랜치 최상위 폴더에 업로드하세요.')
