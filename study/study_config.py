import os
from dotenv import load_dotenv,find_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 验证 API Key 是否加载成功
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key:
    print(f"API Key 已加载：{api_key[:8]}...{api_key[-4:]}")
else:
    print("API Key 未加载，请检查 .env 文件中的配置。")
