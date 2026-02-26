# Health & Fitness Application Suite 🧘‍♂️💪

An AI-integrated health platform featuring real-time exercise posture tracking, personalized nutritional guidance, and evidence-based mindfulness tools.

## 🚀 Key Features
* **PosturePal (AI Coach):** Uses **YOLOv8** pose estimation to monitor exercise form (Bicep Curls, Shoulder Press) in real-time.
* **MoodFood:** A nutritional engine recommending foods based on emotional states (e.g., Magnesium for stress).
* **Mind Minutes:** Quick, research-backed psychological grounding exercises for stress relief.

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Computer Vision:** OpenCV, Ultralytics YOLOv8
- **Frontend:** HTML5, Tailwind CSS

## ⚙️ Setup Instructions
1. Install dependencies:  
   `pip install flask opencv-python ultralytics numpy cvzone`
2. Ensure you have the model file `yolov8n-pose.pt` in the root directory.
3. Run the app:  
   `python app.py`
