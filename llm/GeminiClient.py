import json
from typing import Any

import google.generativeai as genai
import langchain
from google.generativeai import GenerationConfig

from agent.control.smart_navigation import SmartNavigation
from agent.tool.chat_tool import ChatTool
from agent.tool.course_tool import CourseTool
from agent.tool.knowledge_tool import KnowledgeTool
from agent.tool.library_tool import LibraryTool
from config import gemini_key
from llm.base_model import BaseLLMModel
from llm.gemini import GeminiModel
from rag.template.base import BaseTemplate


class GeminiClient(BaseLLMModel):
    llm_Model: GeminiModel = None
    generation_config: GenerationConfig = None

    def getLLM(self) -> Any:
        return self.llm_Model

    def __init__(self, model_name, key: str = ""):
        super().__init__(model_name=model_name)
        genai.configure(api_key=key)
        self.api_key = key
        self.llm_Model = GeminiModel(key=gemini_key, model_name=model_name)
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=5000,
            temperature=0.2
        )
        self.navigation = SmartNavigation(self.llm_Model.getLLM())
        self.navigation.addTools([LibraryTool(), CourseTool(), KnowledgeTool(), ChatTool()])
        self.navigation.prepare()

    def get_answer_at_once(self, input_content: str):
        if not self.api_key:
            raise ValueError("API key is not set")
        response = self._get_response(input_content=input_content)
        if response is None:
            response = "error!"
        return response, self.count_token(response)

    def _get_response(self, input_content: str):
        langchain.debug = True
        history = self.history
        history[-1]["parts"] = [input_content]
        if len(history) > 5:
            history = history[-5:]
        print("----------------------------")
        print(history)
        print("----------------------------")
        llm = self.llm_Model.getLLM()
        chat = llm.start_chat(history=history)
        response = chat.send_message(content=history[-1], generation_config=self.generation_config).text
        return response

    def count_token(self, content: str):
        return self.llm_Model.countToken(text=content)

    def get_answer_stream_iter(self, input_content: str):
        langchain.debug = True
        history = self.history
        if len(history) > 5:
            history = history[-5:]
        print("----------------------------")
        print(history)
        print("----------------------------")
        llm = self.llm_Model.getLLM()
        chat = llm.start_chat(history=history)
        sum_text = ""
        for chunk in chat.send_message(content=input_content, stream=True, generation_config=self.generation_config):
            sum_text = sum_text + chunk.text
            yield sum_text

    def get_answer_stream_iter_by_rag(self, input_content: str, template: BaseTemplate):
        yield "思考中"
        for response in self.navigation.query(question=input_content, history=self.history):
            yield response

    def get_answer_by_rag(self, input_content: str, template: BaseTemplate):
        yield "思考中"
        response = self.navigation.query(question=input_content, history=self.history)
        if response is None:
            response = "error!"
        return response

    def isConsultingCourse(self, input_content):
        template = f"""
            假如你是一个AI助手，能够判断学生问题的类型，并能从中提取信息
            学生的问题是：{input_content}

            请根据上下文、聊天记录和学生的问题，分析和提取以下信息：
            type：判断问题的类型，如果是咨询某个课程，则type为1，如果是咨询图书馆的相关内容，则type为2，如果是咨询某个课程的某个知识点，则type为3，闲聊等其他情况type为4。比如学生的问题是：怎么学习C++，那么type等于1，如果学生的问题是，怎么借书，那么type等于2。
            course_name：如果是咨询某个课程的信息，则从问题中将课程名字提取出，如果不是则为空字符串，比如学生的问题是：怎么学习C++课程，那么course_name的值为C++。
            library_question:如果是咨询图书馆的相关内容,则将问题进行简化，如果不是则为空字符串，比如学生的问题是：你能介绍图书馆吗，那么library_question的值为图书馆的介绍。
            knowledge：如果是咨询某个课程的某个知识点，则将知识点提取出，比如学生的问题是：什么是特征选择算法，那么knowledge的值为特征选择算法。

            请回复我JSON格式的内容，使用以下键将输出格式化为 JSON：
            type
            course_name
            library_question
            knowledge
        """
        llm = self.llm_Model.getLLM()
        chat = llm.start_chat(history=self.history)
        response = chat.send_message(content=template, generation_config=self.generation_config).text.replace("```json", "").replace("```", "").replace("\n", "")
        print(response)
        return json.loads(response)