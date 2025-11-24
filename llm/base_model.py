import traceback
from enum import Enum
from typing import Any

import gradio as gr
from loguru import logger
from rag.template.base import BaseTemplate
from rag.template.courses import CoursesTemplate

from utils import (
    construct_assistant,
    construct_user,
)


class ModelType(Enum):
    Unknown = -1
    Gemini = 0
    OpenAI = 1

    @classmethod
    def get_type(cls, model_name: str):
        model_name_lower = model_name.lower()
        if "chatgpt" in model_name_lower:
            model_type = ModelType.OpenAI
        elif "gemini" in model_name_lower:
            model_type = ModelType.Gemini
        else:
            model_type = ModelType.Unknown
        return model_type


class BaseLLMModel:
    def __init__(
            self,
            model_name,
            temperature=1.0,
            stop="",
    ) -> None:
        self.history = []
        self.model_name = model_name
        self.model_type = ModelType.get_type(model_name)
        self.chatbot = []
        self.default_stop_sequence = stop
        self.temperature = temperature
        self.stop_sequence = stop
        self.coursesTemplate = CoursesTemplate()

    def getLLM(self) -> Any:
        return None

    def get_answer_stream_iter(self, input_content: str):
        logger.warning("stream predict not implemented, using at once predict instead")
        response, _ = self.get_answer_at_once(input_content=input_content)
        yield response

    def get_answer_stream_iter_by_rag(self, input_content: str, template: BaseTemplate):
        logger.warning("stream predict not implemented, using at once predict instead")
        response = self.get_answer_by_rag(input_content=input_content)
        yield response

    def get_answer_by_rag(self, input_content: str, template: BaseTemplate):
        logger.warning("at once predict not implemented, using stream predict instead")
        return ""

    def get_answer_at_once(self, input_content: str):
        logger.warning("at once predict not implemented, using stream predict instead")
        return ""

    def stream_next_chatbot(self, question, chatbot):
        def get_return_value():
            return chatbot
        chatbot.append((question, ""))
        partial_text = ""
        for partial_text in self.get_answer_stream_iter_by_rag(input_content=question, template=self.coursesTemplate):
            if type(partial_text) == tuple:
                partial_text, token_increment = partial_text
            chatbot[-1] = (chatbot[-1][0], partial_text)
            yield get_return_value()
        self.history.append(construct_assistant(partial_text))

    def next_chatbot_at_once(self, question, chatbot):
        chatbot.append((question, ""))
        ai_reply = self.get_answer_by_rag(input_content=question, template=self.coursesTemplate)
        self.history.append(construct_assistant(ai_reply))
        self.history[-2] = construct_user(question)
        chatbot[-1] = (chatbot[-1][0], ai_reply)
        return chatbot

    def handle_file_upload(self, files, chatbot, language):
        """if the model accepts modal input, implement this function"""
        status = gr.Markdown.update()
        return gr.Files.update(), chatbot, status

    def prepare_inputs(
            self, real_inputs, use_websearch,
            files, reply_language, chatbot,
    ):
        if type(real_inputs) == list:
            fake_inputs = real_inputs[0]["text"]
        else:
            fake_inputs = real_inputs
        if files:
            # 将检索到的文件里面的相关内容补充到问题后面
            pass
        elif use_websearch:
            # 将搜索引擎搜到的相关内容补充到问题后面
            pass
        else:
            display_append = ""
        return fake_inputs, real_inputs, chatbot

    def predict(
            self,
            inputs,
            chatbot,
            stream=True,
            use_websearch=False,
            files=None,
            reply_language="中文",
    ):
        if type(inputs) == list:
            logger.info(f"用户的输入为：{inputs[0]['text']}")
        else:
            logger.info(f"用户的输入为：{inputs}")

        fake_inputs, inputs, chatbot = self.prepare_inputs(
            real_inputs=inputs,
            use_websearch=use_websearch,
            files=files,
            reply_language=reply_language,
            chatbot=chatbot
        )
        yield chatbot + [(fake_inputs, "")]
        if len(inputs.strip()) == 0:
            yield chatbot + [(inputs, "")]
            return
        if type(inputs) == list:
            self.history.append(inputs)
        else:
            self.history.append(construct_user(inputs))
        try:
            if stream:
                logger.debug("使用流式传输")
                iter = self.stream_next_chatbot(
                    inputs,
                    chatbot
                )
                for chatbot in iter:
                    yield chatbot
            else:
                logger.debug("不使用流式传输")
                chatbot = self.next_chatbot_at_once(
                    inputs,
                    chatbot
                )
                yield chatbot
        except Exception as e:
            traceback.print_exc()
            print(e)
            yield chatbot

        if len(self.history) > 1 and self.history[-1]["parts"][0] != inputs:
            logger.info(f"回答为：{self.history[-1]["parts"][0]}")

        if len(self.history) > 5:
            count = len(self.history) - 5
            del self.history[-count:]
            status_text = f"为了防止token超限，模型忘记了早期的 {count} 轮对话"
            logger.info(status_text)
            yield chatbot
