from flask import Flask, render_template, request, jsonify
import os
from io import BytesIO
from docx import Document
import PyPDF2
import zipfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_files():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    zip_file = request.files['file']

    if not zipfile.is_zipfile(zip_file):
        return jsonify({"error": "Invalid zip file"})

    try:
        file_contents = {}
        with zipfile.ZipFile(zip_file, 'r') as zip_archive:
            for filename in zip_archive.namelist():
                with zip_archive.open(filename) as file:
                    file_contents[filename] = file.read()
    except zipfile.BadZipFile:
        return jsonify({"error": "Bad Zip File"})

    search_words = request.form.getlist('search_word')

    if not search_words:
        return jsonify({"error": "No search words provided"})

    results = {}
    counter = 0
    for filename, file_content in file_contents.items():
        counter += 1
        if filename.endswith('.docx'):
            parsed_content = parse_word_document(file_content)
        elif filename.endswith('.pdf'):
            parsed_content = parse_pdf(file_content)
        else:
            continue

        found_count = sum(word.lower() in parsed_content.lower() for word in search_words)
        total_words = len(search_words)
        score = round((found_count / total_words) * 100, 2)

        results[filename] = {"score": score}


    # Sort results by score in descending order
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]['score'], reverse=True))

    # Extract file names and scores separately
    file_names = list(sorted_results.keys())
    scores = [sorted_results[filename]['score'] for filename in file_names]

    # Zip the file names and scores together
    file_scores = list(zip(file_names, scores))

    return jsonify(file_scores)

def parse_word_document(file_content):
    doc = Document(BytesIO(file_content))
    content = ""
    for paragraph in doc.paragraphs:
        content += paragraph.text + "\n"
    return content

def parse_pdf(file_content):
    content = ""
    try:
        pdf_file = PyPDF2.PdfReader(BytesIO(file_content))
        for page_num in range(len(pdf_file.pages)):
            page = pdf_file.pages[page_num]
            content += page.extract_text() + "\n"
    except Exception as e:
        print("Error parsing PDF: ", e)
    return content

if __name__ == '__main__':
    app.run(debug=True)
