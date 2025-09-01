# Example: Tone-Toner WITH SECRET_KEY
from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"  # SECURE

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    tone = data.get('tone')
    
    # Remember user's preference securely
    session['last_tone'] = tone
    
    # Process with AI...
    result = f"Generated text with {tone} tone"
    
    return jsonify({
        'result': result,
        'message': f'✅ Securely saved your preference for {tone}'
    })

@app.route('/get-preference')
def get_preference():
    last_tone = session.get('last_tone', '輕鬆')
    return jsonify({'last_tone': last_tone})

# What happens in browser:
# Cookie: session=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9... (ENCRYPTED & SIGNED)
# ✅ Attacker cannot read or modify this cookie

