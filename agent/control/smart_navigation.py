import json

from agent.tool.base_tool import BaseTool


class SmartNavigation:
    tools: list = []
    default_tool: BaseTool = None
    bot_role: str = "AI助手"
    user: str = "用户"
    prompt: str = None

    def __init__(self, llm):
        self.llm = llm

    def addTools(self, tools):
        self.tools = self.tools + tools

    def set_bot_role_name(self, name):
        self.bot_role = name

    def set_user_name(self, name):
        self.user = name

    def set_default_tool(self, tool):
        self.default_tool = tool

    def prepare(self):
        mPrompt = [f"假如你是一个{self.bot_role}，能够判断{self.user}问题的类型", f"{self.user}的问题是：%s"]
        keys, description = self.get_all_params()
        mPrompt = mPrompt + self.get_tips_for_selection() + description
        mPrompt.append("请回复我JSON格式的内容，使用以下键将输出格式化为 JSON：")
        mPrompt.append("type")
        mPrompt = mPrompt + keys
        self.prompt = "\n".join(mPrompt)

    def query(self, question, history):
        if self.prompt:
            print(self.prompt % question)
            chat = self.llm.start_chat(history=history)
            response = chat.send_message(content=self.prompt % question).text.replace(
                "```json", "").replace("```", "").replace("\n", "")
            print(response)
            dic = json.loads(response)
            print(dic)
            selection = dic["type"]
            print(selection)
            if selection is not None:
                if selection == -1 and self.default_tool:
                    for chunk in self.default_tool.action(llm=self.llm, history=history, query=question, param=dic):
                        yield chunk
                else:
                    for chunk in self.tools[selection].action(llm=self.llm, history=history, query=question, param=dic):
                        yield chunk
        else:
            return None

    def get_all_params(self):
        if len(self.tools) == 0:
            return ""
        keys = []
        key_and_description = []
        for index, item in enumerate(self.tools):
            if isinstance(item, BaseTool):
                for key, value in item.param().items():
                    keys.append(key)
                    key_and_description.append(f"{key}:如果type等于{index},{value}")
        return keys, key_and_description

    def get_tips_for_selection(self) -> []:
        result = [f"请根据上下文、聊天记录和{self.user}的问题，提取以下信息："]
        temp = "type：判断问题的类型，"
        if self.default_tool:
            temp = f"{temp}type的默认值为-1。"
        for index, item in enumerate(self.tools):
            if isinstance(item, BaseTool):
                description = item.description()
                example = item.example()
                if example:
                    description = f"{description}，例如：{"、".join(example)}"
                temp = f"{temp}假如问题是关于{description}，则type为{index}。"
        result.append(temp)
        return result
