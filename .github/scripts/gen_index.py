#!/usr/bin/env python3
"""Generate index.html — lists all .html files in the repository root with titles and descriptions."""

import os
import re
import json
import datetime
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESCRIPTIONS_FILE = os.path.join(ROOT, "descriptions.json")

class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self._in_title = False
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = True
        elif tag_lower == "meta":
            attr_dict = {k.lower(): v for k, v in attrs if v is not None}
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            if (name == "description" or prop == "og:description") and not self.description:
                self.description = attr_dict.get("content", "").strip()

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False
            self.title = "".join(self._title_parts).strip()

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)


# 1. 外部 descriptions.json の読み込み（存在する場合）
external_meta = {}
if os.path.exists(DESCRIPTIONS_FILE):
    try:
        with open(DESCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            external_meta = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load descriptions.json: {e}")

# 2. 対象 HTML ファイルの収集（index.html は除外）
html_files = sorted(
    f for f in os.listdir(ROOT)
    if f.endswith(".html") and f != "index.html"
)

# 3. 各 HTML ファイルのメタデータ取得
cards_data = []
for fname in html_files:
    fpath = os.path.join(ROOT, fname)
    title = ""
    description = ""

    # HTML のパース
    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(65536) # 先頭 64KB を対象
        parser = MetaExtractor()
        parser.feed(content)
        title = parser.title
        description = parser.description
    except Exception as e:
        print(f"Warning: Failed to parse {fname}: {e}")

    # descriptions.json による補完／設定
    ext_entry = external_meta.get(fname, {})
    if isinstance(ext_entry, str):
        # 文字列だけの場合は description として扱う
        if not description:
            description = ext_entry
    elif isinstance(ext_entry, dict):
        if ext_entry.get("title"):
            title = ext_entry["title"]
        if ext_entry.get("description"):
            description = ext_entry["description"]

    # フォールバック
    if not title:
        title = fname

    cards_data.append({
        "file": fname,
        "title": title,
        "description": description
    })

now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# 4. カード HTML 生成
cards_html_list = []
for c in cards_data:
    desc_html = f'<p class="card-desc">{c["description"]}</p>' if c["description"] else '<p class="card-desc empty">説明はありません</p>'
    cards_html_list.append(f"""    <a class="card" href="{c['file']}">
      <div class="card-top">
        <span class="card-file">{c['file']}</span>
        <span class="card-arrow">&rarr;</span>
      </div>
      <div class="card-title">{c['title']}</div>
      {desc_html}
    </a>""")

cards_html = "\n".join(cards_html_list)

# 5. 全体 HTML（playMIDI.html と同一のデザインシステム）
html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pondashi — Tools Index</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #fff;
      color: #000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 24px;
      display: flex;
      justify-content: center;
    }}
    .app {{
      width: 100%;
      max-width: 960px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .panel {{
      background: #fff;
      border: 1px solid #000;
      padding: 14px 16px;
    }}
    .panel-header {{
      font-size: 12px;
      font-weight: 700;
      color: #000;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .header-row {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-end;
      gap: 12px;
    }}
    h1 {{
      font-size: 18px;
      font-weight: 700;
      color: #000;
      letter-spacing: -0.01em;
    }}
    .val-display {{
      font-size: 12px;
      color: #000;
      font-variant-numeric: tabular-nums;
    }}
    .search-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    label {{
      font-size: 12px;
      color: #000;
      text-transform: uppercase;
      font-weight: 600;
    }}
    input[type=text] {{
      background: #fff;
      color: #000;
      border: 1px solid #000;
      font: inherit;
      font-size: 12px;
      padding: 5px 8px;
      width: 220px;
      outline: none;
    }}
    input[type=text]:focus {{
      background: #f5f5f5;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 12px;
    }}
    .card {{
      background: #fff;
      color: #000;
      border: 1px solid #000;
      padding: 14px 16px;
      text-decoration: none;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      transition: background 0.12s, color 0.12s;
      cursor: pointer;
    }}
    .card:hover {{
      background: #000;
      color: #fff;
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}
    .card-file {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 11px;
      border: 1px solid currentColor;
      padding: 2px 6px;
    }}
    .card-arrow {{
      font-size: 14px;
      font-weight: 700;
      transition: transform 0.12s;
    }}
    .card:hover .card-arrow {{
      transform: translateX(3px);
    }}
    .card-title {{
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.35;
    }}
    .card-desc {{
      font-size: 12px;
      line-height: 1.5;
      opacity: 0.85;
      word-break: break-word;
    }}
    .card-desc.empty {{
      opacity: 0.4;
      font-style: italic;
    }}
    .footer-panel {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #000;
      font-variant-numeric: tabular-nums;
    }}
    @media (max-width: 600px) {{
      body {{ padding: 16px; }}
      .grid {{ grid-template-columns: 1fr; }}
      input[type=text] {{ width: 100%; }}
      .header-row {{ flex-direction: column; align-items: stretch; }}
    }}
  </style>
</head>
<body>
<div class="app">
  <div class="panel">
    <div class="panel-header">
      <span>REPOSITORY DIRECTORY</span>
      <span class="val-display">{len(html_files)} FILES</span>
    </div>
    <div class="header-row">
      <div>
        <h1>Pondashi Web Tools</h1>
      </div>
      <div class="search-wrap">
        <label for="search">Filter:</label>
        <input type="text" id="search" placeholder="Search by name or keyword..." autocomplete="off">
      </div>
    </div>
  </div>

  <div class="grid" id="cardGrid">
{cards_html}
  </div>

  <div class="panel footer-panel">
    <span>INDEX GENERATED</span>
    <span>{now}</span>
  </div>
</div>

<script>
  const searchInput = document.getElementById('search');
  const cards = document.querySelectorAll('.card');

  searchInput.addEventListener('input', (e) => {{
    const query = e.target.value.toLowerCase().trim();
    cards.forEach(card => {{
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(query) ? '' : 'none';
    }});
  }});
</script>
</body>
</html>
"""

out = os.path.join(ROOT, "index.html")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print(f"Generated index.html with {len(html_files)} file(s): {[c['file'] for c in cards_data]}")
