from functools import partial
import tkinter
import cv2
import face_recognition
import os
import glob
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import serial
connection = serial.Serial('COM4', 9600)
root = Tk()
pause_detection = False
background_img_path = "background.png"
background_img = Image.open(background_img_path)
background_img = background_img.resize((1720, 835))
background = ImageTk.PhotoImage(image=background_img)
canvas = tkinter.Canvas(root, width=1720, height=835)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, anchor="nw", image=background)
correct_pass = "1234"
root.title("Face Recognition Service")
root.geometry('1920x1080')
label = Label(root, text="Who are you?", font=("Helvetica", 32))
label.place(relx=0.5, rely=0.09, anchor=CENTER)
video = Label(root)
video.place(relx=0.5, rely=0.4, anchor=CENTER)

def clicked():
    global pause_detection
    pause_detection = False  
    label.configure(text="Starting face recognition...")
    sfr = facerec()
    sfr.encodings_imgs("images")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return
    update_frame(cap, sfr)

button = Button(root, text="Face Recognition", fg="black", command=clicked, font=16)
button.place(relx=0.5, rely=0.8, anchor=CENTER)

def change_pass():
    global pause_detection
    pause_detection = True  
    for widget in root.winfo_children():
        if isinstance(widget, Entry) or isinstance(widget, Button) and widget != change_button:
            widget.destroy()

    change_button.destroy()
    label.configure(text="Enter Old password:", font=("Helvetica", 20))
    password = Entry(root, width=10, show='*')
    password.place(relx=0.6, rely=0.9, anchor=CENTER)

    def verify():
        entered_password = password.get()
        if entered_password == correct_pass:
            password.destroy()
            label.configure(text="Enter New password:")
            new_pass = Entry(root, width=10, show='*')
            new_pass.place(relx=0.6, rely=0.9, anchor=CENTER)

            def new_handle():
                new_password = new_pass.get()
                global correct_pass
                if len(new_password) == 4:
                    correct_pass = 'P' + new_password 
                    new_pass.destroy()
                    connection.write(correct_pass.encode())
                    label.configure(text="Password Successfully Changed!")
                    root.after(1000, root.destroy)
                else:
                    error_label = Label(root, text="New Password Must Be 4 Characters Long", font=("Helvetica", 20))
                    error_label.place(relx=0.45, rely=0.5, anchor=CENTER)
                    root.after(1000, lambda: error_label.destroy())

            send_button = Button(root, text="Submit New Password", fg="black", command=new_handle, font=16)
            send_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        else:
            label.configure(text="Incorrect password. Please try again.")

    ver = Button(root, text="Submit Password", fg="black", command=verify, font=16)
    ver.place(relx=0.5, rely=0.8, anchor=CENTER)

change_button = Button(root, text="Change Password", fg="black", command=change_pass, font=16)
change_button.place(relx=0.5, rely=0.9, anchor=CENTER)

def del_handle():
    global pause_detection
    pause_detection = True  
    for widget in root.winfo_children():
        if isinstance(widget, Entry) or isinstance(widget, Button) and widget != del_button:
            widget.destroy()
    del_button.destroy()
    label4 = Label(root, text="Enter Password:", font=("Helvetica", 20))
    label4.place(relx=0.5, rely=0.9, anchor=CENTER)
    password = Entry(root, width=10, show='*')
    password.place(relx=0.6, rely=0.9, anchor=CENTER)
    def verify():
        entered_password = password.get() 
        if entered_password == correct_pass:
            ver.destroy()
            password.destroy()
            label4.destroy()
            label.configure(text="Enter Name of User to Delete:", font=("Helvetica", 20))
            name_entry = Entry(root, width=20)
            name_entry.place(relx=0.5, rely=0.9, anchor=CENTER)
            def delete_user():
                user_name = name_entry.get()
                if user_name:
                    user_image_path = f"images/{user_name}.jpg"
                    if os.path.exists(user_image_path):
                        os.remove(user_image_path)
                        label.configure(text=f"User '{user_name}' deleted!")
                    else:
                        label.configure(text=f"No user found with name '{user_name}'.")
                else:
                    label.configure(text="Name cannot be empty.")

            delete_button = Button(root, text="Delete User", fg="black", command=delete_user, font=16)
            delete_button.place(relx=0.5, rely=0.85, anchor=CENTER)
        else:
            label.configure(text="Incorrect password. Please try again.")

    ver = Button(root, text="Submit Password", fg="black", command=verify, font=16)
    ver.place(relx=0.5, rely=0.8, anchor=CENTER)

del_button = Button(root, text="Delete User", fg="black", command=del_handle, font=16)
del_button.place(relx=0.5, rely=0.85, anchor=CENTER)

class facerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resize = 0.25
        self.current_face_location = None
        self.current_frame = None
        self.submit_button = None  

    def encodings_imgs(self, images_path):
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        for path in images_path:
            img = cv2.imread(path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            basename = os.path.basename(path)
            filename, ext = os.path.splitext(basename)
            encodings = face_recognition.face_encodings(rgb_img)
            if encodings:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(filename)
            else:
                print(f"No faces detected in image: {path}")

    def unknown_handling(self, password):
        global pause_detection
        pause_detection = True
        entered = password.get()
        if entered == correct_pass:
            password.destroy()
            if self.submit_button:
                self.submit_button.destroy()  
            change_button.destroy()
            def open():
                connection.write(b'R')
                label.configure(text="Access granted!")
                add_button.destroy()
                open_button.destroy()

            def add():
                connection.write(b'R')
                add_button.destroy()
                open_button.destroy()
                self.ask_for_name()

            open_button = Button(root, text="Open", fg="black", command=open, font=16)
            open_button.place(relx=0.45, rely=0.9, anchor=CENTER)
            add_button = Button(root, text="Add", fg="black", command=add, font=16)
            add_button.place(relx=0.55, rely=0.9, anchor=CENTER)
        else:
            label.configure(text="Incorrect password. Please try again.")
    def ask_for_name(self):
        label_name = Label(root, text="Please enter a name for the new face:", font=("Helvetica", 24))
        label_name.place(relx=0.5, rely=0.7, anchor=CENTER)
        name_entry = Entry(root, width=20)
        name_entry.place(relx=0.5, rely=0.8, anchor=CENTER)

        def save_face():
            user_name = name_entry.get()
            if user_name:
                self.save_face_image(user_name)
            else:
                error_label = Label(root, text="Name cannot be empty.", font=("Helvetica", 18), fg="red")
                error_label.place(relx=0.5, rely=0.9, anchor=CENTER)

        submit_name_button = Button(root, text="Submit Name", fg="black", command=save_face, font=16)
        submit_name_button.place(relx=0.5, rely=0.85, anchor=CENTER)

    def save_face_image(self, user_name):
        if self.current_face_location is not None:
            top, right, bottom, left = self.current_face_location[0]
            face_image = self.current_frame[top:bottom, left:right]
            face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            save_path = f"images/{user_name}.jpg"
            cv2.imwrite(save_path, face_image_rgb)
            label.configure(text=f"Face saved as {user_name}.jpg!")
            root.after(5000, root.destroy)
        else:
            label.configure(text="No face detected to save.")

    def detect(self, frame):
        self.current_frame = frame
        sm_frame = cv2.resize(frame, (0, 0), fx=self.frame_resize, fy=self.frame_resize)
        rgb_frame = cv2.cvtColor(sm_frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, locations)
        face_names = []
        name = "Unknown"
        for f_e in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, f_e)
            if True in matches:
                match_in = matches.index(True)
                name = self.known_face_names[match_in]
                break
        face_names.append(name)
        face_locations = np.array(locations)
        face_locations = face_locations / self.frame_resize
        self.current_face_location = face_locations.astype(int) if face_locations.size > 0 else None
        return face_locations.astype(int), face_names

def update_frame(cap, sfr):
    global pause_detection
    ret, frame = cap.read()

    if not ret or pause_detection: 
        return

    locs, face_name = sfr.detect(frame)
    recognised = False

    for (top, right, bottom, left), name in zip(locs, face_name):
        if name != "Unknown":
            cv2.rectangle(frame, (left, top), (right, bottom), (127, 127, 0), 3)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (127, 127, 127))
            recognised = True
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (127, 127, 127))
            pause_detection = True
            password = Entry(root, width=10, show='*')
            password.place(relx=0.6, rely=0.9, anchor=CENTER)
            submit = Button(root, text="Submit Password", fg="black", command=partial(sfr.unknown_handling, password), font=16)
            submit.place(relx=0.6, rely=0.85, anchor=CENTER)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_img = Image.fromarray(rgb_frame)
    imgtkinter = ImageTk.PhotoImage(image=frame_img)
    video.imgtk = imgtkinter
    video.configure(image=imgtkinter)

    if recognised:
        connection.write(b'R')
        video.after(500, video.destroy)
        label.configure(text=f"Hello, {name}!")  
    else:
        video.after(10, update_frame, cap, sfr)  
root.mainloop()
