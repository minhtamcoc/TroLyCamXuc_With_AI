import cv2
from deepface import DeepFace
import time
from collections import Counter
from PIL import ImageFont, ImageDraw, Image
import numpy as np

# Hàm vẽ chữ tiếng Việt
def draw_text_vn(img, text, position, font_path="arial.ttf", font_size=24, color=(0, 255, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def run_emotion_detection():
    # Load face cascade
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Mở camera
    cap = cv2.VideoCapture(0)

    # Dictionary: English ➔ Vietnamese
    emotion_translation = {
        'angry': 'giận dữ',
        'disgust': 'ghê tởm',
        'fear': 'sợ hãi',
        'happy': 'vui vẻ',
        'sad': 'buồn bã',
        'surprise': 'ngạc nhiên',
        'neutral': 'bình thường',
    }

    all_detected_emotions = []
    start_time = time.time()
    duration = 6  # thời gian chạy camera

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            print("Không mở được camera.")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = rgb_frame[y:y+h, x:x+w]
            try:
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                all_detected_emotions.append(emotion)

                emotion_vn = emotion_translation.get(emotion, emotion)

                # Vẽ khung + chữ tiếng Việt
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                frame = draw_text_vn(frame, emotion_vn, (x, y - 30))
            except Exception as e:
                print(f"Lỗi nhận diện cảm xúc: {e}")

        cv2.imshow('Emotion Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    final_emotion = None
    final_emotion_vn = None
    if all_detected_emotions:
        emotion_counter = Counter(all_detected_emotions)
        final_emotion = emotion_counter.most_common(1)[0][0]
        final_emotion_vn = emotion_translation.get(final_emotion, final_emotion)

    print(f"Cảm xúc cuối cùng: {final_emotion} ({final_emotion_vn})")

    return final_emotion_vn