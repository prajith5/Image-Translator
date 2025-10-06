from flask import Flask, request, render_template, redirect
import os
import easyocr
from langdetect import detect, LangDetectException
from googletrans import Translator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def initialize_easyocr(languages):
    try:
        reader = easyocr.Reader(languages, gpu=False)
        return reader
    except Exception as e:
        print(f"Error initializing EasyOCR with languages {languages}: {e}")
        return None

def extract_text_from_image(image_path, reader):
    try:
        result = reader.readtext(image_path, detail=0)
        extracted_text = ' '.join(result)
        print(f"Extracted text: {extracted_text}")
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}")
        return ""

def detect_language(text):
    try:
        language = detect(text)
        print(f"Detected language: {language}")
        return language
    except LangDetectException as e:
        print(f"Error detecting language: {e}")
        return "en"

def translate_text(text, src_lang, dest_lang):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        print(f"Translated text: {translated.text}")
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return "Translation Error"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = "uploaded_image.jpg"  
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
           
            selected_languages = request.form.getlist('languages[]')
            print(f"Selected languages: {selected_languages}")
         
            reader = initialize_easyocr(selected_languages)
            if reader is None:
                return "Error: Failed to initialize EasyOCR. Please check the server logs for more details."
            
            
            extracted_text = extract_text_from_image(filepath, reader)
            if extracted_text == "":
                return "Error: Failed to extract text from the image."
            detected_language = detect_language(extracted_text)
            if detected_language not in selected_languages:
                detected_language = 'en'  
            
            dest_lang = request.form.get('dest_lang', 'en')  
            translated_text = translate_text(extracted_text, detected_language, dest_lang)
            
            return render_template('result.html', 
                                    extracted_text=extracted_text, 
                                    language_id=detected_language, 
                                    confidence="N/A",  
                                    translated_text=translated_text, 
                                    dest_lang=dest_lang, 
                                    image_path=filepath)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
