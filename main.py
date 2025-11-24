# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description:
"""
import enum

import gradio as gr

from config import (
    server_name,
    server_port,
    config_file,
    autobrowser,
    latex_delimiters_set,
    user_avatar,
    bot_avatar,
    TITLE,
    default_model,
    limit_user_num,
    favicon_path
)
from overwrites import reload_javascript
from models import get_model

from utils import (
    end_outputing,
    transfer_input,
    get_html,
    predict
)
from theme import (
    small_and_beautiful_theme
)

css = """
#chatbot-panel {
    height: 80%;  /* 设置宽度为页面高度的 80% */
}
"""
with gr.Blocks(theme=small_and_beautiful_theme, css=css) as demo:
    user_question = gr.State("")
    current_model = gr.State()
    with gr.Row(elem_id="chuanhu-header"):
        gr.HTML(get_html("header_title.html").format(
            app_title=TITLE), elem_id="app-title")
    with gr.Row(equal_height=True, elem_id="chatbot-panel"):
        with gr.Column(elem_id="chuanhu-area", scale=5):
            with gr.Column(elem_id="chatbot-area"):
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="ChatGPT",
                        elem_id="chuanhu-chatbot",
                        latex_delimiters=latex_delimiters_set,
                        sanitize_html=False,
                        # height=700,
                        show_label=False,
                        avatar_images=[user_avatar, bot_avatar],
                        show_share_button=True,
                    )
                with gr.Row(elem_id="chatbot-footer"):
                    with gr.Box(elem_id="chatbot-input-box"):
                        with gr.Row(elem_id="chatbot-input-row"):
                            with gr.Row(elem_id="chatbot-input-tb-row"):
                                with gr.Column(min_width=225, scale=12):
                                    user_input = gr.Textbox(
                                        elem_id="user-input-tb",
                                        show_label=False,
                                        placeholder="Input here",
                                        elem_classes="no-container",
                                        max_lines=5,
                                        # container=False
                                    )
                                with gr.Column(min_width=42, scale=1, elem_id="chatbot-ctrl-btns"):
                                    submitBtn = gr.Button(
                                        value="", variant="primary", elem_id="submit-btn")


    def create_greeting():
        return get_model(model_name=default_model)
        # loaded_stuff = [gr.update(), gr.update(), gr.Chatbot.update(label=default_model)]
        # return mModel, *loaded_stuff


    demo.load(create_greeting, inputs=None, outputs=[
        current_model, chatbot], api_name="load")
    chatgpt_predict_args = dict(
        fn=predict,
        inputs=[
            current_model,
            user_question,
            chatbot,
        ],
        outputs=[chatbot],
        show_progress=True,
    )

    end_outputing_args = dict(
        fn=end_outputing, inputs=[], outputs=[submitBtn]
    )

    transfer_input_args = dict(
        fn=transfer_input, inputs=[user_input], outputs=[user_question, user_input, submitBtn], show_progress=True
    )

    user_input.submit(
        **transfer_input_args).then(
        **chatgpt_predict_args).then(
        **end_outputing_args)

    submitBtn.click(**transfer_input_args).then(
        **chatgpt_predict_args, api_name="predict").then(
        **end_outputing_args)

demo.title = TITLE

if __name__ == "__main__":
    reload_javascript()
    demo.queue(concurrency_count=limit_user_num).launch(
        server_name=server_name,
        server_port=server_port,
        root_path="/greet",
        blocked_paths=[config_file],
        favicon_path=favicon_path,
        inbrowser=autobrowser,
    )
