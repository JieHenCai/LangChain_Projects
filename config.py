# config.py
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 定义常量，方便其他模块导入
API_KEY = os.getenv("DEEPSEEK_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# （可选）如果某个 Key 必须存在，可以加个检查
if not API_KEY:
    raise ValueError("环境变量 API_KEY 未设置，请检查 .env 文件")