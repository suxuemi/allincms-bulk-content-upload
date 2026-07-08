# 接手 allincms-bulk-content-upload skill(新会话启动稿)

> 给接手维护本仓库的新 AI 会话。事实以仓库当前状态为准:入手先跑 `git log --oneline -5`
> 和下方"常用命令"里的全测试,确认基线仍绿,再动手。

## 你在维护什么

一个 AI skill(agent 操作契约):把用户源料(PDF/DOCX/表格/网站/brief)→ 本地
source wiki → 确认内容包 → AllinCMS / LAICMS live 实测 schema → 上传发布 → 前后台验收。
JSON-first 执行(内容走 Next Server Action 批量回放,主题走 CDP,建站/传图 UI-only)。

## 位置与状态

- 真身:`~/skills/allincms-bulk-content-upload`(独立 git 仓)
- 软链挂载:`~/.codex/skills/` + `~/.claude/skills/`(Claude Code 与 Codex 两个 loader 都能发现)
- GitHub:`suxuemi/allincms-bulk-content-upload`(**私有仓**)
- 入库基线:81 个 `test_*.py` + hygiene + entrypoint 审计全过;工作区应保持 clean、与 origin/main 同步

## 先读哪里(权威源 + 结构)

- `SKILL.md` = **唯一能力契约真相源**。动任何逻辑前先读它(Operating Rule、Required
  Reading、Workflow、Browser Paths、Probe/Payload Rules、Anti-Confusion Checklist、
  Stop Conditions)。
- `README.md` / `AGENTS.md` / `CLAUDE.md` = 薄入口,**只指向 SKILL.md,不复制契约**
  (README 是人/GitHub 门面 + 多 AI 安装矩阵;AGENTS 是通用 agents.md 标准入口;
  CLAUDE defer 到 AGENTS)。
- `references/` = 深度契约(`server-action-save-api.md`、`mutation-safety.md`、
  `field-mapping.md`、`request-capture.md`、`launch-acceptance.md` 等)。
- `scripts/` = 工具 + 安全 gate + 回归测试(约 174 个脚本,81 个 `test_*.py`);
  脚本导航见 `references/script-index.md`。
- `agents/openai.yaml` = OpenAI 式 interface 卡片(带 `contract: SKILL.md` 指针)。
- `_archive/` = 退役的历史构建日志,不属活跃契约。

## 安全铁律(不可协商,代码强制)

1. **read-only 默认**:用户显式授权前,不 mutate 任何站点。
2. **每次远程 mutation 过 `scripts/check_pre_mutation_gate.py`**(preflight 新鲜度 /
   schema 已验 / sample 证明 / evidence / 动作记录)——gate 失败即停,不绕过。
3. **run-scoped 一次授权**可免重复提示,但 **8h TTL 过期**(`run_authorization.py`,
   `DEFAULT_TTL_HOURS = 8`),且硬 **carve-out 永远重确认**:建新站、删除/清理/下架、
   对外设置(域名/追踪/表单)、任何别的站、任何不在白名单的未知动作。
4. **本地零业务数据**:绝不写真实 siteKey / cookie / token / 凭证 / PII;测试占位用
   中性值 `mysite01`,**不能撞代码里的语义关键词**(例:`test` 会撞
   `make_authorization_record.py` 的 `PROBE_INTENT_TERMS`,静默破坏负向测试)。
5. **绝不编造** PII / 联系方式 / 价格 / 证书 / 评价 / 地址——只能用户提供。
6. **远程 mutation 单控制器**:并行 agent 只做独立只读检查。

## 常用命令(在仓库根 `~/skills/allincms-bulk-content-upload`)

```bash
# 全测试
for t in scripts/test_*.py; do python3 "$t" || echo "FAIL $t"; done

# 泄漏审计 + 测试入口审计
python3 scripts/audit_skill_hygiene.py && python3 scripts/audit_test_entrypoints.py

# 换机器安装(clone 后从仓库根跑;幂等,绝不碰真实目录)
./install.sh                    # 两个 loader 都装
./install.sh codex              # 只装 codex;claude 同理
./install.sh claude --force     # 只 repoint 失效软链

# 推 GitHub 前必扫真实 siteKey(发现即脱敏)
grep -rIoE 'laicms\.com/[a-z0-9]{6,}' --include='*.py' --include='*.md' . | sed 's|.*/||' | sort -u
```

## 维护纪律

- 改契约改 `SKILL.md`;薄入口别复制契约,只保持指针(单向无环:README→全部;
  CLAUDE→AGENTS→SKILL;SKILL 不回指)。
- 提交前:全测试绿 + hygiene + entrypoint 过。
- 推私有仓前:扫真实 siteKey + 凭证 + PII,发现即脱敏——**私有仓也可能被缓存/索引**。
- 每轮结束前做 skill 沉淀:判断有无可复用平台发现/接口变更/失败模式,记进 skill 再收尾;
  无则显式声明 "no reusable skill update needed"。
- 改安全模型 / gate / 授权逻辑这类高风险改动,先本地验证,再启独立对抗 agent 复审,
  对抗一致(PASS)后再推。

## 如果是用它建站(不是维护 skill)

不用这份启动稿——直接在 Claude Code / Codex 里 invoke skill
`allincms-bulk-content-upload`,loader 读 SKILL.md 带你走全流程(先 read-only 实测
schema,再按 gate 授权上传)。

## 未尽事项 / 注意

- 本仓库即 skill 真身,不要在别处找旧副本或历史目录;有旧副本请从本仓库重新同步。
- 软链是本机文件系统状态,不进 git;换机器/重装后跑 `./install.sh` 重建。
- 真实 AllinCMS live E2E(用户文件→建站→上传→发布→前后台验收)仍是最大的待验证项,
  需浏览器实操,先证明登录态与 siteKey。
