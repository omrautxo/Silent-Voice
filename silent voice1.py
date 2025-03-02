import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import pickle
import numpy as np
import mediapipe as mp
from threading import Thread

def load_model():
    model_path = "C:/Users/ARYAN/Desktop/model.p"
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    return model_data['model']

def start_detection():
    global cap, running
    running = True
    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.6)
    labels_dict = {0: 'Hi', 1: 'Yes', 2: 'No', 3: 'Thank You', 4: 'I Love You'}
    model = load_model()

    def detect():
        global running
        while running:
            ret, frame = cap.read()
            if not ret:
                continue
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    data_aux = []
                    x_ = [lm.x for lm in hand_landmarks.landmark]
                    y_ = [lm.y for lm in hand_landmarks.landmark]

                    for lm in hand_landmarks.landmark:
                        data_aux.append(lm.x - min(x_))
                        data_aux.append(lm.y - min(y_))

                    if len(data_aux) == model.n_features_in_:
                        confidence = max(model.predict_proba([np.asarray(data_aux)])[0])
                        if confidence < 0.6:
                            detected_label.set("No sign detected")
                            continue
                        prediction = model.predict([np.asarray(data_aux)])[0]
                        detected_label.set(labels_dict[int(prediction)])

            # Display frame inside GUI
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            video_label.imgtk = imgtk
            video_label.config(image=imgtk)

        cap.release()
        cv2.destroyAllWindows()

    Thread(target=detect, daemon=True).start()

def stop_detection():
    global running
    running = False

# GUI Setup
root = tk.Tk()
root.title("ASL Detection")
root.geometry("700x600")

# Load background image
bg_image = Image.open("background.jpg")
bg_image = bg_image.resize((700, 600), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

detected_label = tk.StringVar()
detected_label.set("Waiting...")

label_title = ttk.Label(frame, text="ASL Detection", font=("Arial", 18, "bold"))
label_title.pack(pady=10)

label_detected = ttk.Label(frame, text="Detected Sign:", font=("Arial", 12))
label_detected.pack()

detected_text = ttk.Label(frame, textvariable=detected_label, font=("Arial", 14, "bold"), foreground="blue")
detected_text.pack(pady=5)

video_label = ttk.Label(frame)
video_label.pack(pady=10)

btn_start = ttk.Button(frame, text="Start Detection", command=start_detection)
btn_start.pack(pady=5)

btn_stop = ttk.Button(frame, text="Stop Detection", command=stop_detection)
btn_stop.pack(pady=5)

root.mainloop()