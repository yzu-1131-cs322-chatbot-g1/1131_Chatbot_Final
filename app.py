from flask import Flask, render_template

# custom modules
from modules.config import config
from modules import line


app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE bot 驗證 Webhook URL 用的 callback
    """
    return line.callback(app.logger)


@line.handler.add(line.MessageEvent, message=line.TextMessageContent)
def handle_text_message(event):
    """
    LINE bot 接收並處理文字訊息
    """
    return line.handle_text_message(event)


@line.handler.add(line.MessageEvent, message=line.ImageMessageContent)
def handle_image_message(event):
    """
    LINE bot 接收並處理圖片訊息
    """
    return line.handle_image_message(event)

@line.handler.add(line.MessageEvent, message=line.AudioMessageContent)
def handle_audio_message(event):
    """
    LINE bot 接收並處理audio訊息
    """
    return line.handle_audio_message(event)

@app.route('/')
def hello_world():
    """
    網頁測試，測試是否能讀取 config 並回傳 template
    """
    return render_template(
        template_name_or_list='index.html',
        msg=config['test']['message']
    )


if __name__ == '__main__':
    app.run()
