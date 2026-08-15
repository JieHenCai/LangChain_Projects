# import ollama
import os
from langchain_openai import ChatOpenAI
from config import API_KEY
# 聊天模式
# response = ollama.chat(model="qwen2.5:7b", messages=[{"role": "user", "content": "你好"}])
# print(response)
# print(response['message']['content'])

os.environ["DEEPSEEK_API_KEY"] = API_KEY

llm = ChatOpenAI(
    model='deepseek-v4-pro',
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    openai_api_base="https://api.deepseek.com",
    temperature=0.7,
    max_tokens=1024
)
response = llm.invoke("你好，DeepSeek！请做个简短的自我介绍。")
print(response.content)



