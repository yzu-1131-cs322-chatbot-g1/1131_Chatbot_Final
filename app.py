from flask import Flask, render_template
from modules.config import config
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template(
        template_name_or_list='index.html',
        msg=config['test']['message']
    )


if __name__ == '__main__':
    app.run()
