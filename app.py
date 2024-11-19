from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return 'No selected file'

    filename = secure_filename(pdf_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(filepath)
    return redirect(url_for('viewer', filename=filename))

@app.route('/viewer/<filename>')
def viewer(filename):
    return render_template('viewer.html', filename=filename)

@app.route('/process', methods=['POST'])
def process_pdf():
    data = request.get_json()
    filename = data['filename']
    pages_to_keep = data['pagesToKeep']  # List of page indices (starting from 1)

    input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'modified_' + filename)

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page_num in pages_to_keep:
        writer.add_page(reader.pages[int(page_num) - 1])

    with open(output_pdf_path, 'wb') as f:
        writer.write(f)

    return jsonify(url=url_for('download_file', filename='modified_' + filename))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
