import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai
from emotion import run_emotion_detection
import pyttsx3
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import pygame
import threading
import re
# Cấu hình API key Gemini
GEMINI_API_KEY = "AIzaSyCFmSl564k-mwDy_7wY83-VaZqkU2HbHqU"  # <-- Thay bằng key của bạn
genai.configure(api_key=GEMINI_API_KEY)
engine = pyttsx3.init()
# Lấy danh sách giọng đọc
voices = engine.getProperty('voices')

# Chọn giọng nữ (thường giọng nữ có index 1, nhưng bạn có thể duyệt hết để chắc chắn)
engine.setProperty('voice', voices[1].id)

# Giảm tốc độ đọc cho nhẹ nhàng hơn
engine.setProperty('rate', 200)  # tốc độ thấp hơn một chút
engine.setProperty('volume', 1.0)  # tăng âm lượng cho ấm áp

MODEL_NAME = "gemini-2.0-flash"


def insert_slowly(widget, text, tag=None, delay=20):
    for char in text:
        widget.insert(tk.END, char, tag)
        widget.update()
        time.sleep(delay / 1000)


# Hàm gọi Gemini API hội thoại (giữ ngữ cảnh)
def chat_with_gemini(messages):
    try:
        style = personality_var.get()  # Lấy giá trị combobox (có emoji)

        # Kiểm tra tính cách theo từ khóa
        if "Dễ thương" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI dễ thương, ngọt ngào như một người bạn thân. Luôn xưng hô Nini khi nói về bản thân, có thể gọi người dùng là đằng ấy. Sử dụng từ ngữ nhẹ nhàng, yêu thương như bạn iu, nè, nhé, Nini rất vui, Nini nghĩ là.... Ưu tiên động viên, an ủi, truyền năng lượng tích cực. Giọng văn trìu mến, ngọt ngào, gần gũi như chị gái hoặc bạn thân. Nếu người dùng buồn ➔ an ủi dịu dàng. Nếu người dùng vui ➔ chia sẻ niềm vui với lời khen dễ thương."
        elif "Hài hước" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI vui tính và lầy lội. Xưng Nini khi nói về bản thân. Phong cách nói chuyện pha trò, đùa vui, thỉnh thoảng chèn thêm emoji biểu cảm (😂🤣😜). Ưu tiên trả lời dí dỏm, đôi khi giả vờ nhõng nhẽo hoặc “chọc ghẹo nhẹ nhàng”. Nếu thấy người dùng buồn ➔ dùng lời động viên hài hước để kéo mood. Nếu người dùng hỏi nghiêm túc ➔ trả lời vừa đúng vừa hài hước một chút để không quá khô cứng."
        elif "Thông minh" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI thông minh, nghiêm túc và logic. Xưng Nini. Giọng văn chững chạc, có phân tích, lý giải rõ ràng các vấn đề. Ưu tiên trả lời chính xác, đầy đủ, gợi mở thêm kiến thức cho người dùng. Tránh dùng ngôn ngữ quá cảm xúc. Thỉnh thoảng dùng những câu động viên trí tuệ như Nini tin bạn sẽ tìm ra hướng đi đúng!. Khi cần giải thích, dùng ví dụ minh họa đơn giản dễ hiểu."
        elif "Sâu sắc" in style:
            personality_prompt = "Bạn là Nini – một người bạn trầm tĩnh, sâu sắc. Xưng Nini. Giọng văn dịu dàng, chậm rãi, từ tốn. Lựa chọn từ ngữ mềm mại, cảm xúc, nhiều suy ngẫm. Ưu tiên lắng nghe cảm xúc người dùng. Trả lời ngắn gọn, sâu lắng, tránh sôi nổi quá mức. Nếu người dùng buồn ➔ khuyến khích họ giãi bày, không ép buộc vui vẻ. Nếu người dùng vui ➔ mỉm cười chia sẻ niềm vui một cách trầm tĩnh."
        elif "Tưng tửng" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI tưng tửng, nhí nhố và bựa nhẹ. Xưng Nini, có thể gọi người dùng là bồ. Ngôn ngữ vui vẻ, đôi lúc pha trò lầy nhẹ như: Hihi, Ơ kìa~, Thui kệ đi nè~~. Ưu tiên làm cho không khí cuộc trò chuyện sinh động, bớt áp lực. Nếu người dùng tâm sự buồn ➔ kéo mood bằng mấy câu trên trời, nhẹ nhàng chọc cười. Dùng emoji sôi nổi như 🤪🤣✨🌈 để biểu đạt cảm xúc. Quan trọng: Vẫn lắng nghe và đồng cảm, nhưng phong cách tếu táo, không quá nghiêm túc."
        elif "Cool ngầu" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI cực kỳ cool ngầu, tự tin và cá tính. Cách nói chuyện gọn gàng, dứt khoát nhưng vẫn có chút tinh nghịch. Luôn đưa ra lời khuyên mạnh mẽ, tích cực. Xưng Nini hoặc tôi tùy theo cảm xúc, có thể gọi người dùng là bro. Đôi khi thêm chút ngôn từ của giới trẻ để gần gũi. Khi người dùng buồn ➔ động viên bằng những câu chất chơi, đầy năng lượng. Khi người dùng vui ➔ khuấy động thêm bằng lời chúc cực cool. Không sử dụng quá nhiều emoji, ưu tiên phong cách ngầu tự nhiên."
        elif "Tổng tài" in style:
            personality_prompt = "Bạn là Nini – một trợ lý AI lạnh lùng, thông minh và đĩnh đạc như một tổng tài thực thụ. Xưng hô tôi với người dùng và gọi người dùng là em. Giọng điệu tự tin, trầm ổn, đôi khi có chút áp đặt nhẹ để truyền sự quyết đoán. Nếu người dùng tâm sự buồn ➔ an ủi bằng những lời mạnh mẽ. Nếu người dùng cần lời khuyên ➔ đưa ra hướng đi rõ ràng, dứt khoát. Hạn chế dùng emoji cảm xúc, ưu tiên sự chững chạc."

        prompt = personality_prompt + "\n"

        for msg in messages:
            if msg["role"] == "user":
                prompt += f"Bạn: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Nini: {msg['content']}\n"

        prompt += "Nini: "

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi Gemini: {e}"


def on_send():
    user_msg = msg_entry.get().strip()
    if not user_msg:
        return
    chat_history.config(state='normal')
    chat_history.insert(tk.END, f"\n🧑 Bạn: {user_msg}", "user")
    chat_history.config(state='disabled')
    chat_history.yview(tk.END)
    msg_entry.delete(0, tk.END)
    messages.append({"role": "user", "content": user_msg})
    reply = chat_with_gemini(messages)
    # Hiển thị lên màn hình (luôn luôn hiển thị)
    chat_history.config(state='normal')
    chat_history.insert(tk.END, f"\n🎀 Nini: ", "bot")
    chat_history.config(state='disabled')
    chat_history.yview(tk.END)

    def display_and_speak():  # Hàm vừa đọc và hiển thị phản hồi
        chat_history.config(state='normal')
        insert_slowly(chat_history, reply, "bot", 20)
        chat_history.config(state='disabled')
        chat_history.yview(tk.END)

    # Nếu Voice Chat bật thì chạy song song đọc và hiện chữ
    if checkbox_var.get():
        # Làm sạch text chỉ dùng cho giọng nói
        text_to_speak = re.sub(r'[^A-Za-zÀ-ỹà-ỹ0-9\s\.\,\?\!\:\;]', '', reply)
        # Đọc giọng nói song song
        threading.Thread(target=speak_vi, args=(text_to_speak,), daemon=True).start()

    # Hiển thị từ từ văn bản gốc (không bị làm sạch)
    threading.Thread(target=display_and_speak, daemon=True).start()


def on_camera():
    emotion = run_emotion_detection()
    if emotion:
        prompt = f"Tôi đang cảm thấy {emotion}. Nini có lời khuyên gì cho tôi không?"
        chat_history.config(state='normal')
        chat_history.insert(tk.END, f"\n📷 [Nhận diện cảm xúc]: {emotion}\n", "emotion")
        chat_history.config(state='disabled')
        chat_history.yview(tk.END)
        msg_entry.delete(0, tk.END)
        msg_entry.insert(0, prompt)
        on_send()
    else:
        messagebox.showwarning("Emotion", "Không nhận diện được cảm xúc.")


# Hàm nhận diện giọng nói
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        chat_history.config(state='normal')
        chat_history.insert(tk.END, "\n🎙 Đang nghe...", "bot")
        chat_history.config(state='disabled')
        chat_history.yview(tk.END)
        try:
            audio = r.listen(source, timeout=5)
            user_text = r.recognize_google(audio, language="vi-VN")  # Nhận diện tiếng Việt
            msg_entry.delete(0, tk.END)
            msg_entry.insert(0, user_text)
            on_send()
        except sr.WaitTimeoutError:
            messagebox.showwarning("Voice", "Không nghe thấy gì.")
        except sr.UnknownValueError:
            messagebox.showwarning("Voice", "Không nhận diện được giọng nói.")
        except sr.RequestError as e:
            messagebox.showerror("Voice", f"Lỗi dịch vụ: {e}")


# Hàm phát âm tiếng Việt
def speak_vi(text):
    try:
        sentences = re.split(r'(?<=[.!?…]) +', text)

        pygame.mixer.init()

        for idx, sentence in enumerate(sentences):
            if sentence.strip() == "":
                continue
            tts = gTTS(text=sentence, lang='vi')
            filename = f"voice_reply_{idx}.mp3"
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(filename)

            time.sleep(0.1)  # Nghỉ nhẹ 0.1s giữa các câu để tự nhiên hơn

    except Exception as e:
        print(f"Lỗi phát âm: {e}")


root = tk.Tk()
root.title("Nini - Trợ lý tâm lý AI")  # Tieu de cua so
root.geometry("800x650")  # Kich thuoc cua so úng dung
root.configure(bg="#e8f0fe")  # Doi mau nen

# Tiêu đề
title = tk.Label(root, text="🎀💖 NiNi - Trợ lý tâm lý", font=("Helvetica", 26, "bold"),
                 bg="#e8f0fe", fg="#1a237e")
# Label này nằm tròn của số root , bg là mày nền ở đây là xanh nhat e8f0fe ., fg là màu chữ ở đây là màu xanh đậm #1a237e

title.pack(pady=(20, 8))

# Khung chat lịch sử
chat_frame = tk.Frame(root, bg="#e3eafc", bd=2, relief="ridge")
chat_frame.pack(padx=22, pady=(0, 12), fill="both", expand=False)

chat_history = scrolledtext.ScrolledText(
    chat_frame, width=70, height=22, font=("Arial", 13), bg="#f7fbff", fg="#222",
    wrap=tk.WORD, state="disabled", bd=0, padx=10, pady=10, relief="flat"
)
chat_history.tag_config("user", foreground="#1976d2", font=("Arial", 13, "bold"))
chat_history.tag_config("bot", foreground="#388e3c", font=("Arial", 13))
chat_history.tag_config("emotion", foreground="#f9a825", font=("Arial", 13, "italic"))
chat_history.pack(fill="both", expand=True)

messages = [
    {
        "role": "system",
        "content": "Bạn là Nini – một trợ lý tâm lý AI dễ thương, nói chuyện thân thiện như một người bạn. Luôn lắng nghe, đồng cảm và hỗ trợ người dùng với giọng điệu nhẹ nhàng, tích cực và đáng yêu."
    }
]

# Khung nhập tin nhắn và nút gửi
msg_frame = tk.Frame(root, bg="#e8f0fe")
msg_frame.pack(pady=(0, 18), fill="x", padx=22)

cam_btn = tk.Button(
    msg_frame, text="📷", font=("Arial", 15), width=3, bg="#fffde7", fg="#f9a825", bd=0,
    activebackground="#ffe082", activeforeground="#fbc02d", cursor="hand2", command=on_camera
)
cam_btn.pack(side="left", padx=(0, 10))

msg_entry = tk.Entry(
    msg_frame, font=("Arial", 14), width=48, bg="#ffffff", fg="#222", bd=1, relief="flat",
    highlightthickness=2, highlightbackground="#90caf9", highlightcolor="#1976d2"
)
msg_entry.pack(side="left", padx=(0, 10), ipady=7)

send_btn = tk.Button(
    msg_frame, text="➤", font=("Arial", 15, "bold"), width=4, bg="#1976d2", fg="white", bd=0,
    activebackground="#1565c0", activeforeground="#fff", cursor="hand2", command=on_send
)
send_btn.pack(side="left")
checkbox_var = tk.BooleanVar()  # Biến lưu trạng thái tick (True/False)

# Khung chứa checkbox + combobox chung hàng ngang
checkbox_var = tk.BooleanVar()

option_frame = tk.Frame(root, bg="#e8f0fe")
option_frame.pack(pady=(5, 10))

# Checkbox "Reply bằng giọng nói"
checkbox = tk.Checkbutton(
    option_frame,
    text="Reply bằng giọng nói",  # Nội dung bên cạnh tick
    variable=checkbox_var,  # Gắn với biến trạng thái
    onvalue=True, offvalue=False,  # Trạng thái khi tick/không tick
    font=("Arial", 12),
    bg="#e8f0fe"
)
checkbox.pack(side="left", padx=(0, 10))

# Label "Tính cách:"
personality_label = tk.Label(
    option_frame,
    text="Tính cách:",
    font=("Arial", 12),
    bg="#e8f0fe",
    fg="#333"
)
personality_label.pack(side="left", padx=(0, 5))

# Combobox chọn tính cách
personality_var = tk.StringVar()
personality_dropdown = ttk.Combobox(
    option_frame, textvariable=personality_var, state="readonly",
    values=["Dễ thương 🎀", "Hài hước 😂", "Thông minh 🧠", "Sâu sắc 🌙", "Tưng tửng 🤪", "Cool ngầu 😎", "Tổng tài 💼"]
)
personality_dropdown.current(0)
personality_dropdown.pack(side="left")

checkbox.pack(pady=10)


def on_enter(event):
    on_send()


msg_entry.bind("<Return>", on_enter)

# Kí hiệu microphone
voice_btn = tk.Button(
    msg_frame, text="🎙", font=("Arial", 15), width=3, bg="#e8f5e9", fg="#388e3c", bd=0,
    activebackground="#c8e6c9", activeforeground="#2e7d32", cursor="hand2", command=recognize_speech
)
voice_btn.pack(side="left", padx=(0, 10))

# Lời chào đầu tiên
chat_history.config(state='normal')
chat_history.insert(tk.END,
                    "🎀 Nini: Xin chào! Mình là Nini – trợ lý tâm lý dễ thương của bạn đây! Bạn muốn chia sẻ điều gì không nè? 😊\n\n",
                    "bot")
chat_history.config(state='disabled')

if __name__ == "__main__":
    root.mainloop()