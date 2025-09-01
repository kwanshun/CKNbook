# Example: Tone-Toner WITHOUT SECRET_KEY
from flask import Flask, session, request, jsonify

app = Flask(__name__)
# app.secret_key = None  # ❌ NO SECRET KEY SET

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    tone = data.get('tone')
    
    try:
        # Try to remember user's preference
        session['last_tone'] = tone  # ❌ THIS WILL FAIL!
    except RuntimeError as e:
        print(f"ERROR: {e}")
        # Flask throws: "The session is unavailable because no secret key was set"
    
    result = f"Generated text with {tone} tone"
    
    return jsonify({
        'result': result,
        'message': '❌ Cannot save preferences - no secret key!'
    })

# What happens:
# 1. Flask cannot create secure sessions
# 2. Any session operations crash your app
# 3. Users lose preferences between requests

