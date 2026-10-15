# DeepSeek Agent

一个基于 **DeepSeek API** 的轻量 AI Agent 应用：具备多轮对话能力，并内置**简易 RAG 知识库**（TF-IDF 关键词检索），本地即可部署。项目使用 **Claude Code（Vibe Coding 模式）** 作为开发助手完成，沉淀了一套 Prompt 工程与 API 对接经验。

- 后端：Python + FastAPI
- 模型：DeepSeek（`deepseek-v4-flash` / `deepseek-v4-pro`）
- RAG：纯标准库 TF-IDF + 余弦相似度检索（零重依赖）
- 部署：本地 / WSL（Ubuntu）

## 功能特性

- 💬 多轮对话（OpenAI 兼容的 `/chat/completions` 接口）
- 📚 RAG 知识库：上传 Markdown/TXT 文档 → 自动切块 → 关键词检索 → 注入 Prompt
- 🔗 回答附引用来源（`[1][2]` 编号 + 命中文档与相似度）
- 🌐 极简网页聊天界面 + REST API
- 🧪 纯逻辑单元测试（无需 API Key 即可跑通）

## 架构

```
                         ┌─────────────────────────────┐
  用户提问               │            Agent            │
  ───────────────────▶  │  1. 检索知识库 (TF-IDF)     │
                         │  2. 组装 Prompt（上下文注入）│
                         │  3. 调用 DeepSeek           │
                         └──────────┬──────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
   ┌──────────────────┐  ┌────────────────────┐  ┌────────────────┐
   │  KnowledgeStore  │  │   DeepSeekClient   │  │   FastAPI      │
   │  loader→chunker  │  │   POST /chat/      │  │   /chat        │
   │  →TF-IDF→retrieve│  │   completions      │  │   /ingest      │
   └──────────────────┘  └────────────────────┘  │   /health      │
                                                 └────────────────┘
```

## 目录结构

```
deepseek-agent/
├── app/
│   ├── main.py            # FastAPI 入口与路由
│   ├── config.py          # 环境变量配置
│   ├── schemas.py         # 请求/响应模型
│   ├── agent.py           # 对话编排 + Prompt 模板
│   ├── deepseek_client.py # DeepSeek API 客户端
│   └── rag/               # RAG 模块（tokenizer/chunker/tfidf/loader/store/retriever）
├── data/knowledge/        # 示例知识库（Markdown）
├── static/index.html      # 网页聊天界面
├── scripts/ingest.py      # CLI 重建索引
├── deploy/wsl-setup.sh    # WSL 一键部署脚本
└── tests/                 # 单元测试
```

## 快速开始

### 1. 准备环境

需要 Python 3.10+。

```bash
cd deepseek-agent
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux / WSL
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key：
# DEEPSEEK_API_KEY=sk-xxxxxxxx
```

> 获取 Key：登录 [DeepSeek 开放平台](https://platform.deepseek.com/) → API Keys。

### 3. 启动服务

```bash
python scripts/ingest.py   # 可选：先看看知识库索引统计
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开浏览器访问 <http://localhost:8000>，即可在网页中对话；交互式 API 文档见 <http://localhost:8000/docs>。

### 4. 测试对话

提问知识库内的问题，例如「如何申请退款？」或「专业版套餐多少钱？」，回答会附上引用来源。提问知识库外的问题，模型会明确说明无法回答，而不是编造。

## API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查，返回已索引块数 |
| POST | `/chat` | 对话（含 RAG），返回回复 + 来源 |
| POST | `/ingest` | 重建知识库索引 |
| GET | `/` | 网页聊天界面 |

`POST /chat` 请求示例：

```json
{
  "message": "如何申请退款？",
  "history": [
    { "role": "user", "content": "你好" },
    { "role": "assistant", "content": "你好，有什么可以帮你？" }
  ]
}
```

响应：

```json
{
  "reply": "购买后 7 天内可申请全额退款……[1]",
  "sources": [
    { "index": 1, "source": "常见问题.md", "score": 0.62, "snippet": "所有套餐均支持……" }
  ],
  "model": "deepseek-v4-flash"
}
```

## RAG 设计说明

由于 **DeepSeek API 不提供 embeddings 接口**，本项目采用「TF-IDF 关键词检索」实现简易 RAG，全部使用 Python 标准库，无需下载模型、无需额外服务：

1. **加载**：扫描 `data/knowledge/` 下的 `.md`/`.txt` 文档
2. **分词**：中文按字符 bigram 切分、英文按单词切分并过滤停用词
3. **切块**：按 Markdown 标题/段落切块（默认 ≤500 字），保留标题上下文
4. **索引**：对每个块计算 TF-IDF 向量（平滑 IDF + L2 归一化）
5. **检索**：query 向量与各块做余弦相似度，取 top-k
6. **注入**：命中的块以编号形式拼进 Prompt，供模型引用

> 升级建议：如需更强的语义检索，可替换为本地 embedding（如 BGE）或接入第三方 embedding 服务，仅需改动 `app/rag/` 内部实现，上层接口不变。

## Prompt 工程经验

本项目沉淀的核心 Prompt 思路（见 `app/agent.py` 的 `SYSTEM_PROMPT`）：

1. **角色 + 边界**：明确「知识库问答助手」身份，要求**只依据参考资料作答，不得编造**。
2. **兜底策略**：资料不足时要求模型**明说无法回答**并指出缺什么，避免幻觉。
3. **结构化注入**：把检索结果以 `[1] 来源：xxx（章节：xxx）\n内容` 的编号格式注入，并要求回答末尾标注引用编号，便于溯源。
4. **可观测性**：前端展示「参考来源 + 相似度」，让 RAG 效果可见、可调试。

调优要点：`TOP_K`（注入多少块）与 `SCORE_THRESHOLD`（相似度阈值）直接影响回答质量——块太少上下文不足，太多则引入噪声；阈值过低会注入无关内容。

## DeepSeek API 对接要点

- **基地址**：`https://api.deepseek.com`，端点 `POST /chat/completions`，与 OpenAI 兼容。
- **认证**：`Authorization: Bearer <API_KEY>`。
- **模型**（⚠️ 2026-07-24 起 `deepseek-chat`/`deepseek-reasoner` 已停用）：
  - `deepseek-v4-flash`：默认，速度快、成本低
  - `deepseek-v4-pro`：能力更强
  - 可通过 `.env` 的 `DEEPSEEK_MODEL` 切换。
- **无 embeddings 接口**：因此 RAG 向量化采用本地 TF-IDF（见上文）。

英文文档：<https://api-docs.deepseek.com/>

## WSL 部署

在 Windows 上打开 WSL 终端，进入项目目录（若项目在 `C:\Users\A\deepseek-agent`，对应 WSL 路径为 `/mnt/c/Users/A/deepseek-agent`）：

```bash
cd /mnt/c/Users/A/deepseek-agent
bash deploy/wsl-setup.sh
```

脚本会自动：安装系统依赖 → 创建 `.venv` → 安装 Python 依赖 → 生成 `.env`（首次需填入 Key 后重跑）→ 重建索引 → 启动服务。启动后浏览器访问 <http://localhost:8000>。

> 小提示：把项目放在 WSL 原生文件系统（如 `~/deepseek-agent`）比放在 `/mnt/c` 性能更好。

## 运行测试

```bash
pip install pytest
python -m pytest -v
```

单元测试覆盖分词、切块、TF-IDF 检索与 Agent 编排，均不依赖真实 API Key。

## 代码托管

```bash
git init
git add .
git commit -m "feat: DeepSeek Agent MVP —— 对话 + TF-IDF RAG"

# 在 GitHub 创建同名仓库后：
git remote add origin https://github.com/<你的用户名>/deepseek-agent.git
git branch -M main
git push -u origin main
```

## License

MIT
