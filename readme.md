# FlexiCare - Intelligent Posture Correction System

FlexiCare is a web-based application that uses computer vision and machine learning to provide real-time feedback for posture correction exercises. It leverages your webcam and advanced pose estimation (MediaPipe) to help you perform exercises with correct form, track your progress, and receive instant feedback.

## Features

- **Real-time Posture Analysis:** Uses your webcam to analyze body posture during exercises.
- **Multiple Exercise Modes:** Includes Shoulder Raise, Back Straightening, Neck Alignment, and Forward Bend.
- **Live Feedback:** Visual and textual feedback on posture correctness, score, and exercise time.
- **Exercise Instructions:** Step-by-step guidance for each exercise.
- **Modern UI:** Responsive and user-friendly interface.

## Live Demo

Try the deployed app here:  
👉 [https://flexi-care.onrender.com/](https://flexi-care.onrender.com/)

## Screenshots

![FlexiCare Screenshot](https://flexi-care.onrender.com/static/screenshot.png)  
*Example UI (screenshot may not be available if not uploaded)*

## Technology Stack

- **Backend:** Python, Flask, OpenCV, MediaPipe, NumPy
- **Frontend:** HTML, CSS, JavaScript, FontAwesome
- **Deployment:** Gunicorn, Render.com

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/flexicare.git
   cd flexicare
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at [http://localhost:10000](http://localhost:10000).

### Production Deployment

- Use `gunicorn` with the provided `gunicorn_config.py` for production.
- Example:
  ```bash
  gunicorn -c gunicorn_config.py app:app
  ```

## Usage

1. Open the app in your browser.
2. Allow camera access when prompted.
3. Select an exercise from the dropdown.
4. Click "Start Exercise" to begin.
5. Follow the on-screen instructions and feedback.
6. Click "Stop Exercise" to end the session and view your results.

## Project Structure

```
FlexiCare/
├── app.py
├── gunicorn_config.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── readme.md
```

## License

This project is for educational and demonstration purposes.

---

**Deployed Link:** [https://flexi-care.onrender.com/](https://flexi-care.onrender.com/)
