from flask import Flask, render_template, Response, request, jsonify
from emotion_recommendation import get_emotion_recommendations, predict_emotion_from_frame
from content_recommendation import get_content_recommendations
import cv2
import threading
import numpy as np

app = Flask(__name__)

# Global variables to store frames and emotions
frames = []
emotions = []
capture = False

def capture_frames():
    global frames, capture
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for Windows

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    count = 0
    while count < 50:
        ret, frame = cap.read()
        if ret and capture:
            frames.append(frame)
            count += 1
        elif not capture:
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    global capture
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for Windows

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture_image():
    global frames, capture, emotions
    frames = []
    emotions = []
    capture = True
    thread = threading.Thread(target=capture_frames)
    thread.start()
    thread.join()

    for frame in frames:
        emotion = predict_emotion_from_frame(frame)
        emotions.append(emotion)
    
    dominant_emotion = max(set(emotions), key=emotions.count)
    print(dominant_emotion)
    recommendations = get_emotion_recommendations(dominant_emotion)

    return render_template('emotion_results.html', emotion=dominant_emotion, recommendations=recommendations)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    movie_name = data.get('movie_name')
    if not movie_name:
        return jsonify({'error': 'No movie name provided'}), 400
    recommendations = get_content_recommendations(movie_name)
    return jsonify({'recommended_movies': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
