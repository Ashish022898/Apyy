from flask import Flask, render_template, request, send_file
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import PyPDF2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/files/'
app.config['CONVERTED_FOLDER'] = './converted_files/'

def count_words_chars(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
        word_count = len(text.split())
        char_count = len(text)
    return word_count, char_count, text

def create_pdf(file_path, word_count, char_count, text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Word Count: {word_count}")
    c.drawString(100, 730, f"Character Count: {char_count}")
    c.drawString(100, 700, "Text:")
    c.drawString(100, 680, text)
    c.save()
    buffer.seek(0)
    return buffer

def pdf_to_text(file_path):
    text = ""
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()
    return text

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    uploaded_file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(file_path)
    if file_path.endswith('.pdf'):
        text = pdf_to_text(file_path)
    else:
        with open(file_path, 'r') as txt_file:
            text = txt_file.read()
    word_count, char_count, _ = count_words_chars(file_path)
    pdf_buffer = create_pdf(file_path, word_count, char_count, text)
    converted_file_name = uploaded_file.filename.replace('.txt', '.pdf')
    if not converted_file_name.endswith('.pdf'):
        converted_file_name += '.pdf'
    converted_file_path = os.path.join(app.config['CONVERTED_FOLDER'], converted_file_name)
    if not os.path.exists(app.config['CONVERTED_FOLDER']):
        os.makedirs(app.config['CONVERTED_FOLDER'])
    with open(converted_file_path, 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())
    return render_template('convert.html', converted_file_name=converted_file_name)

if __name__ == '__main__':
    app.run(debug=True)
