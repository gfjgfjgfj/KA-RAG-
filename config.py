import os
import commentjson as json
from loguru import logger

# 添加一个统一的config文件
config_file = "config.json"
config = {}
if os.path.exists(config_file):
    with open(config_file, "r", encoding='utf-8') as f:
        config = json.load(f)
if config:
    logger.info(f"加载配置文件成功, config: {config}")

gemini_key = config.get("gemini_key", "")
pinecone_key = config.get("pinecone_key", "")

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

# 处理gradio.launch参数
server_name = config.get("server_name", None)
server_port = config.get("server_port", None)
if server_name is None:
    server_name = "127.0.0.1"
if server_port is None:
    server_port = 7860

# 设置默认model
default_model = config.get("default_model", "gemini-1.5-flash")

autobrowser = config.get("autobrowser", True)


# 处理latex options
user_latex_option = config.get("latex_option", "default")
if user_latex_option == "default":
    latex_delimiters_set = [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ]
elif user_latex_option == "strict":
    latex_delimiters_set = [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ]
elif user_latex_option == "all":
    latex_delimiters_set = [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
        {"left": "\\begin{equation}", "right": "\\end{equation}", "display": True},
        {"left": "\\begin{align}", "right": "\\end{align}", "display": True},
        {"left": "\\begin{alignat}", "right": "\\end{alignat}", "display": True},
        {"left": "\\begin{gather}", "right": "\\end{gather}", "display": True},
        {"left": "\\begin{CD}", "right": "\\end{CD}", "display": True},
    ]
elif user_latex_option == "disabled":
    latex_delimiters_set = []
else:
    latex_delimiters_set = [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ]

bot_avatar = config.get("bot_avatar", "default")
user_avatar = config.get("user_avatar", "default")

if bot_avatar == "default":
    bot_avatar = "assets/chatbot.png"
if user_avatar == "default":
    user_avatar = "assets/user.png"

TITLE = config.get("title", "")

limit_user_num = config.get("limit_user_num", 100)  # 允许同时使用的用户数量

favicon_path = "assets/title.png"


