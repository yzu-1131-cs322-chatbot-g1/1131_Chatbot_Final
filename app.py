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
def message_text(event):
    """
    LINE bot 接收並處理文字訊息
    """
    return line.message_text(event)

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
