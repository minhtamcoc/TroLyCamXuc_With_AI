import cv2
from deepface import DeepFace
import time
from collections import Counter


def run_emotion_detection():
    # Load face cascade classifier
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Start capturing video
    cap = cv2.VideoCapture(0)

    # Dictionary to translate emotions from English to Vietnamese
    emotion_translation = {
        'angry': 'gian du',
        'disgust': 'ghe tom',
        'fear': 'so hai',
        'happy': 'vui ve',
        'sad': 'buon',
        'surprise': 'ngac nhien',
        'neutral': 'binh thuong'
    }
    # List to store all detected emotions during the analysis period
    all_detected_emotions = []
    all_detected_genders = []
    # Set start time for timing
    start_time = time.time()
    duration = 10

    # Main loop for data collection
    while time.time() - start_time < duration:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Convert grayscale frame to RGB format
        rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract the face ROI (Region of Interest)
            face_roi = rgb_frame[y:y + h, x:x + w]

            # Perform emotion analysis on the face ROI
            try:
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

                # Determine the dominant emotion
                emotion = result[0]['dominant_emotion']

                # Add this emotion to our collection
                all_detected_emotions.append(emotion)

                # Translate emotion to Vietnamese
                emotion_vn = emotion_translation.get(emotion, emotion)
                # Draw rectangle around face and label with predicted emotion
                label ='f{emotion_vn}'
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, emotion_vn, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error in emotion detection: {e}")

        # Display the resulting frame
        cv2.imshow('Emotion Detection', frame)

        # Press 'q' to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Turn off the camera after analysis
    cap.release()
    cv2.destroyAllWindows()


    final_emotion = None
    final_emotion_vn = None
    if all_detected_emotions:
        emotion_counter = Counter(all_detected_emotions)
        final_emotion = emotion_counter.most_common(1)[0][0]


    final_emotion_vn = emotion_translation.get(final_emotion, final_emotion)
    print(f"Final emotion: {final_emotion} ({final_emotion_vn})")

# Store the final emotion in a variable for later use
    emotion_result = {
    "final_emotion": final_emotion,
    "final_emotion_vn": final_emotion_vn
}

    return emotion_result["final_emotion_vn"]


