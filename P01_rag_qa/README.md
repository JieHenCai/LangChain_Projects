# 01 RAG 知识库问答

这是一个最小规格的RAG问答系统演示——功能上走通了全流程。

## 1.RAG标准流程：

```text
文档 → 切分 → 向量化 → 存入向量库
                          ↓
用户提问 → 向量化 → 检索相关片段 → 拼进 prompt → LLM 生成回答
```

## 2.代码结构

|   环节    |                实现                |
|:-------:|:--------------------------------:|
|  文档加载   |   内置`sample_text`→ `Document`    |
|  文档切分   | `RecursiveCharacterTextSplitter` |
|   向量化   |     `BAAI/bge-large-zh-v1.5`     |
|  存入向量库  |          `Chroma`+ 持久化           |
|   检索    |       `as_retriever(k=3)`        |
| 拼prompt | `ChatPromptTemplate`含`{context}` |
|   生成    |       `RetrievalQA` + LLM        |
|   界面    |            Streamlit             |

## 3.问题

### 3.1. 知识库是硬编码的3句话

```python
sample_text = """
人工智能（AI）是计算机科学的一个分支...
机器学习是AI的一个子集...
深度学习是机器学习的一个子集...
"""
```
这是演示文本，后续要变成从PDF/Markdown/数据库加载。这只是用来验证流程是否能跑通。
### 3.2. RetrievalQA 是legacy写法
langchain_classic.chains.RetrievalQA 是旧版 Chain，LangChain 官方现在推荐用 LCEL 写：
```python
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```
01_rag_qa 用 legacy 没问题（能跑、好学），但要知道这是"老写法"，学新东西时别停在它上面。后续要更新代码内容。
### 3.3. 对话历史没有真正进模型
```python
st.session_state.messages.append(...)   # 存了
...
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = ...[-MAX_HISTORY:]   # 裁剪了
```
但 qa_chain.invoke({"query": user_input}) 只传了当前问题。RetrievalQA 是无状态的，它看不到历史。

所以：

* `st.session_state.messages` 只是界面显示的历史。

* `max_history` 只是控制界面显示多少条。

* 模型本身没有多轮记忆——你问"它是什么？"再问"它有什么特点？"，第二个"它"模型不知道指谁。

这是"演示版"和"真·对话 RAG"最大的差距。 想真正多轮，要用 `ConversationalRetrievalChain`（legacy）或 LCEL + 历史消息注入。

### 3.4. 检索没有做任何优化
* `k=3`是写死的。
* 没有rerank、没有相似度阈值、没有混合检索。
* 没有引用来源（`return_source_documents=False`，用户看不到答案依据）。

### 3.5. 没有评估
RAG最容易被忽视、也是最重要的环节就是评估：检索准不准？答案好不好？现在没有书写任何评估手段，改了什么参数全靠感觉。

**总结：它是一个“流程完整、但每个环节都取最简”的RAG演示——用来验证“RAG是怎么跑起来的”很合适，用来当“生产级RAG模板”不够。**

## 4.修补建议流程
### 4.1. 换真实知识源
从`.txt`/`.md`/PDF加载，而不是硬编码3句话。可以体验`DocumentLoader`。
### 4.2. 让历史真正生效
用 `ConversationalRetrievalChain`（legacy）或 LCEL + `MessagesPlaceholder`（历史消息注入），让多轮对话有意义。
### 4.3. 显示来源
`return_source_documents=True`，把命中的片段展示出来，能看到检索质量，让用户知道答案依据。
### 4.4. 换成LCEL重写
作为` 02 `或` 05 `的对比示例，体会新旧写法差异。
### 4.5. 添加评估
准备几个"问题 + 期望答案"，改参数后对比效果。