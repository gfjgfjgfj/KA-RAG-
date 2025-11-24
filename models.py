# -*- coding: utf-8 -*-
"""
Get model client from model name
"""
import gradio as gr
from loguru import logger
import config
from llm.base_model import ModelType


def get_model(
        model_name,
        original_model=None,
):
    model_type = ModelType.get_type(model_name)
    if model_type != ModelType.OpenAI:
        config.local_embedding = True
    model = original_model
    chatbot = gr.Chatbot.update(label=model_name)
    # try:
    if model_type == ModelType.OpenAI:
        pass
    elif model_type == ModelType.Gemini:
        logger.info(f"正在加载Gemini模型: {model_name}")
        from llm.GeminiClient import GeminiClient
        model = GeminiClient(model_name, key=config.gemini_key)
    elif model_type == ModelType.Unknown:
        raise ValueError(f"未知模型: {model_name}")
    # except Exception as e:
    #     logger.error(e)
    return model, chatbot
