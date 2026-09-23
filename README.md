# LangChain_Projects

## 00-项目说明

### 项目简介

本项目基于 LangChain 构建，项目根目录为 `python_LangChain`。

**主要功能：构建 LangChain 项目基础结构，支持配置管理、路径管理、RAG 问答等功能。**

- 项目配置通过 `.env` 和 `config.yaml` 管理
- `core/` 目录存放核心配置和路径管理
- 各子项目按功能模块拆分

### 项目目录结构

```text
python_LangChain/                  ← 项目根（CWD 应停在这里）
├── .env                           ← 敏感配置（API Key 等），不进 git
├── .env.example                   ← .env 模板，进 git
├── .gitignore
├── config.yaml                    ← 非敏感业务配置（提示词、模型名、参数）
├── README.md
├── core/                          ← 共享基础设施（全项目复用）
│   ├── config.py                  ← 唯一配置加载点
│   └── paths.py                   ← 统一路径常量
├── P01_rag_qa/                    ← 子项目 1：RAG 知识库问答
│   ├── chroma_db/                 ← 向量库持久化目录
│   ├── app.py                     ← 子项目入口（Streamlit）
│   ├── README.md
│   ├── requirements.txt
│   └── temp_knowledge.txt         ← 知识文本（现在代码里已不必须）
├── study/                         ← 学习/试验用
│   └── study_config.py            
└── tests/                         ← 测试目录
    ├── main.py
    └── Ollama_user.py             ← Ollama 使用试验
```

## **P01-rag-qa**

本项目实现 **RAG 文档问答系统**，使用 Streamlit 构建界面。

1. 使用 `RecursiveCharacterTextSplitter` 切分文档
2. 使用 `BAAI/bge-large-zh-v1.5` 生成 embedding
3. 使用 `chroma_db/` 作为向量数据库
4. 检索 top-3 相关片段
5. LLM 使用 `get_llm()`，支持 Ollama / DeepSeek
6. 通过 `st.session_state` 管理历史对话和 `MAX_HISTORY`