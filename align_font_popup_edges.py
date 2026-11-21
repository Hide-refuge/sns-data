#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import shutil
path = Path(__file__).resolve().parent / "archive-menu.js"
if not path.exists():
    raise SystemExit("archive-menu.js 파일이 같은 폴더에 없습니다.")
source = path.read_text(encoding="utf-8")
if "FONT_DIALOG_EDGE_ALIGN_V1" in source:
    raise SystemExit("이미 적용된 패치입니다.")
anchor = "\n})();"
if anchor not in source:
    raise SystemExit("예상한 코드 구조가 아닙니다. 변경하지 않았습니다.")
backup = path.with_name("archive-menu.js.backup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
shutil.copy2(path, backup)
addition = "\n  /* FONT_DIALOG_EDGE_ALIGN_V1 */\n  (() => {\n    function align() {\n      const dialog = document.querySelector('#modalRoot .font-dialog');\n      const first = dialog?.querySelector('#font-tab-button-1');\n      const third = dialog?.querySelector('#font-tab-button-3');\n      const close = dialog?.querySelector('.font-head [data-close]');\n      if (!first || !third || !close) return;\n      const d = dialog.getBoundingClientRect();\n      const a = first.getBoundingClientRect();\n      const b = third.getBoundingClientRect();\n      if (!d.width || !a.width || !b.width) return;\n      const left = a.left - d.left;\n      const width = Math.ceil(b.right - a.left + 2 * left);\n      if (width < 320) return;\n      dialog.style.setProperty('box-sizing', 'border-box', 'important');\n      dialog.style.setProperty('width', 'min(' + width + 'px, 96vw)', 'important');\n      dialog.style.setProperty('max-width', '96vw', 'important');\n      close.style.setProperty('margin-right', '0', 'important');\n    }\n    let pending = false;\n    function schedule() {\n      if (pending) return;\n      pending = true;\n      requestAnimationFrame(() => { pending = false; align(); });\n    }\n    function start() {\n      const root = document.getElementById('modalRoot');\n      if (root) new MutationObserver(schedule).observe(root, {childList:true});\n      schedule();\n    }\n    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);\n    else start();\n    window.addEventListener('resize', schedule);\n  })();\n"
path.write_text(source.replace(anchor, "\n" + addition + anchor, 1), encoding="utf-8")
print("완료: archive-menu.js 수정 / 백업:", backup.name)
