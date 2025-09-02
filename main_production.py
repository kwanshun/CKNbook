import os
import logging
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tone_toner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['ENV'] = 'production'
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# CORS configuration - restrict in production
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)
limiter.init_app(app)

# Configure Gemini API
api_key = os.getenv('API_KEY')
if not api_key:
    logger.error("ERROR: API_KEY not found in environment variables")
    exit(1)

logger.info("Configuring Gemini API...")
genai.configure(api_key=api_key)

def load_system_prompt():
    """Load the system prompt from file"""
    try:
        with open('prompts/system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("System prompt file not found")
        return "You are a helpful assistant that rewrites text."

def load_response_prompt():
    """Load the response prompt from file"""
    try:
        with open('prompts/response_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Response prompt file not found")
        return "You are a helpful assistant that generates effective responses."

def validate_input(paragraph, tone, language):
    """Validate user input"""
    if not paragraph or len(paragraph.strip()) == 0:
        return False, "段落內容不能為空"
    
    if len(paragraph) > 2000:
        return False, "段落內容過長，請限制在2000字元以內"
    
    valid_tones = ['活潑輕鬆', '溫暖', '專業', '謙虛', '幽默']
    if tone not in valid_tones:
        return False, "無效的語調選項"
    
    valid_languages = ['廣東話', '普通話', '英文', '西班牙文']
    if language not in valid_languages:
        return False, "無效的語言選項"
    
    # Basic content filtering - allow common punctuation and Chinese characters
    # Allow: word chars, whitespace, CJK chars, common punctuation including smart quotes
    if re.search(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2000-\u206f\u2010-\u2027\u2030-\u205f.,!?;:()""\'\-–—/\\&%@#*+<>=[\]{}|~`]', paragraph):
        return False, "包含不允許的字元"
    
    return True, ""

def fine_tune_text(paragraph, tone, language):
    """Fine-tune the paragraph using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = load_system_prompt()
        user_prompt = f"""
        [Tone]: {tone}
        [Language or Dialect]: {language}
        
        原文段落:
        {paragraph}
        
        請根據上述語調和語言要求，重寫這個段落為三個不同的選項。
        """
        
        full_prompt = system_prompt + "\n\n" + user_prompt
        
        logger.info(f"Processing request - Tone: {tone}, Language: {language}")
        response = model.generate_content(full_prompt)
        
        if response.text:
            logger.info("Successfully generated response")
            return response.text
        else:
            logger.warning("Empty response from API")
            return "錯誤: API 回應為空"
        
    except Exception as e:
        logger.error(f"Error in fine_tune_text: {str(e)}")
        return f"錯誤: 服務暫時不可用，請稍後再試"

def generate_effective_response(text, image_base64, tone):
    """Generate effective responses using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response_prompt = load_response_prompt()
        
        # Find relevant knowledge content based on user input
        relevant_knowledge = find_relevant_knowledge(text)
        
        user_prompt = f"""
        用戶輸入：{text}
        語調要求：{tone}
        相關書本知識：{relevant_knowledge}
        """
        
        if image_base64:
            user_prompt += f"\n\n圖片已上傳，請分析圖片內容並納入回應考慮。"
        
        full_prompt = response_prompt + "\n\n" + user_prompt
        
        print(f"Generating effective response with tone: {tone}...")
        print(f"Relevant knowledge found: {len(relevant_knowledge)} characters")
        
        if image_base64:
            # Handle image analysis
            image_data = {"mime_type": "image/jpeg", "data": image_base64}
            response = model.generate_content([full_prompt, image_data])
        else:
            response = model.generate_content(full_prompt)
        
        print(f"Response generation: {response.text[:200]}...")
        
        if response.text:
            return response.text
        else:
            return "錯誤: API 回應為空"
        
    except Exception as e:
        print(f"Error in generate_effective_response: {str(e)}")
        return f"錯誤: {str(e)}"

def find_relevant_knowledge(user_input):
    """Find relevant knowledge content based on user input"""
    import glob
    import os
    import re
    
    # Keywords that might indicate specific topics
    keywords = {
        '維生素': ['維生素', 'vitamin', '維他命'],
        '蛋白質': ['蛋白質', 'protein', '氨基酸'],
        '脂肪': ['脂肪', 'fat', '油', '膽固醇'],
        '碳水化合物': ['碳水化合物', 'carb', '糖', '澱粉'],
        '礦物質': ['礦物質', 'mineral', '鈣', '鐵', '鋅'],
        '早餐': ['早餐', 'breakfast', '早上'],
        '營養補充': ['營養補充', 'supplement', '補充劑'],
        '烹調': ['烹調', 'cooking', '煮', '蒸', '炒'],
        '健康': ['健康', 'health', '養生'],
        '疾病': ['疾病', 'disease', '病', '症狀']
    }
    
    # Find matching topics
    relevant_topics = []
    user_input_lower = user_input.lower()
    
    for topic, topic_keywords in keywords.items():
        for keyword in topic_keywords:
            if keyword.lower() in user_input_lower:
                relevant_topics.append(topic)
                break
    
    # If no specific topics found, use general knowledge
    if not relevant_topics:
        relevant_topics = ['general']
    
    # Load relevant chapter content
    relevant_content = []
    
    # Always include some general knowledge
    try:
        with open('book_knowledge.txt', 'r', encoding='utf-8') as f:
            general_knowledge = f.read()
            relevant_content.append(f"一般營養知識：\n{general_knowledge}")
    except:
        pass
    
    # Load specific chapter content based on topics
    knowledge_files = glob.glob('knowledge/*.md')
    
    for file_path in knowledge_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if this chapter is relevant to the user's input
                is_relevant = False
                for topic in relevant_topics:
                    if topic in content or any(keyword in content for keyword in keywords.get(topic, [])):
                        is_relevant = True
                        break
                
                if is_relevant:
                    # Extract chapter title and key content
                    lines = content.split('\n')
                    title = lines[0] if lines else "未知章節"
                    # Get first few paragraphs for context
                    key_content = '\n'.join(lines[1:min(10, len(lines))])
                    relevant_content.append(f"{title}\n{key_content}")
                    
        except Exception as e:
            print(f"Error reading knowledge file {file_path}: {e}")
            continue
    
    # If no specific content found, try to find chapters that might be relevant
    if len(relevant_content) <= 1:  # Only general knowledge
        # Load a few random chapters to provide context
        import random
        knowledge_files = glob.glob('knowledge/*.md')
        if knowledge_files:
            selected_files = random.sample(knowledge_files, min(3, len(knowledge_files)))
            for file_path in selected_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        title = lines[0] if lines else "未知章節"
                        key_content = '\n'.join(lines[1:min(8, len(lines))])
                        relevant_content.append(f"{title}\n{key_content}")
                except:
                    continue
    
    return "\n\n---\n\n".join(relevant_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
@limiter.limit("5 per minute")
def process_text():
    try:
        if not request.is_json:
            return jsonify({'error': '請求格式錯誤'}), 400
            
        data = request.json
        paragraph = data.get('paragraph', '').strip()
        tone = data.get('tone', '')
        language = data.get('language', '')
        
        # Validate input
        is_valid, error_msg = validate_input(paragraph, tone, language)
        if not is_valid:
            logger.warning(f"Invalid input: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Log request (without sensitive data)
        logger.info(f"Processing request - Length: {len(paragraph)}, Tone: {tone}, Language: {language}")
        
        result = fine_tune_text(paragraph, tone, language)
        
        return jsonify({'result': result})
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}")
        return jsonify({'error': '處理時發生錯誤，請稍後再試'}), 500

@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({'error': '請求過於頻繁，請稍後再試'}), 429

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({'error': '頁面不存在'}), 404

@app.errorhandler(500)
def internal_error_handler(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': '服務器內部錯誤'}), 500

if __name__ == '__main__':
    # This should only be used for development
    # In production, use a proper WSGI server like Gunicorn
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
