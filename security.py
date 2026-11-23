# 4단계 보안 정리 (security-20261123): 사용하지 않는 Supabase 외부 스크립트 제거
# - 버전이 고정되지 않은 외부 CDN 스크립트를 매번 불러오던 것을 없앰 (코드 어디에서도 사용하지 않음)
# 사용: 사이트 폴더에서 python3 apply_security_v1.py
import pathlib, shutil, sys, datetime
idx = pathlib.Path('index.html')
s = idx.read_text(encoding='utf-8')
tag = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>'
if tag not in s:
    sys.exit('이미 적용되어 있거나 대상이 없습니다. 변경 없음.')
assert s.count(tag) == 1
for f in pathlib.Path('.').glob('*.js'):
    t = f.read_text(encoding='utf-8', errors='ignore')
    assert 'createClient' not in t and 'window.supabase' not in t, f'{f.name}에서 Supabase를 사용 중 — 중단'
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy(idx, f'index.html.before-security-{stamp}.bak')
idx.write_text(s.replace(tag, '<!-- security-20261123: 사용하지 않는 Supabase 외부 스크립트 제거 -->'), encoding='utf-8')
print(f'적용 완료: Supabase 외부 스크립트 제거 (백업: index.html.before-security-{stamp}.bak)')
