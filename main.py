import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


class LocalQABot:
    def __init__(self, config_path="config.yaml"):
        # 1. 从配置文件中读取设置
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["bot_settings"]

        # 2. 动态构建系统提示词 (System Prompt)
        system_template = (
            "你是一个{role}。请严格遵守以下行为准则：\n{behavior_rules}"
        )

        # 3. 组装完整的聊天提示词模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("system", "请根据以下对话历史，生成一个简洁、准确的答案：\n{history}"),
            ("human", "{question}")
        ])

        # 4. 初始化本地大模型
        self.llm = ChatOllama(model=self.config["model_name"])

        # 5. 构建链 (Chain)
        self.chain = self.prompt | self.llm

        # 6.初始化一个列表来存储所有对话历史
        self.history = []
        self.max_history_length = self.config.get("max_history", 30)  # 最大保留的对话轮次数

        print(f"✅ 机器人初始化成功！当前角色：{self.config['role']}")

    def chat(self):
        """处理用户的循环输入"""
        print("💬 问答机器人已就绪，输入 'exit' 或 'quit' 退出。")
        while True:
            user_input = input("\n👤 你: ").strip()
            # 退出命令
            if user_input.lower() in ["exit", "quit"]:
                print("👋 再见！")
                break

            # 清空历史命令
            if user_input.lower() in ["clear", "重置"]:
                self.history = []
                print("🔄 历史对话已清空。")
                continue

            if not user_input:
                continue

            # 1. 添加用户问题到历史
            self.history.append({"role": "user", "content": user_input})

            try:
                # 2. 构建包含完整历史的对话上下文
                # 只保留最近10轮对话（防止上下文过长）
                max_message = self.max_history_length * 2
                recent_history = self.history[-max_message:] if len(self.history) > max_message else self.history
                # 3. 格式化历史对话
                history_text = self._format_history(recent_history[:-1])
                # 4. 将用户输入注入模板prompt_data，并调用大模型
                prompt_data = {
                    "role": self.config["role"],
                    "behavior_rules": self.config["behavior_rules"],
                    "history": history_text,  # 历史上下文
                    "question": user_input
                }
                # 5. 流式输出
                print("\n🤖 机器人: ", end="", flush=True)
                full_response = ""

                for chunk in self.chain.stream(prompt_data):
                    # 逐块打印，不换行并立即刷新控制台
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content

                # 模型回答结束后，打印一个换行符，保持控制台格式整洁
                print()
                # 6. 将AI 的回答加入历史
                self.history.append({"role": "assistant", "content": full_response})

            except Exception as e:
                print(f"❌ 发生错误: {e}")

    def _format_history(self, history_messages):
        """格式化历史对话为文本"""
        if not history_messages:
            return "（这是对话的开始）"

        formatted = []
        for msg in history_messages:
            role = "用户" if msg["role"] == "user" else "AI"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)




if __name__ == "__main__":
    bot = LocalQABot()
    bot.chat()
