import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
api_key = os.getenv('API_KEY')
if not api_key:
    print("ERROR: API_KEY not found in .env file")
    exit(1)
print(f"Configuring Gemini with API key: {api_key[:10]}...")
genai.configure(api_key=api_key)

def load_system_prompt():
    """Load the system prompt from file"""
    with open('prompts/system_prompt.txt', 'r', encoding='utf-8') as f:
        return f.read()

def fine_tune_text(paragraph, tone, language):
    """Fine-tune the paragraph using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = load_system_prompt()
        user_prompt = f"""
        [Tone]: {tone}
        [Language or Dialect]: {language}
        
        原文段落:
        {paragraph}
        
        請根據上述語調和語言要求，重寫這個段落為三個不同的選項。
        """
        
        full_prompt = system_prompt + "\n\n" + user_prompt
        
        print(f"Sending prompt to Gemini API...")
        response = model.generate_content(full_prompt)
        print(f"Received response: {response.text[:200]}...")
        
        if response.text:
            return response.text
        else:
            return "錯誤: API 回應為空"
        
    except Exception as e:
        print(f"Error in fine_tune_text: {str(e)}")
        return f"錯誤: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    try:
        data = request.json
        paragraph = data.get('paragraph', '')
        tone = data.get('tone', '')
        language = data.get('language', '')
        
        if not paragraph or not tone or not language:
            return jsonify({'error': '請填寫所有必要欄位'}), 400
        
        result = fine_tune_text(paragraph, tone, language)
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

