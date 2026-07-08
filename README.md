# allincms-bulk-content-upload

一个 AI **skill**(给 AI 编程助手用的"操作契约"),用于搭建和填充 [AllinCMS / LAICMS](https://www.allincms.com) 站点:把你的源料 —— PDF、DOCX、表格、网站、一份文字 brief —— 提炼成本地知识库和一份"确认过的内容包",然后新建或选择站点、实测它的当前字段结构,再上传/发布产品、文章、媒体、主题、路由和页面,**每一步都回读后台 + 前台核验**。

本仓库是这个 skill 的**唯一真身**。Claude Code、Codex 和其它 AI 工具加载的是同一份契约;这份 README 和薄入口文件 `AGENTS.md` / `CLAUDE.md` 只是把各工具指向它,不复制它。

> **权威契约是 [`SKILL.md`](SKILL.md),它是唯一真相源。** 本文档只是通往它的地图;如果本 README 和 `SKILL.md` 有出入,以 `SKILL.md` 为准。

> **文档语言说明**:给人读的入口(本 README、`NEXT-SESSION.md`)是中文;给 AI 读的契约(`SKILL.md`、`AGENTS.md`、`CLAUDE.md`、`references/`)是英文——这是刻意设计,不是没写完。AI 读英文契约无障碍,翻译反而会造成两份漂移。

## 这个 skill 能做什么

- **源料 → 内容包**:把源文件提炼成本地知识库,再生成可发布的草稿包(单页/产品/文章/站点信息草稿,外加媒体、表单、导航、分类计划)。**不编造任何东西** —— 联系方式、价格这类只能你提供。
- **先确认,再动手**:你先审一遍准备好的内容包,skill 才会碰线上站点。
- **JSON 优先执行**:抓一次真实保存请求后,直接用 Next Server Action 回放,而不是模拟点界面 —— 内容(分类/产品/文章)走 JSON 批量,主题设计走 CDP 抓取,只有建站和"本地图片→CDN"上传是真正需要点界面的步骤。
- **一切都核验**:每次新建/保存/发布都回读线上后台 + 公开前台确认,而不是听 AI 自己说"做好了"。

## 快速开始

两种方式,不想碰命令行就用**方式 A**。

### 方式 A · 把一句话丢给你的 AI(推荐,零命令行)

如果你在用 Claude Code、Codex 这类**能执行命令的 AI 助手**,直接把下面这段话整段复制给它 —— 它会自己 clone、安装、验证,并用中文告诉你怎么用:

```text
帮我安装并配置 allincms-bulk-content-upload 这个 AI skill:
1）把 https://github.com/suxuemi/allincms-bulk-content-upload 克隆到 ~/skills/allincms-bulk-content-upload(若已存在就 git pull 更新);
2）进入该目录运行 ./install.sh —— 它会自动探测本机已装的 AI 工具(Claude Code / Codex / WorkBuddy 等)并把 skill 软链进各自的 skills 目录(脚本幂等,绝不碰真实文件,只建软链);若你这个 AI 工具的 skills 目录不在默认探测范围,改用 ./install.sh --dir=<你的skills目录> 指定;
3）验证软链能读到 SKILL.md;
4）判断你这个工具支不支持 SKILL.md 格式的 skill:支持就确认已能发现它;若不支持(用的是别的插件/扩展机制),就直接把本仓库的 SKILL.md 当作操作契约读取并遵循,不必安装;
5）读 SKILL.md 和 README.md,用中文告诉我:这个 skill 能干什么、用它之前我要准备什么(AllinCMS 后台登录态、源料文件、以及你是否具备浏览器控制能力)、现在怎么开始建第一个站。
装完如果工具只在启动时扫描 skill,提醒我重启。
```

AI 跑命令时会请求你确认,你看一眼它在装什么再放行即可;装完它会直接带你进入下一步。

> 注意:skill 本体(clone + 软链)AI 能自动装好,但**操作 AllinCMS 需要 AI 工具具备浏览器控制能力**(如 Claude Code 的浏览器扩展、Codex 的内置浏览器)—— 这类工具侧扩展 AI 装不了,得你在工具里开;上面第 4 步会让它检查并告诉你缺不缺。

### 方式 B · 手动命令行

**第一步:拉下仓库**

```bash
git clone https://github.com/suxuemi/allincms-bulk-content-upload.git "$HOME/skills/allincms-bulk-content-upload"
```

> 公开仓,任何人可直接 clone,无需协作者权限或 token。

**第二步:挂到你的 AI 工具**

从仓库根目录跑自带安装脚本,它会**自动探测本机已装的 AI 工具**(Claude Code / Codex / WorkBuddy)并软链进各自的 skill 目录:

```bash
cd "$HOME/skills/allincms-bulk-content-upload"
./install.sh                        # 自动探测已装工具,各自软链
# ./install.sh codex                # 只装指定工具
# ./install.sh claude workbuddy     # 装多个指定工具
# ./install.sh --dir=/你的/skills   # 其它工具:软链进它的 skills 目录
# ./install.sh claude --force       # 重新指向已失效的软链
```

`install.sh` 是**幂等**的(重复跑没副作用),而且**绝不碰真实文件或目录** —— 只会创建或替换软链。装完如果工具只在启动时扫描 skill,重启一下工具即可。

**第三步:在对话里用它**

- **Claude Code / Codex**:直接让助手调用 skill `allincms-bulk-content-upload`,它会读 `SKILL.md` 带你走全流程 —— 先只读实测站点结构,再按安全闸逐步授权上传。
- 你只需要准备好源料(PDF/DOCX/表格/官网/brief),把要建什么站说清楚,剩下的按它的提示走。

## ⚠️ 注意事项(务必先读)

这个 skill 会动**线上共享状态**,所以安全规则是写进代码强制的(`scripts/check_pre_mutation_gate.py`),不只是嘴上说说:

- **默认只读**。你没有明确授权之前,它不会改动任何站点。
- **每次线上改动前都过一道闸**。新建/保存/发布/上传/删除/批量,都必须通过"改动前门禁"(检查数据新鲜度、字段结构已验证、样本已证明、证据齐全、留有操作记录)—— **门禁不过就停,不会硬闯**。
- **一次授权也不是空白支票**。你可以在确认内容包时给一次"全程授权"免掉反复确认,但它会**过期**(默认 8 小时),而且永远盖不住这些高危动作:**建新站、删除/清理/下架、对外设置(域名/追踪/表单)、以及任何别的站点** —— 这些每次都要你重新明确授权。
- **绝不编造**。联系方式、价格、证书、评价、地址,只能你提供,它不会自己填。
- **本地不留业务数据**。真实站点 key、cookie、token、账号、导出的名单绝不写进本仓库 —— 仓库里只有中性的字段名、路由形状和脱敏后的证据。
- **改动只由单一控制者执行**。并行的 AI 只能做只读检查,真正的线上写操作永远单线程、走完门禁再做。

## 在不同 AI 工具里使用

| 工具 | 怎么加载 | 兼容性 |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` 软链,调用名 `allincms-bulk-content-upload` | 原生 SKILL.md,直接可用 |
| **Codex** | `~/.codex/skills/` 软链 | 原生 SKILL.md,直接可用 |
| **WorkBuddy** | `~/.workbuddy/skills/` 软链(install.sh 自动探测) | WorkBuddy 用自有 skill 格式;软链会建好,但能否发现 SKILL.md 需在其内实测 |
| **其它读 `agents.md` 的**(Cursor、Gemini CLI…) | 读仓库根 `AGENTS.md` | `AGENTS.md` → `SKILL.md` |
| **用别的插件机制的**(如 zcode) | 不走 skills 目录 | 直接把本仓库 `SKILL.md` 当操作契约喂给它,不必安装 |
| **OpenAI 式接口** | `agents/openai.yaml` 卡片 | `agents/openai.yaml` → `SKILL.md` |

**兼容性底线**:这个 skill 的本体是一份 `SKILL.md` 契约 + 一组脚本。凡是能读 SKILL.md 的工具都能用 —— 支持"skills 目录自动发现"的(Claude / Codex 等)靠软链自动触发;不支持的,直接让 AI 读 `SKILL.md` 照做即可,一样能用,只是不自动触发。

`AGENTS.md` 和 `CLAUDE.md` 主要在**仓库被当项目打开**时起作用;当它**作为 skill 加载**时,loader 直接读 `SKILL.md`。两条路最终汇到同一份契约。

如果环境不支持软链,把整个目录复制进工具的 skill 文件夹 —— 但只保留一份为权威,其余从本仓库重新同步。

## 目录结构

| 路径 | 放什么 |
|---|---|
| [`SKILL.md`](SKILL.md) | 权威操作契约:操作规则、必读、工作流、浏览器路径、探针/载荷规则、停止条件 |
| [`AGENTS.md`](AGENTS.md) | 通用 agent 薄入口(`agents.md` 标准)→ 指向 `SKILL.md` |
| [`CLAUDE.md`](CLAUDE.md) | Claude Code 薄入口 → 指向 `AGENTS.md` + `SKILL.md` |
| [`NEXT-SESSION.md`](NEXT-SESSION.md) | 给接手维护的新会话的启动稿(中文) |
| `references/` | 深度契约:Server-Action 保存 API、改动安全、字段映射、请求抓取、上线验收等 |
| `scripts/` | 强制 + 辅助工具:改动前门禁、授权构建器、清单/证据校验器、模拟器,及各自的 `test_*.py` |
| `agents/` | 各工具的接口卡片(`openai.yaml`) |
| `_archive/` | 退役的历史构建日志,留作追溯,不属活跃契约 |

## 仓库安全

本仓库在 GitHub 维护、跨设备复用。保持它通用、干净:

- **要**放:操作契约、references、辅助脚本、测试、安装说明。
- **不要**放:客户数据、密钥、生产凭证、真实站点 key、cookie/token、导出的名单、账号相关的业务文案。测试里的占位 key 都是中性的(如 `mysite01`),绝非真实值。

## 许可证

MIT — 见 [LICENSE](LICENSE)。你可以自由使用、修改、再分发,保留版权声明即可。
