import cv2
import mediapipe as mp
import numpy as np
import base64
from flask import Flask, render_template, Response, jsonify, request
import time
import os

app = Flask(__name__)

class PostureCorrectionSystem:
    def __init__(self):
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Current exercise and status tracking
        self.current_exercise = "Shoulder Raise"
        self.posture_status = "Not Started"
        self.score = 0
        self.exercise_time = 0
        self.start_time = time.time()
        self.is_exercise_active = False
        
        # Available exercises
        self.exercises = [
            "Shoulder Raise",
            "Back Straightening",
            "Neck Alignment",
            "Forward Bend"
        ]
    
    def get_exercises(self):
        return self.exercises
    
    def get_instructions(self, exercise):
        instructions = {
            "Shoulder Raise": "Stand straight facing the camera. Raise both arms to shoulder height and hold. Keep shoulders relaxed and back straight.",
            "Back Straightening": "Stand sideways to the camera. Keep your back straight and aligned. Avoid hunching or arching your back.",
            "Neck Alignment": "Face the camera. Keep your head level and your neck straight. Avoid tilting your head or jutting your chin forward.",
            "Forward Bend": "Stand sideways to the camera. Bend forward at the hips while keeping your back straight. Go only as far as comfortable."
        }
        return instructions.get(exercise, "No instructions available")
    
    def start_exercise(self, exercise_name):
        self.current_exercise = exercise_name
        self.posture_status = "Analyzing..."
        self.score = 0
        self.start_time = time.time()
        self.is_exercise_active = True
        return {"status": "started", "exercise": self.current_exercise}
    
    def stop_exercise(self):
        self.posture_status = "Stopped"
        self.is_exercise_active = False
        return {
            "status": "stopped", 
            "exercise": self.current_exercise, 
            "final_score": self.score,
            "time": int(time.time() - self.start_time)
        }
    
    def analyze_posture(self, landmarks):
        """Analyze body posture based on landmarks for the current exercise"""
        if not self.is_exercise_active:
            return False, "Not Started"
            
        # Get landmark positions (x, y coordinates normalized to 0.0-1.0)
        landmark_positions = {
            'left_shoulder': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                                      landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y]),
            'right_shoulder': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                                       landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y]),
            'left_elbow': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW].x,
                                   landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW].y]),
            'right_elbow': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                                    landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y]),
            'left_wrist': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].x,
                                   landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].y]),
            'right_wrist': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].x,
                                    landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].y]),
            'left_hip': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x,
                                 landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].y]),
            'right_hip': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP].x,
                                  landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP].y]),
            'nose': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].x,
                             landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y]),
            'left_ear': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_EAR].x,
                                 landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_EAR].y]),
            'right_ear': np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_EAR].x,
                                  landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_EAR].y])
        }
        
        # Calculate angles and metrics for different exercises
        correct_posture = False
        feedback = ""
        
        if self.current_exercise == "Shoulder Raise":
            # Check if arms are raised to shoulder height
            left_shoulder_angle = self.calculate_angle(
                landmark_positions['left_hip'],
                landmark_positions['left_shoulder'],
                landmark_positions['left_elbow']
            )
            
            right_shoulder_angle = self.calculate_angle(
                landmark_positions['right_hip'],
                landmark_positions['right_shoulder'],
                landmark_positions['right_elbow']
            )
            
            # Check if arms are horizontal (90 degrees from torso)
            if 80 <= left_shoulder_angle <= 100 and 80 <= right_shoulder_angle <= 100:
                correct_posture = True
                feedback = "Good! Arms at shoulder height"
                self.score += 1
            else:
                feedback = "Adjust arms to shoulder height"
        
        elif self.current_exercise == "Back Straightening":
            # Calculate back alignment
            shoulder_midpoint = (landmark_positions['left_shoulder'] + landmark_positions['right_shoulder']) / 2
            hip_midpoint = (landmark_positions['left_hip'] + landmark_positions['right_hip']) / 2
            
            # Calculate the vertical alignment (should be close to a vertical line)
            horizontal_diff = abs(shoulder_midpoint[0] - hip_midpoint[0])
            
            if horizontal_diff < 0.05:  # Threshold for good alignment
                correct_posture = True
                feedback = "Good! Back is straight"
                self.score += 1
            else:
                feedback = "Straighten your back"
        
        elif self.current_exercise == "Neck Alignment":
            # Check neck alignment with ears and shoulders
            nose_to_center = abs(landmark_positions['nose'][0] - 0.5)  # Center is at x=0.5
            ears_level = abs(landmark_positions['left_ear'][1] - landmark_positions['right_ear'][1])
            
            if nose_to_center < 0.05 and ears_level < 0.05:
                correct_posture = True
                feedback = "Good! Neck is well aligned"
                self.score += 1
            else:
                feedback = "Align your head and neck"
        
        elif self.current_exercise == "Forward Bend":
            # Calculate hip hinge angle
            torso_angle = self.calculate_angle(
                landmark_positions['right_shoulder'],
                landmark_positions['right_hip'],
                np.array([landmark_positions['right_hip'][0], landmark_positions['right_hip'][1] + 0.2])
            )
            
            if 45 <= torso_angle <= 90:
                correct_posture = True
                feedback = "Good! Correct forward bend"
                self.score += 1
            else:
                feedback = "Bend at the hips, keep back straight"
        
        self.posture_status = "Correct: " + feedback if correct_posture else "Incorrect: " + feedback
        self.exercise_time = int(time.time() - self.start_time)
            
        return correct_posture, feedback
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = min(1.0, max(-1.0, cosine_angle))  # Ensure value is in valid range
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)
    
    def process_frame(self, frame):
        """Process a single frame and return analysis results"""
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Pose
        results = self.pose.process(rgb_frame)
        
        # Draw the pose annotations on the frame
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Analyze posture if exercise is active
            if self.is_exercise_active:
                correct, feedback = self.analyze_posture(results.pose_landmarks)
                
                # Add visual feedback to the frame
                status_color = (0, 255, 0) if correct else (0, 0, 255)
                cv2.putText(frame, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                
                # Draw a colored rectangle at the top to indicate posture status
                cv2.rectangle(frame, (0, 0), (frame.shape[1], 20), status_color, -1)
        
        # Display exercise name and time
        cv2.putText(frame, f"Exercise: {self.current_exercise}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {self.exercise_time}s", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Score: {self.score}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def get_status(self):
        """Get current status information"""
        return {
            "exercise": self.current_exercise,
            "status": self.posture_status,
            "score": self.score,
            "time": self.exercise_time
        }

# Create instance of the posture system - in Render, this can be a global instance
posture_system = PostureCorrectionSystem()

@app.route('/')
def index():
    """Render the main page"""
    exercises = posture_system.get_exercises()
    return render_template('index.html', exercises=exercises)

@app.route('/api/exercises')
def get_exercises():
    """Return available exercises"""
    return jsonify(posture_system.get_exercises())

@app.route('/api/instructions/<exercise>')
def get_instructions(exercise):
    """Return instructions for the specified exercise"""
    return jsonify({"instructions": posture_system.get_instructions(exercise)})

@app.route('/api/start', methods=['POST'])
def start_exercise():
    """Start an exercise session"""
    data = request.json
    exercise = data.get('exercise', 'Shoulder Raise')
    return jsonify(posture_system.start_exercise(exercise))

@app.route('/api/stop', methods=['POST'])
def stop_exercise():
    """Stop the current exercise session"""
    return jsonify(posture_system.stop_exercise())

@app.route('/api/status')
def get_status():
    """Get current exercise status"""
    return jsonify(posture_system.get_status())

@app.route('/api/process_frame', methods=['POST'])
def process_frame():
    """Process a single frame sent from client"""
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image data received'}), 400
    
    # Decode base64 image
    try:
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the frame
        processed_frame = posture_system.process_frame(frame)
        
        # Encode processed frame to base64
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        # Return processed image and status
        return jsonify({
            'image': f"data:image/jpeg;base64,{processed_image}",
            'status': posture_system.get_status()
        })
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)