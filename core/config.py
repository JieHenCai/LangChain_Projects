# core/config.py
import os
from pathlib import Path
from typing import Any

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import yaml
from dotenv import load_dotenv

from core.paths import PROJECT_ROOT, ENV_FILE, CONFIG_YAML

# ---------- 1. 加载 .env ----------
load_dotenv(ENV_FILE)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"找不到配置文件：{path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_yaml = _load_yaml(CONFIG_YAML)

# ---------- 3. 敏感配置（来自 .env）----------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")

# ---------- 4. 业务配置（来自 config.yaml）----------
BOT_SETTINGS: dict[str, Any] = _yaml.get("bot_settings", {})

BOT_ROLE: str = BOT_SETTINGS.get("role", "")
BOT_BEHAVIOR_RULES: str = BOT_SETTINGS.get("behavior_rules", "")
MAX_HISTORY: int = int(BOT_SETTINGS.get("max_history", 30))


# ---------- 5. 启动校验 ----------
def _validate_provider():
    if LLM_PROVIDER == "deepseek" and not DEEPSEEK_API_KEY:
        raise ValueError(
            "llm_provider=deepseek 但缺少 DEEPSEEK_API_KEY 配置, 请检查 .env 文件"
        )


# 从 config.yaml 读取（你已有 BOT_SETTINGS 字典）
LLM_PROVIDER = BOT_SETTINGS.get("llm_provider", "ollama")
OLLAMA_MODEL = BOT_SETTINGS.get("model_name", "qwen2.5:7b")
DEEPSEEK_MODEL = BOT_SETTINGS.get("deepseek_model", "deepseek-flash")


def get_llm():
    """根据配置返回对应的 LLM 实例"""
    _validate_provider()
    if LLM_PROVIDER == "deepseek":
        return ChatOpenAI(
            model=DEEPSEEK_MODEL,
            temperature=0,
            api_key=DEEPSEEK_API_KEY,  # 新版参数名是 api_key
            base_url="https://api.deepseek.com",  # 官方 base_url 不带 /v1 也可以[citation:3]
        )
    else:
        # 默认走本地 Ollama
        return ChatOllama(
            model=OLLAMA_MODEL,
            temperature=0,
            base_url="http://localhost:11434",  # Ollama 默认地址
        )
