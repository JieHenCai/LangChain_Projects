# 01 RAG 知识库问答

**学了什么**：文档切分 → embedding → Chroma → 检索 → LLM 生成

**关键点**：Chroma 持久化用 persist_directory；RetrievalQA 是 legacy，以后要学 LCEL

**踩的坑**：bge 模型第一次下载很慢；向量库不删会一直用旧的