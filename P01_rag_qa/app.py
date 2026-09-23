# p01_rag_qa/app.py
import sys
from pathlib import Path

# ---------- 让 core 可导入（临时方案，长期建议 pip install -e .）----------
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA

from core.config import (
    get_llm,
    BOT_ROLE,
    BOT_BEHAVIOR_RULES,
    MAX_HISTORY,
)

# ---------- 页面配置 ----------
st.set_page_config(page_title="我的知识库问答", layout="centered")
st.title("📚 知识库问答助手")

# ---------- 路径：全部基于当前文件，不依赖 CWD ----------
APP_DIR = Path(__file__).resolve().parent
CHROMA_DIR = APP_DIR / "chroma_db"

# ---------- 初始化向量存储 ----------
@st.cache_resource
def init_vectorstore():
    embedding = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-zh-v1.5",
        model_kwargs={"device": "cpu"},          # 有显卡可改 "cuda"
        encode_kwargs={"normalize_embeddings": True},
    )

    # 已有向量库：直接加载，避免每次冷启动重算 embedding
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embedding,
        )

    # 首次：用内置示例文本建库（不落盘中间文件）
    sample_text = """
    人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
    机器学习是AI的一个子集，它使计算机能够从数据中学习。
    深度学习是机器学习的一个子集，使用神经网络来模拟人脑的工作方式。
    """
    docs = [Document(page_content=sample_text)]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "，", " "],
    )
    chunks = splitter.split_documents(docs)

    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=str(CHROMA_DIR),
    )


vectorstore = init_vectorstore()

# ---------- LLM（由 core.config.get_llm 决定用 Ollama 还是 DeepSeek）----------
llm = get_llm()

# ---------- Prompt（把 config.yaml 的 role / behavior_rules 注入）----------
system_prompt = f"{BOT_ROLE}\n\n行为规则：\n{BOT_BEHAVIOR_RULES}"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "参考资料：\n{context}\n\n问题：{question}"),
])

# ---------- 检索问答链 ----------
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=False,
)

# ---------- 聊天界面 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("问点关于AI的问题吧"):
    # 显示并记录用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 生成并显示助手回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = qa_chain.invoke({"query": user_input})
        answer = response["result"]
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # 裁剪历史，让 config.yaml 里的 max_history 生效
    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]