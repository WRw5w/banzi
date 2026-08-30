#!/usr/bin/env python3
"""Serve a searchable, copy-friendly view of the authoritative TeX listings."""

from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import urlsplit

import audit_listing_coverage as coverage


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>算法板子复制器</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17211b;
      --muted: #64716a;
      --paper: #f3f0e8;
      --card: #fffdf7;
      --line: #d9d4c7;
      --accent: #146b4a;
      --accent-soft: #dfeee6;
      --code: #16211c;
      --code-ink: #edf5ef;
      --shadow: 0 12px 34px rgba(44, 51, 46, .09);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(circle at 12% -10%, #d9eadf 0, transparent 34rem),
        var(--paper);
      color: var(--ink);
      font-family: Inter, "Segoe UI", "Microsoft YaHei", sans-serif;
    }
    header {
      position: sticky;
      top: 0;
      z-index: 10;
      padding: 22px max(24px, calc((100vw - 1280px) / 2));
      border-bottom: 1px solid rgba(89, 101, 94, .18);
      background: rgba(243, 240, 232, .92);
      backdrop-filter: blur(16px);
    }
    .title-row, .controls, .meta-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .title-row { justify-content: space-between; }
    h1 { margin: 0; font-size: clamp(24px, 3vw, 38px); letter-spacing: -.04em; }
    .subtitle { margin: 7px 0 18px; color: var(--muted); }
    .controls { flex-wrap: wrap; }
    input, select, button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--card);
      color: var(--ink);
      font: inherit;
    }
    input { flex: 1 1 420px; padding: 0 14px; }
    select { flex: 0 1 270px; padding: 0 12px; }
    button { padding: 0 14px; cursor: pointer; font-weight: 650; }
    button:hover { border-color: var(--accent); }
    button.primary { background: var(--accent); color: white; border-color: var(--accent); }
    main { width: min(1280px, calc(100% - 32px)); margin: 24px auto 70px; }
    .summary { margin: 0 0 16px; color: var(--muted); }
    .grid { display: grid; gap: 16px; }
    article {
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: var(--card);
      box-shadow: var(--shadow);
    }
    .card-head { padding: 16px 18px 13px; }
    .card-title { margin: 0; font-size: 17px; line-height: 1.45; }
    .meta-row { flex-wrap: wrap; margin-top: 8px; color: var(--muted); font-size: 13px; }
    .badge {
      padding: 3px 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 750;
    }
    .copy { margin-left: auto; min-height: 34px; }
    pre {
      max-height: 520px;
      margin: 0;
      padding: 18px;
      overflow: auto;
      border-top: 1px solid #26352e;
      background: var(--code);
      color: var(--code-ink);
      font: 13.5px/1.6 "Cascadia Code", "JetBrains Mono", Consolas, monospace;
      tab-size: 4;
      white-space: pre;
    }
    .empty {
      padding: 60px 24px;
      text-align: center;
      border: 1px dashed var(--line);
      border-radius: 15px;
      color: var(--muted);
    }
    .error { color: #9b2c2c; }
    kbd { padding: 2px 6px; border: 1px solid var(--line); border-radius: 5px; background: white; }
    @media (max-width: 680px) {
      header { padding: 16px; }
      main { width: min(100% - 20px, 1280px); margin-top: 14px; }
      .title-row { align-items: flex-start; }
      .copy { width: 100%; margin-left: 0; }
      pre { font-size: 12px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="title-row">
      <h1>算法板子复制器</h1>
      <button id="refresh" type="button">刷新源码</button>
    </div>
    <p class="subtitle">实时读取唯一 TeX 章节源。按 <kbd>/</kbd> 聚焦搜索，点击按钮复制完整代码块。</p>
    <div class="controls">
      <input id="search" type="search" placeholder="搜索：快速幂、qpow、线段树、最短路……" autocomplete="off">
      <select id="chapter" aria-label="按章节筛选"><option value="">全部章节</option></select>
      <select id="category" aria-label="按验证类别筛选"><option value="">全部类别</option></select>
    </div>
  </header>
  <main>
    <p id="summary" class="summary">正在读取正式板子……</p>
    <div id="results" class="grid"></div>
  </main>
  <script>
    const state = { snippets: [], query: "", chapter: "", category: "" };
    const search = document.querySelector("#search");
    const chapter = document.querySelector("#chapter");
    const category = document.querySelector("#category");
    const results = document.querySelector("#results");
    const summary = document.querySelector("#summary");

    function option(value, label) {
      const node = document.createElement("option");
      node.value = value;
      node.textContent = label;
      return node;
    }

    function searchable(item) {
      return `${item.title}\n${item.source}\n${item.category}\n${item.code}`.toLocaleLowerCase("zh-CN");
    }

    function filtered() {
      const terms = state.query.trim().toLocaleLowerCase("zh-CN").split(/\s+/).filter(Boolean);
      return state.snippets.filter(item => {
        if (state.chapter && item.chapter !== state.chapter) return false;
        if (state.category && item.category !== state.category) return false;
        const haystack = searchable(item);
        return terms.every(term => haystack.includes(term));
      });
    }

    function fallbackCopy(text) {
      const area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.append(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }

    async function copyCode(button, code) {
      try {
        if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(code);
        else fallbackCopy(code);
        const old = button.textContent;
        button.textContent = "已复制";
        button.classList.add("primary");
        setTimeout(() => { button.textContent = old; button.classList.remove("primary"); }, 1200);
      } catch (error) {
        fallbackCopy(code);
      }
    }

    function render() {
      const items = filtered();
      summary.textContent = `显示 ${items.length} / ${state.snippets.length} 个代码块；数据直接来自当前正式 TeX 渲染树。`;
      results.replaceChildren();
      if (!items.length) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "没有匹配的代码块，请换一个关键词或清除筛选。";
        results.append(empty);
        return;
      }
      const fragment = document.createDocumentFragment();
      for (const item of items) {
        const card = document.createElement("article");
        card.id = item.id;
        const head = document.createElement("div");
        head.className = "card-head";
        const title = document.createElement("h2");
        title.className = "card-title";
        title.textContent = item.title;
        const meta = document.createElement("div");
        meta.className = "meta-row";
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = item.category;
        const location = document.createElement("span");
        location.textContent = `${item.source}:${item.line}`;
        const copy = document.createElement("button");
        copy.className = "copy";
        copy.type = "button";
        copy.textContent = "复制代码";
        copy.addEventListener("click", () => copyCode(copy, item.code));
        meta.append(badge, location, copy);
        head.append(title, meta);
        const pre = document.createElement("pre");
        const code = document.createElement("code");
        code.textContent = item.code;
        pre.append(code);
        card.append(head, pre);
        fragment.append(card);
      }
      results.append(fragment);
    }

    async function load() {
      summary.textContent = "正在读取正式板子……";
      try {
        const response = await fetch("/api/snippets", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        state.snippets = data.snippets;
        const selectedChapter = chapter.value;
        const selectedCategory = category.value;
        chapter.replaceChildren(option("", "全部章节"));
        category.replaceChildren(option("", "全部类别"));
        for (const value of [...new Set(data.snippets.map(x => x.chapter))]) chapter.append(option(value, value));
        for (const value of [...new Set(data.snippets.map(x => x.category))].sort()) category.append(option(value, value));
        chapter.value = selectedChapter;
        category.value = selectedCategory;
        state.chapter = chapter.value;
        state.category = category.value;
        render();
      } catch (error) {
        summary.className = "summary error";
        summary.textContent = `读取失败：${error.message}`;
      }
    }

    search.addEventListener("input", () => { state.query = search.value; render(); });
    chapter.addEventListener("change", () => { state.chapter = chapter.value; render(); });
    category.addEventListener("change", () => { state.category = category.value; render(); });
    document.querySelector("#refresh").addEventListener("click", load);
    document.addEventListener("keydown", event => {
      if (event.key === "/" && document.activeElement !== search) { event.preventDefault(); search.focus(); }
      if (event.key === "Escape") { search.value = ""; state.query = ""; render(); search.blur(); }
    });
    load();
  </script>
</body>
</html>
"""


def build_catalog() -> dict[str, Any]:
    """Build the browser payload from the same formal tree used by coverage gates."""
    listings, sources = coverage.inventory_formal_tree()
    coverage.apply_differential_cases(listings)
    coverage.apply_contract_cases(listings)
    coverage.apply_explicit_classifications(listings)
    snippets = []
    for listing in listings:
        chapter = listing.headings.get("chapter") or "入口与速查"
        snippets.append(
            {
                "id": listing.block_id,
                "title": listing.heading,
                "chapter": chapter,
                "category": coverage.STATUS_LABELS[listing.category],
                "source": listing.source,
                "line": listing.line,
                "code": listing.body,
            }
        )
    return {
        "source_count": len(sources),
        "snippet_count": len(snippets),
        "snippets": snippets,
    }


def make_handler(
    catalog_builder: Callable[[], dict[str, Any]] = build_catalog,
) -> type[BaseHTTPRequestHandler]:
    class SnippetHandler(BaseHTTPRequestHandler):
        server_version = "BanziSnippetPicker/1.0"

        def send_bytes(self, status: int, content_type: str, payload: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urlsplit(self.path).path
            if path == "/":
                self.send_bytes(200, "text/html; charset=utf-8", INDEX_HTML.encode())
                return
            if path == "/api/snippets":
                try:
                    payload = json.dumps(
                        catalog_builder(), ensure_ascii=False, separators=(",", ":")
                    ).encode("utf-8")
                except (OSError, ValueError, KeyError) as exc:
                    payload = json.dumps(
                        {"error": str(exc)}, ensure_ascii=False
                    ).encode("utf-8")
                    self.send_bytes(500, "application/json; charset=utf-8", payload)
                    return
                self.send_bytes(200, "application/json; charset=utf-8", payload)
                return
            self.send_bytes(404, "text/plain; charset=utf-8", "Not found\n".encode())

    return SnippetHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认仅本机")
    parser.add_argument("--port", type=int, default=8765, help="监听端口，默认 8765")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 <= args.port <= 65535:
        raise SystemExit("--port must be between 0 and 65535")
    server = ThreadingHTTPServer((args.host, args.port), make_handler())
    host, port = server.server_address[:2]
    url_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{url_host}:{port}/"
    print(f"板子复制器已启动：{url}", flush=True)
    print("按 Ctrl+C 停止；点击“刷新源码”可重新读取当前 TeX。", flush=True)
    if not args.no_open:
        threading.Timer(0.35, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
