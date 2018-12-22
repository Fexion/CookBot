import os
from dialog import Dialog
from flask import Flask, request, render_template, send_from_directory


app = Flask(__name__)

dialog_flow = Dialog()


@app.route('/')
def hello():
    return render_template('idle.html')


@app.route('/processM', methods=['POST'])
def process_message():
    text = request.form['user_text']
    return dialog_flow.process_dialog(text)


@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'icon/favicon.ico')
    except Exception as ex:
        return ex
