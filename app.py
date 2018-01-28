import os
from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.form['api_key']
    if api_key != 'huehue':
        return
    file = request.files['d']
    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    file.save(f)

    return f"http://localhost/uploads/{file.filename}"

while True:
    app.run()
    print("Restarting...")