import cv2
import cvzone
from ultralytics import YOLO
import numpy as np
import math
import sys # Used for exiting the script if needed


# 1. POSTURE GEOMETRY FUNCTION


def calculate_angle(p1_coord, p2_coord, p3_coord):
    """Calculates the angle (p1-p2-p3) in degrees."""
    p1 = np.array(p1_coord)
    p2 = np.array(p2_coord)
    p3 = np.array(p3_coord)

    angle = math.degrees(math.atan2(p3[1] - p2[1], p3[0] - p2[0]) -
                         math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
    
    # Normalize the angle to be between 0 and 180 degrees
    if angle < 0:
        angle += 360
    if angle > 180:
        angle = 360 - angle
        
    return angle

# ====================================================================
# 2. EXERCISE CHECK FUNCTION
# ====================================================================

def check_posture(keypoints_data, exercise_name):
    """Analyzes the keypoints data based on the current exercise."""
    
    status_text = "Finding Pose..."
    status_color = (0, 165, 255) # Orange (Initial)
    angle_value = None

    # COCO Keypoint Indices (Right Side used for consistency)
    # 6: R-Shoulder, 8: R-Elbow, 10: R-Wrist, 12: R-Hip
    conf_threshold = 0.6
    
    # --- A. BICEP CURL (Checks Right Elbow Angle: Shoulder-Elbow-Wrist) ---
    if exercise_name == "BICEP_CURL":
        p1_idx, p2_idx, p3_idx = 6, 8, 10 
        
        if keypoints_data.shape[0] > p3_idx and all(keypoints_data[[p1_idx, p2_idx, p3_idx], 2] > conf_threshold):
            p_coords = [keypoints_data[i][:2] for i in [p1_idx, p2_idx, p3_idx]]
            angle_value = calculate_angle(*p_coords)
            
            if 40 < angle_value < 120:
                status_text = "BICEP CURL: OK NICE!"
                status_color = (0, 255, 0) # Green
            elif angle_value >= 160:
                status_text = "BICEP CURL: EXTEND ARM"
                status_color = (0, 165, 255)
            else:
                status_text = "BICEP CURL: WRONG FORM"
                status_color = (0, 0, 255) # Red

    # --- B. SHOULDER PRESS (Checks Right Shoulder Angle: Hip-Shoulder-Elbow) ---
    elif exercise_name == "SHOULDER_PRESS":
        p1_idx, p2_idx, p3_idx = 12, 6, 8 
        
        if keypoints_data.shape[0] > p3_idx and all(keypoints_data[[p1_idx, p2_idx, p3_idx], 2] > conf_threshold):
            p_coords = [keypoints_data[i][:2] for i in [p1_idx, p2_idx, p3_idx]]
            angle_value = calculate_angle(*p_coords)
            
            if 150 < angle_value <= 180:
                status_text = "PRESS: REPETITION COMPLETE"
                status_color = (0, 255, 0) # Green
            elif 70 < angle_value < 150:
                 status_text = "PRESS: LIFTING/LOWERING"
                 status_color = (0, 165, 255)
            else:
                status_text = "PRESS: WRONG START POSITION"
                status_color = (0, 0, 255) # Red

    # --- C. FOREARM CURL (Checks Right Elbow Angle: Shoulder-Elbow-Wrist) ---
    # *Note: Forearm curls primarily involve wrist movement, but we can check elbow stability.*
    elif exercise_name == "FOREARM_CURL":
        p1_idx, p2_idx, p3_idx = 6, 8, 10 
        
        if keypoints_data.shape[0] > p3_idx and all(keypoints_data[[p1_idx, p2_idx, p3_idx], 2] > conf_threshold):
            p_coords = [keypoints_data[i][:2] for i in [p1_idx, p2_idx, p3_idx]]
            angle_value = calculate_angle(*p_coords)
            
            # Posture Logic: Require the elbow to be held steady (mostly straight)
            if 160 < angle_value <= 180:
                status_text = "FOREARM CURL: ELBOW STABLE"
                status_color = (0, 255, 0) # Green
            else:
                status_text = "FOREARM CURL: MOVE WRIST ONLY"
                status_color = (0, 0, 255) # Red

    return status_text, status_color, angle_value

# ====================================================================
# 3. EXERCISE SELECTION (Pre-Loop Setup)
# ====================================================================

# Dictionary mapping menu option to exercise name
EXERCISES = {
    1: "BICEP_CURL",
    2: "SHOULDER_PRESS",
    3: "FOREARM_CURL"
}

print("\n--- Exercise Selection Menu ---")
print("1: Bicep Curl (Checks Elbow Flexion)")
print("2: Shoulder Press (Checks Upper Arm Angle)")
print("3: Forearm Curl (Checks Elbow Stability)")
print("-------------------------------\n")

selected_exercise_name = None

while selected_exercise_name is None:
    try:
        choice = input("Enter the number of the exercise you want to perform (e.g., 1): ")
        choice = int(choice)
        
        if choice in EXERCISES:
            selected_exercise_name = EXERCISES[choice]
            print(f"\n✅ Starting session for: {selected_exercise_name.replace('_', ' ')}\n")
        else:
            print(f"❌ Invalid choice: {choice}. Please enter 1, 2, or 3.")
            
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        
# ====================================================================
# 4. MAIN APPLICATION LOOP
# ====================================================================

cap = cv2.VideoCapture(0)
model = YOLO('yolov8n-pose.pt')

if not cap.isOpened():
    print("FATAL ERROR: Camera could not be opened.")
    sys.exit(1)

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Camera connection lost. Exiting loop.")
        break

    frame = cv2.resize(frame, (840, 820))
    width, height = frame.shape[:2]
    blank_image = np.zeros((width, height, 3), dtype=np.uint8)

    results = model(frame, verbose=False)
    yolo_frame = results[0].plot()

    status_text = "Finding Pose..."
    status_color = (0, 165, 255) 
    angle_display = ""
    
    # Check if a person was detected
    if results[0].keypoints.data.numel() > 0:
        keypoints_data = results[0].keypoints.data[0].cpu().numpy()
        
        # Call the unified check function with the user's selection
        status_text, status_color, angle_value = check_posture(keypoints_data, selected_exercise_name)
        
        if angle_value is not None:
             angle_display = f'{selected_exercise_name.replace("_", " ")} Angle: {int(angle_value)}°'

        # --- Drawing Keypoints and Connections ---
        # (This remains your original drawing logic)
        for i, keypoint in enumerate(keypoints_data):
            x, y, confidence = keypoint
            if confidence > 0.7:
                cv2.circle(blank_image, (int(x), int(y)), radius=5, color=(255, 0, 0), thickness=-1)

        connections = [
            (3, 1), (1, 0), (0, 2), (2, 4), (1, 2), (4, 6), (3, 5), (5, 6),
            (5, 7), (7, 9), (6, 8), (8, 10), (11, 12), (11, 13), (13, 15), (12, 14),
            (14, 16), (5, 11), (6, 12)
        ]
        
        for part_a, part_b in connections:
            x1, y1, conf1 = keypoints_data[part_a][:3]
            x2, y2, conf2 = keypoints_data[part_b][:3]

            if conf1 > 0.5 and conf2 > 0.5:
                cv2.line(blank_image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 255), thickness=2)

   
    
    output = cvzone.stackImages([yolo_frame, blank_image], cols=2, scale=0.80)
    
    # Draw Posture Status
    cv2.putText(output, status_text, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.5, status_color, 3, cv2.LINE_AA)
    
    # Draw Angle
    if angle_display:
        cv2.putText(output, angle_display, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Posture Analysis', output) 
    
    if cv2.waitKey(1) & 0xff == ord('t'):
        break

cap.release()
cv2.destroyAllWindows()