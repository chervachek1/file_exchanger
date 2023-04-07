from flask import Flask, request, url_for, send_file, render_template, flash, redirect
import os
import time
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        start_time = time.time()
        file.save(os.path.join('files', filename))
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        file_size = os.path.getsize(os.path.join('files', filename))
        data = {
            'duration': duration,
            'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
            'file_size': file_size,
            'file_link': url_for('download_file', filename=filename),
        }
        return render_template('download.html', data=data)
    return render_template('upload.html')


@app.route('/download/<filename>')
def download_file(filename):
    path = f'files/{filename}'
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
