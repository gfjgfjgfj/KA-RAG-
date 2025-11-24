# -*- coding:utf-8 -*-

import datetime
import hashlib
import json
import os
import pickle
import re
from enum import Enum
from typing import List, Union
from typing import TYPE_CHECKING

import gradio as gr
import pandas as pd
import tiktoken
from loguru import logger
from markdown import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pypinyin import lazy_pinyin

from config import config_file

if TYPE_CHECKING:
    from typing import TypedDict


    class DataframeData(TypedDict):
        headers: List[str]
        data: List[List[Union[str, int, bool]]]


def predict(current_model, *args):
    if current_model:
        iter = current_model.predict(*args)
        for i in iter:
            yield i


def billing_info(current_model):
    if current_model:
        return current_model.billing_info()


def set_key(current_model, *args):
    return current_model.set_key(*args)


def load_chat_history(current_model, *args):
    return current_model.load_chat_history(*args)


def delete_chat_history(current_model, *args):
    return current_model.delete_chat_history(*args)


def interrupt(current_model, *args):
    return current_model.interrupt(*args)


def reset(current_model, *args):
    if current_model:
        return current_model.reset(*args)


def retry(current_model, *args):
    iter = current_model.retry(*args)
    for i in iter:
        yield i


def delete_first_conversation(current_model, *args):
    return current_model.delete_first_conversation(*args)


def delete_last_conversation(current_model, *args):
    return current_model.delete_last_conversation(*args)


def set_system_prompt(current_model, *args):
    return current_model.set_system_prompt(*args)


def rename_chat_history(current_model, *args):
    return current_model.rename_chat_history(*args)


def auto_name_chat_history(current_model, *args):
    if current_model:
        return current_model.auto_name_chat_history(*args)


def export_markdown(current_model, *args):
    return current_model.export_markdown(*args)


def upload_chat_history(current_model, *args):
    return current_model.load_chat_history(*args)


def set_token_upper_limit(current_model, *args):
    return current_model.set_token_upper_limit(*args)


def set_temperature(current_model, *args):
    current_model.set_temperature(*args)


def set_top_p(current_model, *args):
    current_model.set_top_p(*args)


def set_n_choices(current_model, *args):
    current_model.set_n_choices(*args)


def set_stop_sequence(current_model, *args):
    current_model.set_stop_sequence(*args)


def set_max_tokens(current_model, *args):
    current_model.set_max_tokens(*args)


def set_presence_penalty(current_model, *args):
    current_model.set_presence_penalty(*args)


def set_frequency_penalty(current_model, *args):
    current_model.set_frequency_penalty(*args)


def set_logit_bias(current_model, *args):
    current_model.set_logit_bias(*args)


def set_user_identifier(current_model, *args):
    current_model.set_user_identifier(*args)


def set_single_turn(current_model, *args):
    current_model.set_single_turn(*args)


def handle_file_upload(current_model, *args):
    return current_model.handle_file_upload(*args)


def handle_summarize_index(current_model, *args):
    return current_model.summarize_index(*args)


def like(current_model, *args):
    return current_model.like(*args)


def dislike(current_model, *args):
    return current_model.dislike(*args)


def count_token(input_str):
    encoding = tiktoken.get_encoding("cl100k_base")
    if type(input_str) == dict:
        input_str = f"role: {input_str['role']}, content: {input_str['content']}"
    length = len(encoding.encode(input_str))
    return length


def markdown_to_html_with_syntax_highlight(md_str):  # deprecated
    def replacer(match):
        lang = match.group(1) or "text"
        code = match.group(2)

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ValueError:
            lexer = get_lexer_by_name("text", stripall=True)

        formatter = HtmlFormatter()
        highlighted_code = highlight(code, lexer, formatter)

        return f'<pre><code class="{lang}">{highlighted_code}</code></pre>'

    code_block_pattern = r"```(\w+)?\n([\s\S]+?)\n```"
    md_str = re.sub(code_block_pattern, replacer, md_str, flags=re.MULTILINE)

    html_str = markdown(md_str)
    return html_str


def normalize_markdown(md_text: str) -> str:  # deprecated
    lines = md_text.split("\n")
    normalized_lines = []
    inside_list = False

    for i, line in enumerate(lines):
        if re.match(r"^(\d+\.|-|\*|\+)\s", line.strip()):
            if not inside_list and i > 0 and lines[i - 1].strip() != "":
                normalized_lines.append("")
            inside_list = True
            normalized_lines.append(line)
        elif inside_list and line.strip() == "":
            if i < len(lines) - 1 and not re.match(
                    r"^(\d+\.|-|\*|\+)\s", lines[i + 1].strip()
            ):
                normalized_lines.append(line)
            continue
        else:
            inside_list = False
            normalized_lines.append(line)

    return "\n".join(normalized_lines)


def get_html(filename):
    path = f"assets/html/{filename}"
    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            return file.read()
    return ""


def clip_rawtext(chat_message, need_escape=True):
    # first, clip hr line
    hr_pattern = r'\n\n<hr class="append-display no-in-raw" />(.*?)'
    hr_match = re.search(hr_pattern, chat_message, re.DOTALL)
    message_clipped = chat_message[: hr_match.start()] if hr_match else chat_message
    # second, avoid agent-prefix being escaped
    agent_prefix_pattern = (
        r'(<!-- S O PREFIX -->.*?<!-- E O PREFIX -->)'
    )
    # agent_matches = re.findall(agent_prefix_pattern, message_clipped)
    agent_parts = re.split(agent_prefix_pattern, message_clipped, flags=re.DOTALL)
    final_message = ""
    for i, part in enumerate(agent_parts):
        if i % 2 == 0:
            if part != "" and part != "\n":
                final_message += (
                    f'<pre class="fake-pre">{escape_markdown(part)}</pre>'
                    if need_escape
                    else f'<pre class="fake-pre">{part}</pre>'
                )
        else:
            part = part.replace(' data-fancybox="gallery"', '')
            final_message += part
    return final_message


def convert_bot_before_marked(chat_message):
    """
    注意不能给输出加缩进, 否则会被marked解析成代码块
    """
    if '<div class="md-message">' in chat_message:
        return chat_message
    else:
        raw = f'<div class="raw-message hideM">{clip_rawtext(chat_message)}</div>'
        # really_raw = f'{START_OF_OUTPUT_MARK}<div class="really-raw hideM">{clip_rawtext(chat_message, need_escape=False)}\n</div>{END_OF_OUTPUT_MARK}'

        code_block_pattern = re.compile(r"```(.*?)(?:```|$)", re.DOTALL)
        code_blocks = code_block_pattern.findall(chat_message)
        non_code_parts = code_block_pattern.split(chat_message)[::2]
        result = []
        for non_code, code in zip(non_code_parts, code_blocks + [""]):
            if non_code.strip():
                result.append(non_code)
            if code.strip():
                code = f"\n```{code}\n```"
                result.append(code)
        result = "".join(result)
        md = f'<div class="md-message">\n\n{result}\n</div>'
        return raw + md


def convert_user_before_marked(chat_message):
    if '<div class="user-message">' in chat_message:
        return chat_message
    else:
        return f'<div class="user-message">{escape_markdown(chat_message)}</div>'


def escape_markdown(text):
    """
    Escape Markdown special characters to HTML-safe equivalents.
    """
    escape_chars = {
        # ' ': '&nbsp;',
        "_": "&#95;",
        "*": "&#42;",
        "[": "&#91;",
        "]": "&#93;",
        "(": "&#40;",
        ")": "&#41;",
        "{": "&#123;",
        "}": "&#125;",
        "#": "&#35;",
        "+": "&#43;",
        "-": "&#45;",
        ".": "&#46;",
        "!": "&#33;",
        "`": "&#96;",
        ">": "&#62;",
        "<": "&#60;",
        "|": "&#124;",
        "$": "&#36;",
        ":": "&#58;",
        "\n": "<br>",
    }
    text = text.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    return "".join(escape_chars.get(c, c) for c in text)


def detect_language(code):  # deprecated
    if code.startswith("\n"):
        first_line = ""
    else:
        first_line = code.strip().split("\n", 1)[0]
    language = first_line.lower() if first_line else ""
    code_without_language = code[len(first_line):].lstrip() if first_line else code
    return language, code_without_language


def construct_text(role, text):
    return {"role": role, "parts": [text]}


def construct_user(text):
    return construct_text("user", text)


def construct_system(text):
    return construct_text("system", text)


def construct_assistant(text):
    return construct_text("model", text)


def sorted_by_pinyin(list):
    return sorted(list, key=lambda char: lazy_pinyin(char)[0][0])


def sorted_by_last_modified_time(list, dir):
    return sorted(
        list, key=lambda char: os.path.getctime(os.path.join(dir, char)), reverse=True
    )


def get_file_names_by_type(dir, filetypes=[".json"]):
    os.makedirs(dir, exist_ok=True)
    files = []
    for type in filetypes:
        files += [f for f in os.listdir(dir) if f.endswith(type)]
    return files


def get_file_names_by_pinyin(dir, filetypes=[".json"]):
    files = get_file_names_by_type(dir, filetypes)
    if files != [""]:
        files = sorted_by_pinyin(files)
    logger.debug(f"files are:{files}")
    return files


def get_file_names_dropdown_by_pinyin(dir, filetypes=[".json"]):
    files = get_file_names_by_pinyin(dir, filetypes)
    return gr.Dropdown.update(choices=files)


def get_file_names_by_last_modified_time(dir, filetypes=[".json"]):
    files = get_file_names_by_type(dir, filetypes)
    if files != [""]:
        files = sorted_by_last_modified_time(files, dir)
    logger.debug(f"files are:{files}")
    return files


def reset_textbox():
    logger.debug("重置文本框")
    return gr.update(value="")


def hide_middle_chars(s):
    if s is None:
        return ""
    if len(s) <= 8:
        return s
    else:
        head = s[:4]
        tail = s[-4:]
        hidden = "*" * (len(s) - 8)
        return head + hidden + tail


def submit_key(key):
    key = key.strip()
    msg = f"API密钥更改为了{hide_middle_chars(key)}"
    logger.info(msg)
    return key, msg


def replace_today(prompt):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    return prompt.replace("{current_date}", today)


SERVER_GEO_IP_MSG = None
FETCHING_IP = False


def find_n(lst, max_num):
    n = len(lst)
    total = sum(lst)

    if total < max_num:
        return n

    for i in range(len(lst)):
        if total - lst[i] < max_num:
            return n - i - 1
        total = total - lst[i]
    return 1


def start_outputing():
    logger.debug("显示取消按钮，隐藏发送按钮")
    return gr.Button.update(visible=False)


def end_outputing():
    return gr.Button.update(visible=True)


def transfer_input(inputs):
    return (
        inputs,
        gr.update(value=""),
        gr.Button.update(visible=False),
    )


def add_source_numbers(lst, source_name="Source", use_source=True):
    if use_source:
        return [
            f'[{idx + 1}]\t "{item[0]}"\n{source_name}: {item[1]}'
            for idx, item in enumerate(lst)
        ]
    else:
        return [f'[{idx + 1}]\t "{item}"' for idx, item in enumerate(lst)]


def add_details(lst):
    nodes = []
    for index, txt in enumerate(lst):
        brief = txt[:25].replace("\n", "")
        nodes.append(f"<details><summary>{brief}...</summary><p>{txt}</p></details>")
    return nodes


def sheet_to_string(sheet, sheet_name=None):
    result = []
    for index, row in sheet.iterrows():
        row_string = ""
        for column in sheet.columns:
            row_string += f"{column}: {row[column]}, "
        row_string = row_string.rstrip(", ")
        row_string += "."
        result.append(row_string)
    return result


def excel_to_string(file_path):
    # 读取Excel文件中的所有工作表
    excel_file = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)

    # 初始化结果字符串
    result = []

    # 遍历每一个工作表
    for sheet_name, sheet_data in excel_file.items():
        # 处理当前工作表并添加到结果字符串
        result += sheet_to_string(sheet_data, sheet_name=sheet_name)

    return result


def get_last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)


def get_model_source(model_name, alternative_source):
    if model_name == "gpt2-medium":
        return "https://huggingface.co/gpt2-medium"


def refresh_ui_elements_on_load(current_model, selected_model_name, user_name):
    current_model.set_user_identifier(user_name)
    return toggle_like_btn_visibility(selected_model_name), *current_model.auto_load()


def toggle_like_btn_visibility(selected_model_name):
    if selected_model_name == "xmchat":
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


def get_corresponding_file_type_by_model_name(selected_model_name):
    if selected_model_name in ["xmchat", "GPT4 Vision"]:
        return ["image"]
    else:
        return [".pdf", ".docx", ".pptx", ".epub", ".xlsx", ".txt", "text"]


def auth_from_conf(username, password):
    try:
        with open(config_file, encoding="utf-8") as f:
            conf = json.load(f)
        usernames, passwords = [i[0] for i in conf["users"]], [
            i[1] for i in conf["users"]
        ]
        if username in usernames:
            if passwords[usernames.index(username)] == password:
                return True
        return False
    except:
        return False


def get_files_hash(file_src=None, file_paths=None):
    if file_src:
        file_paths = [x.name for x in file_src]
    file_paths.sort(key=lambda x: os.path.basename(x))

    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)

    return md5_hash.hexdigest()


def myprint(**args):
    print(args)


def replace_special_symbols(string, replace_string=" "):
    # 定义正则表达式，匹配所有特殊符号
    pattern = r"[!@#$%^&*()<>?/\|}{~:]"

    new_string = re.sub(pattern, replace_string, string)

    return new_string


class ConfigType(Enum):
    Bool = 1
    String = 2
    Password = 3
    Number = 4
    ListOfStrings = 5


class ConfigItem:
    def __init__(self, key, name, default=None, type=ConfigType.String) -> None:
        self.key = key
        self.name = name
        self.default = default
        self.type = type


def save_pkl(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def load_pkl(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data


def chinese_preprocessing_func(text: str) -> List[str]:
    import jieba
    jieba.setLogLevel('ERROR')
    return jieba.lcut(text)
