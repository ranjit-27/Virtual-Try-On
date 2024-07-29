from flask import Flask, render_template, request, Response

import cv2
import numpy as np
from cvzone.PoseModule import PoseDetector
import os

app = Flask(__name__)

# Global variable to store the path of the uploaded image
uploaded_image_path = None

# Initialize variables for capturing video and detecting poses
cap = None
detector = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global uploaded_image_path
    if 'image' in request.files:
        image = request.files['image']
#         image_path = os.path.join('uploads', image.filename)
        uploaded_image_path=image.filename
        image.save(uploaded_image_path)
        img = plt.imread(uploaded_image_path)
        plt.imshow(img)
        plt.show()
        return 'Image uploaded successfully', 200
    else:
        return 'No image found in request', 400

def generate_frames():
    global cap, detector, uploaded_image_path
    if cap is None:
        cap = cv2.VideoCapture(0)
    if detector is None:
        detector = PoseDetector()

    while cap.isOpened():
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findPose(img,draw=False)
        lmList, _ = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm_shoulder_left = lmList[11][0:2]
            lm_shoulder_right = lmList[12][0:2]
            lm_hip_left = lmList[23][0:2]
            lm_hip_right = lmList[24][0:2]

            shirt_width = int(abs(lm_shoulder_right[0] - lm_shoulder_left[0]) * 1.5)
            shirt_height = int(abs(lm_shoulder_left[1] - lm_hip_left[1]) * 1.5)

            # Check if an uploaded image exists
            if uploaded_image_path and os.path.exists(uploaded_image_path):
                shirt_img = cv2.imread(uploaded_image_path, cv2.IMREAD_UNCHANGED)
                shirt_img = cv2.resize(shirt_img, (shirt_width, shirt_height))

                shirt_x = int(min(lm_shoulder_left[0], lm_shoulder_right[0]) - shirt_width * 0.2)
                shirt_y = int(min(lm_shoulder_left[1], lm_shoulder_right[1]) - shirt_height * 0.8)

                max_y, max_x, _ = img.shape
                shirt_img_height, shirt_img_width, _ = shirt_img.shape
                if shirt_y < 0:
                    shirt_y = 0
                if shirt_x < 0:
                    shirt_x = 0
                if shirt_y + shirt_img_height > max_y:
                    shirt_img_height = max_y - shirt_y
                if shirt_x + shirt_img_width > max_x:
                    shirt_img_width = max_x - shirt_x

                for c in range(3):
                    img_part = shirt_img[:shirt_img_height, :shirt_img_width, c] * (
                            shirt_img[:shirt_img_height, :shirt_img_width, 3] / 255.0)
                    img[shirt_y:shirt_y + shirt_img_height, shirt_x:shirt_x + shirt_img_width, c] = (
                                img_part +
                                img[shirt_y:shirt_y + shirt_img_height, shirt_x:shirt_x + shirt_img_width,
                                c] * (1 - (shirt_img[:shirt_img_height, :shirt_img_width, 3] / 255.0))
                            ).astype(np.uint8)

                    for c in range(3):
                        img_part = shirt_img[:shirt_img_height, :shirt_img_width, c] * (
                                shirt_img[:shirt_img_height, :shirt_img_width, 3] / 255.0)
                        img[shirt_y:shirt_y + shirt_img_height, shirt_x:shirt_x + shirt_img_width, c] = np.where(
                            img_part > 0,
                            img_part,
                            img[shirt_y:shirt_y + shirt_img_height, shirt_x:shirt_x + shirt_img_width, c]
                        ).astype(np.uint8)

        ret, frame = cv2.imencode('.jpg', img)
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    if cap:
        cap.release()
        cap=None

@app.route('/start_video_feed')
def start_video_feed():
    global video_feed_running
    video_feed_running = True
    return 'Video feed started'

@app.route('/stop_video_feed')
def stop_video_feed():
    global video_feed_running
    video_feed_running = False
    return 'Video feed stopped'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
