#!/usr/bin/env python3
"""Generate index.html — lists all .html files in the repository root."""

import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Collect .html files (exclude index.html itself)
html_files = sorted(
    f for f in os.listdir(ROOT)
    if f.endswith(".html") and f != "index.html"
)

now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

items = "\n".join(
    f'      <li><a href="{f}">{f}</a></li>'
    for f in html_files
)

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ファイル一覧</title>
<style>
  body {{
    font-family: system-ui, -apple-system, "Hiragino Sans", "Yu Gothic UI", sans-serif;
    background: #15171c;
    color: #eceef3;
    margin: 0;
    padding: 40px 24px;
  }}
  h1 {{ font-size: 20px; margin: 0 0 8px; }}
  p.updated {{ font-size: 12px; color: #8c95a6; margin: 0 0 28px; }}
  ul {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 480px;
  }}
  li a {{
    display: block;
    background: #20242c;
    border: 1px solid #323845;
    border-radius: 10px;
    padding: 12px 16px;
    color: #4da3ff;
    text-decoration: none;
    font-size: 15px;
    transition: border-color .15s;
  }}
  li a:hover {{ border-color: #4da3ff; }}
</style>
</head>
<body>
<h1>ファイル一覧</h1>
<p class="updated">最終更新: {now}</p>
<ul>
{items}
</ul>
</body>
</html>
"""

out = os.path.join(ROOT, "index.html")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print(f"Generated index.html with {len(html_files)} file(s): {html_files}")
