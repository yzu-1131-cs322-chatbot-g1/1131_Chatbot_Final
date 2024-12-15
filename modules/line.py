import os, sys, shutil
import tempfile
from logging import Logger
from enum import Enum
from pyclbr import Function
from traceback import print_tb

from flask import Flask, request, abort

# custom modules    # 不確定直接 import modules 會不會有問題，但避免循環 import 還是先不要 import 全部
from modules.config import config
from modules import azure, gemini

# line imports
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
)


channel_access_token = config["Line"]["CHANNEL_ACCESS_TOKEN"]
channel_secret = config["Line"]["CHANNEL_SECRET"]
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

def _clean_user_images():
    if os.path.exists(user_image_path):
        shutil.rmtree(user_image_path)  # 刪除整個資料夾
        os.makedirs(user_image_path)  # 重新建立空資料夾

user_image_path = os.path.normpath(config["Line"]["USER_IMAGE_PATH"])
if not os.path.exists(user_image_path):
    os.makedirs(user_image_path)
else:
    _clean_user_images()


def callback(app_logger: Logger) -> str:
    """
    LINE 驗證 Webhook URL 用的 callback
    """
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app_logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


class ChatMode(Enum):
    """
    聊天模式的列舉，包含：

    - GEMINI: 聊天
    - SEARCH_MOVIE: 查詢資料庫
    - GUESS_MOVIE: 以圖搜尋
    - SUB_TRANSLATE: 字幕翻譯
    """
    GEMINI = "聊天"
    SEARCH_MOVIE = "查詢資料庫"
    GUESS_MOVIE = "以圖搜尋"
    SUB_TRANSLATE = "字幕翻譯"


def foo(x):
    x = "command not implemented yet\nreceived: " + x
    print(x)
    return x


# 不同聊天模式的指令處理函數
CommandHandlers: dict = {
    ChatMode.GEMINI: gemini.gemini_llm_sdk,
    ChatMode.GUESS_MOVIE: foo,
    ChatMode.SEARCH_MOVIE: foo,
    ChatMode.SUB_TRANSLATE: foo,
}


# default chat mode
chat_mode = ChatMode.GEMINI

# default command handler
command_handler = CommandHandlers[chat_mode]


def handle_text_message(event) -> None:
    r"""
    處理文字訊息的函數。

    當文字訊息為指令時，會切換聊天模式，並刪除所有已上傳的圖片。

    當文字訊息不是指令時，會根據目前聊天模式取得對應的處理函數並進行回應。
    """
    global chat_mode, command_handler
    text = event.message.text
    result = ""

    # text is a command
    if text.startswith("@"):
        cmd = text[1:]
        try:
            new_chat_mode = ChatMode(cmd)
            if new_chat_mode != chat_mode:
                chat_mode = new_chat_mode
                command_handler = CommandHandlers[new_chat_mode]
                _clean_user_images()
            result = "聊天模式已切換至：" + chat_mode.value
        except ValueError:
            result = "找不到指令：" + cmd
        except Exception as e:
            result = "發生錯誤：" + str(e)

    # text is not a command
    else:
        result = command_handler(text)

    # send response
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=result)]
            )
        )

def handle_image_message(event) -> None:
    """
    處理圖片訊息的函數。

    當聊天模式為以圖搜尋時，上傳圖片後會立刻進行電影猜測，並且刪除所有已上傳的圖片。

    黨聊天模式為其他時，上傳圖片後會回傳已上傳圖片數量。
    """
    uploaded_images = []
    UPLOAD_FOLDER="uploads"
    
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(
            message_id=event.message.id
        )
        with tempfile.NamedTemporaryFile(
            dir=UPLOAD_FOLDER, prefix="", delete=False
        ) as tf:
            tf.write(message_content)
            tempfile_path = tf.name

    original_file_name = os.path.basename(tempfile_path + '.jpg')
    new_file_path = UPLOAD_FOLDER + "/" + original_file_name
    os.replace(tempfile_path, new_file_path)

    uploaded_images.append(new_file_path)

    uploaded_image_count = len(os.listdir(user_image_path))
    if chat_mode == ChatMode.GUESS_MOVIE:
        result = gemini.guess_movie(uploaded_images)
        _clean_user_images()
    else:
        result = f"上傳完成，已上傳 {uploaded_image_count} 張圖片"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=result)],
            )
        )