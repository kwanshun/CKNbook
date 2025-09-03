import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json

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

def load_book_knowledge():
    """Load the nutrition book knowledge from file"""
    try:
        with open('book_knowledge.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: book_knowledge.txt not found")
        return ""

def load_quiz_prompt():
    """Load the quiz prompt from file"""
    try:
        with open('prompts/quiz_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: quiz_prompt.txt not found")
        return ""

def load_response_prompt():
    """Load the response prompt from file"""
    try:
        with open('prompts/response_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: response_prompt.txt not found")
        return ""

def get_chapter_content(day_number):
    """Get content from the knowledge directory for a specific day"""
    import glob
    import os
    
    # Try to find the chapter file with different naming patterns
    patterns = [
        f"knowledge/第{day_number}天：*.md",
        f"knowledge/第 {day_number} 天：*.md",
        f"knowledge/第{day_number}天*.md",
        f"knowledge/第 {day_number} 天*.md"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {files[0]}: {e}")
                continue
    
    return f"第{day_number}課的內容未找到"

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

def generate_quiz(day_number):
    """Generate quiz questions and answers using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        quiz_prompt = load_quiz_prompt()
        chapter_content = get_chapter_content(day_number)
        
        user_prompt = f"""
        請根據以下章節內容生成測驗題：
        
        章節內容：
        {chapter_content}
        
        請確保使用正確的章節編號：第{day_number}天
        """
        
        full_prompt = quiz_prompt + "\n\n" + user_prompt
        
        print(f"Generating quiz for day {day_number}...")
        response = model.generate_content(full_prompt)
        print(f"Quiz response: {response.text[:200]}...")
        
        if response.text:
            # Try to parse as JSON
            try:
                # Clean up the response text - remove markdown code blocks if present
                clean_text = response.text.strip()
                
                # Remove markdown code blocks more thoroughly
                if '```json' in clean_text:
                    # Extract content between ```json and ```
                    start = clean_text.find('```json') + 7
                    end = clean_text.rfind('```')
                    if end > start:
                        clean_text = clean_text[start:end].strip()
                elif clean_text.startswith('```') and clean_text.endswith('```'):
                    # Remove ``` at start and end
                    clean_text = clean_text[3:-3].strip()
                
                print(f"Cleaned text for JSON parsing: {clean_text[:100]}...")
                
                quiz_data = json.loads(clean_text)
                print("Successfully parsed JSON response")
                return quiz_data  # Return the actual JSON object, not a string
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print("Falling back to plain text response")
                return response.text
        else:
            return "錯誤: API 回應為空"
        
    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return f"錯誤: {str(e)}"

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
        
        請生成回應，使用以下JSON格式：
        {{
            "feeling": "對用戶分享內容的直接反應和感受，使用表情符號增加親切感，字數在30字內",
            "knowledge": "結合《吃的營養科學觀》的相關知識，分析營養價值，提出建議，鼓勵成員分享，字數在120字內"
        }}
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
            # Try to parse as JSON
            try:
                # Clean up the response text - remove markdown code blocks if present
                clean_text = response.text.strip()
                
                # Remove markdown code blocks more thoroughly
                if '```json' in clean_text:
                    # Extract content between ```json and ```
                    start = clean_text.find('```json') + 7
                    end = clean_text.rfind('```')
                    if end > start:
                        clean_text = clean_text[start:end].strip()
                elif clean_text.startswith('```') and clean_text.endswith('```'):
                    # Remove ``` at start and end
                    clean_text = clean_text[3:-3].strip()
                
                print(f"Cleaned text for JSON parsing: {clean_text[:100]}...")
                
                response_data = json.loads(clean_text)
                print("Successfully parsed JSON response")
                return response_data  # Return the actual JSON object, not a string
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print("Falling back to plain text response")
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
    
    # Enhanced keywords that might indicate specific topics
    keywords = {
        '維生素': ['維生素', 'vitamin', '維他命', '維他命c', '維他命b', 'b族維生素'],
        '蛋白質': ['蛋白質', 'protein', '氨基酸', '必需氨基酸', '必需氨基酸', '氨基酸種類'],
        '脂肪': ['脂肪', 'fat', '油', '膽固醇', '脂肪酸'],
        '碳水化合物': ['碳水化合物', 'carb', '糖', '澱粉', '醣類'],
        '礦物質': ['礦物質', 'mineral', '鈣', '鐵', '鋅', '鎂'],
        '早餐': ['早餐', 'breakfast', '早上', '早飯'],
        '營養補充': ['營養補充', 'supplement', '補充劑', '營養品'],
        '烹調': ['烹調', 'cooking', '煮', '蒸', '炒', '料理'],
        '健康': ['健康', 'health', '養生', '保健'],
        '疾病': ['疾病', 'disease', '病', '症狀', '治療'],
        '年輕': ['年輕', '衰老', '老化', '抗衰老', '保持年輕'],
        '氨基酸': ['氨基酸', '必需氨基酸', '非必需氨基酸', '氨基酸種類', '氨基酸數量'],
        '數字': ['數字', '數量', '幾種', '多少種', '幾種', '數量'],
        '天': ['天', '日', '第幾天', '第幾日']
    }
    
    # Find matching topics
    relevant_topics = []
    user_input_lower = user_input.lower()
    
    # First pass: look for exact matches
    for topic, topic_keywords in keywords.items():
        for keyword in topic_keywords:
            if keyword.lower() in user_input_lower:
                relevant_topics.append(topic)
                break
    
    # Second pass: look for specific patterns like "第X天" or "必需氨基酸"
    if '第' in user_input and '天' in user_input:
        relevant_topics.append('天')
    
    if '必需氨基酸' in user_input or '氨基酸' in user_input:
        relevant_topics.append('氨基酸')
        relevant_topics.append('蛋白質')
    
    if any(word in user_input for word in ['數字', '數量', '幾種', '多少種']):
        relevant_topics.append('數字')
    
    # If no specific topics found, use general knowledge
    if not relevant_topics:
        relevant_topics = ['general']
    
    print(f"Detected topics: {relevant_topics}")
    
    # Load relevant chapter content
    relevant_content = []
    
    # Always include some general knowledge
    try:
        with open('book_knowledge.txt', 'r', encoding='utf-8') as f:
            general_knowledge = f.read()
            relevant_content.append(f"一般營養知識：\n{general_knowledge}")
            print("✓ Loaded general knowledge")
    except Exception as e:
        print(f"✗ Error loading general knowledge: {e}")
    
    # Load specific chapter content based on topics
    knowledge_files = glob.glob('knowledge/*.md')
    print(f"Found {len(knowledge_files)} knowledge files")
    
    # Priority: load chapters that are most relevant
    chapter_scores = {}
    
    for file_path in knowledge_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Calculate relevance score
                score = 0
                for topic in relevant_topics:
                    if topic in content:
                        score += 10
                    if topic == '氨基酸' and ('必需氨基酸' in content or '氨基酸種類' in content):
                        score += 20  # Bonus for amino acid specific content
                    if topic == '數字' and any(word in content for word in ['22種', '8種', '14種']):
                        score += 15  # Bonus for specific numbers
                    if topic == '天' and any(word in content for word in ['第3天', '第三天', '第三日']):
                        score += 15  # Bonus for specific days
                
                # Check for exact keyword matches
                for topic, topic_keywords in keywords.items():
                    for keyword in topic_keywords:
                        if keyword in content:
                            score += 5
                
                if score > 0:
                    chapter_scores[file_path] = score
                    
        except Exception as e:
            print(f"✗ Error reading knowledge file {file_path}: {e}")
            continue
    
    # Sort chapters by relevance score and load the most relevant ones
    sorted_chapters = sorted(chapter_scores.items(), key=lambda x: x[1], reverse=True)
    
    for file_path, score in sorted_chapters[:5]:  # Load top 5 most relevant
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                title = lines[0] if lines else "未知章節"
                # Get more content for highly relevant chapters
                key_content = '\n'.join(lines[1:min(15, len(lines))])
                relevant_content.append(f"{title}\n{key_content}")
                print(f"✓ Loaded relevant content from: {os.path.basename(file_path)} (score: {score})")
                    
        except Exception as e:
            print(f"✗ Error reading knowledge file {file_path}: {e}")
            continue
    
    # If no specific content found, try to find chapters that might be relevant
    if len(relevant_content) <= 1:  # Only general knowledge
        print("No specific content found, loading random chapters...")
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
                        print(f"✓ Loaded random content from: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"✗ Error reading random file {file_path}: {e}")
                    continue
    
    final_content = "\n\n---\n\n".join(relevant_content)
    print(f"\nTotal knowledge content loaded: {len(final_content)} characters")
    print(f"Number of content sections: {len(relevant_content)}")
    
    return final_content

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

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/effective-reply')
def effective_reply():
    return render_template('effective_reply.html')

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz_route():
    try:
        data = request.json
        day = data.get('day', '')
        
        if not day:
            return jsonify({'error': '請選擇天數'}), 400
        
        result = generate_quiz(day)
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-response', methods=['POST'])
def generate_response_route():
    try:
        data = request.json
        text = data.get('text', '')
        image = data.get('image', '')
        tone = data.get('tone', '')
        
        if not text or not tone:
            return jsonify({'error': '請填寫所有必要欄位'}), 400
        
        result = generate_effective_response(text, image, tone)
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

