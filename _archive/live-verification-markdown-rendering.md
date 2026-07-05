---
doc_id: allincms-archive-live-verification-markdown
title: 【归档】live-verification 的 markdown 渲染实测段
description: mysite01 站 2026-06-29 的 markdown-residue / frontend batch audit 实测明细;2026-07-04 移出(结论已固化到 field-contract/batch-verification/INV-4/validate_slate_content_shape),此为原始明细供快速恢复
layer: ops
status: final
created: 2026-07-05
updated: 2026-07-05
page_type: log
sources: []
confidence: low
---

# 【归档】live-verification markdown 渲染实测段

> 从 `references/live-verification-mysite01.md` 移出(见提交 065789c)。结论已固化到
> field-contract / batch-verification / Invariant INV-4 / validate_slate_content_shape。原始明细供快速恢复。

## Markdown / Rich Text Rendering

Checked on 2026-06-29:

```text
Frontend URL: https://mysite01.web.allincms.com/posts/{post-slug-with-markdown-residue}
Backend edit URL: https://workspace.laicms.com/mysite01/posts/{postId}/update
```

Findings:

```text
Literal **bold** syntax remained visible on the frontend.
Literal backticks remained visible on the frontend.
The frontend DOM had 0 <strong>/<b> nodes inside this article content.
The frontend DOM had 0 <table> nodes inside this article content.
The backend Slate editor text also contained literal ** and backticks.
```

Counter-check:

```text
Frontend URL: https://mysite01.web.allincms.com/products/{product-slug-with-structured-table}
```

Findings:

```text
The product page rendered real <strong>/<b> nodes.
The product page rendered 1 real <table>.
```

Conclusion:

```text
The frontend can render structured bold/table nodes, but raw Markdown syntax is not parsed automatically when stored as plain Slate text. Batch upload must convert Markdown source into the editor's structured content-block schema, including marks and table blocks, before saving.
```

## Frontend Batch Audit Findings

Checked with `scripts/audit_frontend_rendering.py` on 2026-06-29 against 5 post URLs and 4 product URLs.

Refreshed redacted command shape:

```bash
python3 skills/allincms-bulk-content-upload/scripts/audit_frontend_rendering.py \
  --json --redact \
  https://mysite01.web.allincms.com/posts/{post-slug}
```

`--redact` keeps route patterns and issue codes while removing concrete slugs, headings, and raw snippets.

Blocking post issues observed:

```text
/posts/{post-slug-a}:
  literal_bold: **redacted bold markdown text**
  literal_inline_code: `https://example.invalid/path`
  jsx_style_object: style={{color: '#e67c00'}}
  html_tag_text: <u>

/posts/{post-slug-b}:
  literal_bold: **redacted bold markdown text**

/posts/{post-slug-c}:
  literal_bold: **redacted bold markdown text**
  literal_inline_code: `redacted-inline-code`
  literal_markdown_link: [redacted link text](./relative-target.md#anchor)

/posts/{post-slug-d}:
  literal_bold: **redacted bold markdown text**
  literal_inline_code: `redacted-inline-code`
  literal_markdown_link: [redacted link text](./relative-target.md)
```

Structural warnings observed:

```text
Several post pages had two H1s, often duplicate title H1s.
One checked product page had duplicate H1 text.
Other checked product pages had no render-audit issues.
```

Conclusion:

```text
The highest-risk current failure mode is not missing frontend support; it is importing Markdown/MDX/HTML-like source as plain Slate text. Upload tooling must convert rich text structurally, then run frontend DOM audit after sample and batch publish.
```
