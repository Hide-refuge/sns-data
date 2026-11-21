#!/usr/bin/env python3
"""Arrange existing archive drawer controls on individual rows without replacing handlers."""
from pathlib import Path
from datetime import datetime
import shutil
file = Path(__file__).resolve().parent / "archive-menu.js"
if not file.is_file():
    raise SystemExit("archive-menu.js 파일이 없습니다. 같은 폴더에 업로드해 주세요.")
source = file.read_text(encoding="utf-8")
marker = "ARCHIVE_MENU_ONE_BUTTON_PER_ROW_V1"
if marker in source:
    raise SystemExit("이미 적용된 패치입니다.")
if "archiveMenuDrawer" not in source:
    raise SystemExit("예상한 햄버거 메뉴 코드가 없습니다. 수정하지 않았습니다.")
anchor = "\n})();"
if anchor not in source:
    raise SystemExit("파일 구조가 예상과 다릅니다. 수정하지 않았습니다.")
backup = file.with_name("archive-menu.js.before-row-layout-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".bak")
shutil.copy2(file, backup)
addition = '\n  /* ARCHIVE_MENU_ONE_BUTTON_PER_ROW_V1 */\n  (() => {\n    const style = document.createElement(\'style\');\n    style.textContent = `\n      .archive-menu-drawer .archive-menu-items,\n      .archive-menu-drawer #syncControls {\n        display:flex!important;\n        flex-direction:column!important;\n        flex-wrap:nowrap!important;\n        align-items:flex-start!important;\n        gap:8px!important;\n      }\n      .archive-menu-drawer .archive-menu-items > :is(button,a,[role="button"]),\n      .archive-menu-drawer #syncControls > :is(button,a,[role="button"]) {\n        display:inline-flex!important;\n        flex:0 0 auto!important;\n        width:max-content!important;\n        max-width:100%!important;\n        box-sizing:border-box!important;\n        white-space:normal!important;\n        text-align:left;\n      }\n      /* Other cloud actions, such as guest sign-in, remain on separate lines. */\n      .archive-menu-drawer #archiveMenuCloud #syncPanel button {\n        max-width:100%;\n        box-sizing:border-box;\n      }\n      .archive-menu-drawer #archiveMenuCloud #syncPanel button:not(#syncControls button) {\n        display:block;\n        margin-bottom:8px;\n      }\n      .archive-menu-drawer.archive-menu-compact {\n        padding-top:12px!important;\n        padding-bottom:12px!important;\n      }\n      .archive-menu-drawer.archive-menu-compact .archive-menu-heading {\n        margin-bottom:12px!important;\n      }\n      .archive-menu-drawer.archive-menu-compact .archive-menu-group {\n        padding-top:10px!important;\n        padding-bottom:10px!important;\n      }\n      .archive-menu-drawer.archive-menu-compact .archive-menu-items,\n      .archive-menu-drawer.archive-menu-compact #syncControls {\n        gap:5px!important;\n      }\n      .archive-menu-drawer.archive-menu-compact button {\n        padding-top:5px!important;\n        padding-bottom:5px!important;\n        font-size:0.94em!important;\n      }\n    `;\n    document.head.appendChild(style);\n    let scheduled = false;\n    const update = () => {\n      scheduled = false;\n      const drawer = document.getElementById(\'archiveMenuDrawer\');\n      if (!drawer || drawer.hidden) return;\n      drawer.classList.remove(\'archive-menu-compact\');\n      if (drawer.scrollHeight > drawer.clientHeight + 2) {\n        drawer.classList.add(\'archive-menu-compact\');\n      }\n    };\n    const schedule = () => {\n      if (scheduled) return;\n      scheduled = true;\n      requestAnimationFrame(update);\n    };\n    const start = () => {\n      const drawer = document.getElementById(\'archiveMenuDrawer\');\n      if (!drawer) return;\n      new MutationObserver(schedule).observe(drawer, {attributes:true, attributeFilter:[\'hidden\'], childList:true, subtree:true, characterData:true});\n      window.addEventListener(\'resize\', schedule);\n      schedule();\n    };\n    if (document.readyState === \'loading\') document.addEventListener(\'DOMContentLoaded\', start);\n    else start();\n  })();\n'
file.write_text(source.replace(anchor, "\n" + addition + anchor, 1), encoding="utf-8")
print("완료: 각 버튼 개별 행 배치, 높이 초과 시 버튼 간격/크기 소폭 축소")
print("백업 파일:", backup.name)
