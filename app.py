import sys
import subprocess
import json
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# 1. APP SETUP AND CONFIGURATION

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' 
users_db = {
    'Abhi@gmail.com': 'Abhi123',
}
MOODFOOD_ANSWERS = {
    "STRESSED": {
        "text": ("**Focus on Magnesium-Rich Foods!** Magnesium helps calm your nervous system and regulate stress hormones. "
                 "**Suggestion:** Try a snack of a **handful of almonds** or a **square of dark chocolate** (70%+ cacao). "
                 "For dinner, opt for a **salmon fillet** with spinach."),
        "sources": [
            {"title": "The Role of Magnesium in Stress", "uri": "https://example.com/magnesium-stress-source-1"},
            {"title": "Omega-3s and Anxiety Relief", "uri": "https://example.com/omega-3s-source-2"}
        ]
    },
    "TIRED": {
        "text": ("**Boost with Iron and B12!** These nutrients are essential for red blood cell health and sustained energy delivery "
                 "to your brain, fighting fatigue without relying on sugar crashes. "
                 "**Suggestion:** A bowl of **oatmeal with berries** and a glass of fortified milk, "
                 "or a **lentil soup** for lunch to keep you going strong."),
        "sources": [
            {"title": "Complex Carbs for Stable Energy", "uri": "https://example.com/carbs-energy-source-1"},
            {"title": "Iron and Fatigue", "uri": "https://example.com/iron-fatigue-source-2"}
        ]
    },
    "HAPPY": {
        "text": ("**Maintain Wellness with Probiotics!** When feeling good, focus on gut health which produces most of the body's serotonin. "
                 "**Suggestion:** Enjoy a small bowl of **Greek yogurt** with a banana and a drizzle of honey. The yogurt provides probiotics, "
                 "and the banana offers mood-lifting tryptophan."),
        "sources": [
            {"title": "Gut Health and Mood", "uri": "https://example.com/gut-mood-source-1"},
            {"title": "Tryptophan and Serotonin", "uri": "https://example.com/tryptophan-source-2"}
        ]
    },
    "SAD": {
        "text": ("**Elevate Mood with Omega-3 Fatty Acids!** Omega-3s are crucial components of brain cell membranes and are linked to improved mood regulation. "
                 "**Suggestion:** Have a quick snack of **walnuts or flaxseeds**, or incorporate a source of fatty fish like **sardines or salmon** into your next meal."),
        "sources": [
            {"title": "Omega-3s and Depression", "uri": "https://example.com/omega-3-sadness-source-1"},
            {"title": "Brain Cell Function", "uri": "https://example.com/brain-cell-source-2"}
        ]
    },
    "HUNGRY": {
        "text": ("**Achieve Satiety with Fiber and Protein!** This combination digests slowly, stabilizing blood sugar and keeping you full for hours. "
                 "**Suggestion:** An ideal snack is **apple slices dipped in peanut butter** or a **hard-boiled egg** with whole-wheat toast. Avoid simple sugars."),
        "sources": [
            {"title": "Fiber and Satiety", "uri": "https://example.com/fiber-satiety-source-1"},
            {"title": "Protein for Appetite Control", "uri": "https://example.com/protein-appetite-source-2"}
        ]
    }
}

MIND_MINUTES_ANSWERS = {
    "QUICKCALM": {
        "text": ("**Box Breathing (4-4-4-4):** This simple technique rapidly calms the nervous system. "
                 "1. Inhale slowly for 4 seconds. "
                 "2. Hold your breath for 4 seconds. "
                 "3. Exhale slowly for 4 seconds. "
                 "4. Hold your breath (lungs empty) for 4 seconds. Repeat 4 times."),
        "sources": [
            {"title": "Benefits of Box Breathing", "uri": "https://example.com/box-breathing-source-1"}
        ]
    },
    "DEEPFOCUS": {
        "text": ("**The Grounding 5-4-3-2-1 Technique:** This exercise pulls your mind away from distractions by engaging your senses. "
                 "1. **5** things you can see. "
                 "2. **4** things you can touch. "
                 "3. **3** things you can hear. "
                 "4. **2** things you can smell. "
                 "5. **1** thing you can taste."),
        "sources": [
            {"title": "Grounding Techniques for Focus", "uri": "https://example.com/grounding-focus-source-1"}
        ]
    },
    "SLEEPPREP": {
        "text": ("**Progressive Muscle Relaxation (PMR):** Lying down, systematically tense and then completely relax each muscle group. "
                 "1. Start with your toes (curl and release). "
                 "2. Move up to calves, thighs, and abdomen. "
                 "3. Finish with hands, arms, shoulders, and face. This releases built-up tension for sleep."),
        "sources": [
            {"title": "PMR for Insomnia", "uri": "https://example.com/pmr-sleep-source-1"}
        ]
    },
    "ENERGYBOOST": {
        "text": ("**Mindful Movement and Hydration:** A quick change in posture and breathing can restore alertness. "
                 "1. Stand up and stretch your arms high above your head. "
                 "2. Take 5 deep, cleansing breaths. "
                 "3. Drink a full glass of water immediately. This combo fights brain fog and restarts the body."),
        "sources": [
            {"title": "Quick Desk Stretches", "uri": "https://example.com/desk-stretches-source-1"}
        ]
    }
}

# 3. ROUTE DEFINITIONS
# Route for the Login/Sign Up Page (Uses index.html)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Route to Handle Login Submission
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if email in users_db and users_db[email] == password:
        session['user'] = email
        return redirect(url_for('select_exercise'))
    else:
        return "Login Failed. Invalid credentials.", 401

# Route to Handle Sign Up Submission
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    
    if email in users_db:
        return "Sign Up Failed. User already exists.", 409

    users_db[email] = password
    session['user'] = email
    
    return redirect(url_for('select_exercise'))

# Route for Exercise Selection and Main Menu Display (Renders main_menu.html)
@app.route('/select_exercise')
def select_exercise():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session['user']
    
    return render_template('main_menu.html', user_email=user_email)

# Route to launch PosturePal camera app 
@app.route('/launch_posture_pal', methods=['POST'])
def launch_posture_pal():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_email = session['user']
    
    try:
        print(f"\n--- LAUNCHING POSTUREPAL for {user_email} ---")
        python_executable = sys.executable 
        script_path = "c:\\Documents\\HF_Project\\main3.py" 
        
        subprocess.Popen([python_executable, script_path]) 

        return jsonify({"message": "PosturePal launched successfully!"})

    except Exception as e:
        print(f"Error launching PosturePal: {e}")
        return jsonify({"error": f"Error launching PosturePal: {e}"}), 500

# Route to handle MoodFood request (uses hardcoded answers)
@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    mood = data.get('mood')
    if not mood:
        mood_key = "HAPPY" 
    else:
        mood_key = mood.upper().replace(' ', '').strip()
    if mood_key not in MOODFOOD_ANSWERS:
        mood_key = 'HAPPY' 
    
    return jsonify(MOODFOOD_ANSWERS[mood_key])

# Route to handle Mind Minutes request (uses hardcoded answers)
@app.route('/get_mindfulness', methods=['POST'])
def get_mindfulness():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    need = data.get('need')
    if not need:
         # Default to a safe answer if no selection is made
        need_key = "QUICKCALM"
    else:
        # Clean input: remove spaces, convert to uppercase, strip whitespace
        need_key = need.upper().replace(' ', '').strip()

    # Look up the specific answer based on the cleaned key
    if need_key not in MIND_MINUTES_ANSWERS:
        # Fallback to a default calm answer if key is still wrong
        need_key = 'QUICKCALM'
    
    return jsonify(MIND_MINUTES_ANSWERS[need_key])

# Route to Handle Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
# 4. RUN BLOCK
if __name__ == '__main__':
    # Ensure you are running this from the HF_Project folder
    app.run(debug=True)