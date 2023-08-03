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
    # Check if 'file' is present in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    # Get the uploaded zip file
    zip_file = request.files['file']

    # Check if the uploaded file is a valid zip file
    if not zipfile.is_zipfile(zip_file):
        return jsonify({"error": "Invalid zip file"})

    try:
        # Extract the contents of the zip file
        file_contents = {}
        with zipfile.ZipFile(zip_file, 'r') as zip_archive:
            for filename in zip_archive.namelist():
                with zip_archive.open(filename) as file:
                    file_contents[filename] = file.read()
    except zipfile.BadZipFile:
        return jsonify({"error": "Bad Zip File"})

    # Get the list of search words from the form
    search_words = request.form.getlist('search_word')

    # Check if search words are provided
    if not search_words:
        return jsonify({"error": "No search words provided"})

    # Process each file in the zip and calculate scores
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
        score = (found_count / total_words) * 100

        results[filename] = {"score": score}
    
    # Sort the results based on the score in descending order
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]['score'], reverse=True))
    return jsonify(sorted_results)

def parse_word_document(file_content):
    # Parse the content of a Word document
    doc = Document(BytesIO(file_content))
    content = ""
    for paragraph in doc.paragraphs:
        content += paragraph.text + "\n"
    return content

def parse_pdf(file_content):
    # Parse the content of a PDF document
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
    # Set the maximum content length for file uploads to 250 MB
    app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
    app.run(debug=True)

