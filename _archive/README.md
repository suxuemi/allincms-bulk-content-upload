---
doc_id: allincms-archive-readme
title: 【归档】allincms-bulk-content-upload 归档说明
description: 本 skill 清理时移出的过期/被取代/施工流水内容的归档区,归档不删除,便于快速恢复;非活跃指引
layer: ops
status: final
created: 2026-07-05
updated: 2026-07-05
page_type: index
sources: []
confidence: low
---

# 归档区（archive-not-delete）

## 约定

清理这个 skill 时,**被取代 / 过期 / 施工流水 / 被遗弃**的内容**移到这里,不硬删**,便于以防万一的快速恢复。git 历史本已可恢复,但这个文件夹让"翻回原始明细"一步到位。

- 这里的东西**不是活跃指引**——活跃规则在 `references/` 和 `SKILL.md`。
- 每个归档文件的 frontmatter `description` 写清:从哪移出、结论现固化在哪、原提交号。
- 后续再清理时,同样先归档到这里,再从活跃文件移除。

## 现有归档

| 文件 | 来源 | 结论现固化于 |
|---|---|---|
| `source-package-buildlog.md` | `references/operational-findings.md` 蒸馏移出(提交 cc23f71)~1600 行施工/加固流水 | `source-files-to-site-package.md` + operational-findings 顶部 Invariants + 校验器/测试 |
| `live-verification-markdown-rendering.md` | `references/live-verification-mysite01.md` 移出(提交 065789c)markdown-residue 实测段 | `field-contract.md` / `batch-verification.md` / Invariant INV-4 / `validate_slate_content_shape.py` |

## 恢复方式

直接从本文件夹复制回目标 reference,或 `git show <原提交>^:<原路径>` 取压缩前全文。
