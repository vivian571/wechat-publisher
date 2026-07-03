#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import html
import json
import sys
from pathlib import Path

import requests

PERMANENT_THUMB_MEDIA_IDS = [
    "r2SuJ--pe9hF_U34Ly0J_Gnfu0A3JcEW2sJjpR9EcK2FxIZRWyBXO37XXkQQRpOk",
    "r2SuJ--pe9hF_U34Ly0J_CqFWTjPqbEeJJm9BhB9dD-DLuxCPjAGF4wVY9QQsU1s",
    "r2SuJ--pe9hF_U34Ly0J_BfCZUmJEsU8Ii9UOVi68e_jFSrwTJDJdszw8TObD1nt",
]


def load_config(config_path: Path) -> tuple[str, str]:
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config["WeChat"]["APP_ID"], config["WeChat"]["APP_SECRET"]


def get_access_token(app_id: str, app_secret: str) -> str:
    url = "https://api.weixin.qq.com/cgi-bin/stable_token"
    payload = {
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret,
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "access_token" in data:
        return data["access_token"]

    fallback_url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    fallback_response = requests.get(fallback_url, timeout=30)
    fallback_response.raise_for_status()
    fallback_data = fallback_response.json()
    if "access_token" not in fallback_data:
        raise RuntimeError(json.dumps(fallback_data, ensure_ascii=False))
    return fallback_data["access_token"]


def extract_title_and_html(md_path: Path) -> tuple[str, str]:
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    title = md_path.stem
    html_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            html_lines.append(f"<h1>{html.escape(title)}</h1>")
            continue
        if line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
            continue
        escaped = html.escape(line).replace("**", "")
        html_lines.append(f"<p>{escaped}</p>")

    article_html = """
<section style="font-size:16px;line-height:1.8;color:#222;">
%s
</section>
""" % "\n".join(html_lines)
    return truncate_title(title), article_html


def truncate_title(title: str, max_bytes: int = 64) -> str:
    encoded = title.encode("utf-8")
    if len(encoded) <= max_bytes:
        return title
    result = []
    current = 0
    for ch in title:
        size = len(ch.encode("utf-8"))
        if current + size > max_bytes:
            break
        result.append(ch)
        current += size
    return "".join(result)


def upload_draft(access_token: str, title: str, content: str, author: str) -> dict:
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    payload = {
        "articles": [
            {
                "title": title,
                "author": author,
                "digest": "",
                "content": content,
                "content_source_url": "",
                "thumb_media_id": PERMANENT_THUMB_MEDIA_IDS[0],
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: publish_simple_wechat.py <markdown_path> [author]")
        return 1

    md_path = Path(sys.argv[1]).expanduser().resolve()
    author = sys.argv[2] if len(sys.argv) > 2 else "AI助手"
    if not md_path.exists():
        print(f"Markdown not found: {md_path}")
        return 1

    app_id, app_secret = load_config(Path(__file__).with_name("config.ini"))
    title, content = extract_title_and_html(md_path)
    access_token = get_access_token(app_id, app_secret)
    result = upload_draft(access_token, title, content, author)
    print(json.dumps({"title": title, "result": result}, ensure_ascii=False))
    return 0 if result.get("errcode", 0) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
