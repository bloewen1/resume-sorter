from flask import Flask, render_template, request, jsonify
import os
from io import BytesIO
from docx import Document
import PyPDF2
import zipfile
import openpyxl
import re
from datetime import datetime

app = Flask(__name__)
keywords = ["Python", "Javascript", "SQL", "HTML", "Oracle"]
# If there's an existing workbook, open it, otherwise make a new one
try:
    wb = openpyxl.load_workbook("resumes.xlsx")
except:
    wb = openpyxl.Workbook()

if "Resumes" in wb.sheetnames:
    ws = wb["Resumes"]
else:
    ws = wb.create_sheet("Resumes")
    ws.append(["Filename", "Keywords"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def rank_files():
    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        filename, keywords_str = row
        keys = keywords_str.split(', ') if keywords_str else []
        data.append({"filename": filename, "keywords": keys})
    
    # Get the list of search words from the form
    search_words = request.form.getlist('search_word')

    # Check if search words are provided
    if len(search_words) == 0:
        search_words = keywords

    results = {}
    for entry in data:
        filename = entry["filename"]
        keys = entry["keywords"]
        found_count = sum(word.lower() in [kw.lower() for kw in keys] for word in search_words)
        total_words = len(search_words)
        score = round((found_count / total_words) * 100)
        results[filename] = {"score": score, "date": get_date_from_filename(filename)}

     # Sort the results based on the score in descending order
    sorted_results = dict(sorted(results.items(), key=lambda item: (item[1]['score'], item[1]['date']), reverse=True))
    
    # Extract file names and scores separately
    file_names = list(sorted_results.keys())
    scores = [sorted_results[filename]['score'] for filename in file_names]

    # Zip the file names and scores together
    file_scores = list(zip(file_names, scores))

    return jsonify(file_scores)

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

    # Process each file in the zip
    for filename, file_content in file_contents.items():
        if filename.endswith('.docx'):
            parsed_content = parse_word_document(file_content)
        elif filename.endswith('.pdf'):
            parsed_content = parse_pdf(file_content)
        else:
            continue

        found_words = []
        for key in keywords:
            if key.lower() in parsed_content.lower():
                found_words.append(key)
        file_keywords = ', '.join(found_words)

        existing_row_index = None
        for row_index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if row[0] == filename:
                existing_row_index = row_index
                break

        if existing_row_index:
            # Replace existing row if filename already exists
            ws.delete_rows(existing_row_index)
            new_row = [filename, file_keywords]
            ws.insert_rows(existing_row_index, amount=1)
            for col_index, value in enumerate(new_row, start=1):
                ws.cell(row=existing_row_index, column=col_index, value=value)
        else:
            # Add new row if filename doesn't exist
            ws.append([filename, file_keywords])

    wb.save("resumes.xlsx")

    return jsonify(True)

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

def get_date_from_filename(filename):
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    if match:
        date_str = match.group(0)
        return datetime.strptime(date_str, '%Y-%m-%d')
    return datetime.min  # Return a default date if no match is found

if __name__ == '__main__':
    # Set the maximum content length for file uploads to 250 MB
    app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
    app.run(debug=True)

