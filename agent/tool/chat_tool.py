from agent.tool.base_tool import BaseTool


class ChatTool(BaseTool):
    def description(self) -> str:
        return "其他问题"

    def action(self, llm, query, history, param: dict):
        prompt = f"""
            假如你是武汉工程大学图书馆的一个热情、专业和智能的AI助手，名字叫知行，能够解答学生的问题或者跟学生闲聊。
            学生的给你的问题是：{query}

            要求：
            如果存在过往的聊天记录，请你结合过往的聊天记录进行回答，形成流畅和合理的对话，如果学生没有特别要求，请使用中文进行解答。
            如果涉及到暴力、国家政治等方面的问题，请你委婉拒绝不要回答。
            请你为学生生成问题的详细解答或对闲聊进行回复。
        """
        chat = llm.start_chat(history=history)
        sum_text = ""
        for chunk in chat.send_message(content=prompt, stream=True):
            sum_text = sum_text + chunk.text
            yield sum_text
