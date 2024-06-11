#Importing libraries

import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import CreateCSV
import TakeAttendance
import webbrowser

import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk


# Using frontal face detector of dlib
detector = dlib.get_frontal_face_detector()

class Face_Register:
    def __init__(self):

        self.current_frame_faces_cnt = 0  #  Counting frames in current frame
        self.existing_faces_cnt = 0  # Counting Saved Faces
        self.ss_cnt = 0  #  to Count Screen Shots

        # Using Tkinter GUI api
        self.win = tk.Tk()
        self.win.title("Student Face Registration")

        # Window size of Application
        self.win.geometry("1000x550")

        # to show camera
        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        # to show form interface
        self.frame_right_info = tk.Frame(self.win)
        self.label_cnt_face_in_database = tk.Label(self.frame_right_info, text=str(self.existing_faces_cnt))
        self.label_fps_info = tk.Label(self.frame_right_info, text="")
        self.input_name = tk.Entry(self.frame_right_info)
        self.input_name_char = ""
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in current frame: ")
        self.log_all = tk.Label(self.frame_right_info)

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=12, weight='bold')
        self.font_warning = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "data/Registered_Faces/"
        self.current_face_dir = ""
        self.font = cv2.FONT_ITALIC

        # for current frame and Region of Interest (ROI)
        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False
        self.face_folder_created_flag = False

        # to calculate Frames Per Second FPS
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(0)  # Get video stream from camera

    # function to run Take Attendance main() function file
    def runAT(self):
        self.win.destroy()
        TakeAttendance.main()

    # function to run Flask App Python file
    def runApp(self):
        webbrowser.open("http://127.0.0.1:5000")


    # to clear entries from database
    def GUI_clear_data(self):
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera + folders_rd[i])
        if os.path.isfile("data/Student_Features.csv"):
            os.remove("data/Student_Features.csv")
        self.label_cnt_face_in_database['text'] = "0"
        self.existing_faces_cnt = 0
        self.log_all["text"] = "All entries removed!"
        self.log_all["fg"] = 'purple'

    #to get input
    def GUI_get_input_name(self):
        self.input_name_char = self.input_name.get()
        self.create_face_folder()
        self.label_cnt_face_in_database['text'] = str(self.existing_faces_cnt)

    # creating GUI for the application
    def GUI_info(self):
        tk.Label(self.frame_right_info,
                 text="Register Student",
                 font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        tk.Label(self.frame_right_info, text="FPS: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_fps_info.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, text="Students in database: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_cnt_face_in_database.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # to clear old data through a remove button
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Step 1: Remove old entries").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        tk.Button(self.frame_right_info,
                  text='Remove',
                  command=self.GUI_clear_data,
                  activebackground='yellow').grid(row=5, column=1, columnspan=3, sticky=tk.W, padx=100, pady=2)

        # creating text field for student name
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Step 2: Enter Student Name").grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="New Student Name: ").grid(row=7, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_name.grid(row=7, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Button(self.frame_right_info,
                  text='Submit',
                  command=self.GUI_get_input_name,
                  activebackground='SpringGreen').grid(row=7, column=2, padx=5)

        # button to save new student entry in a database
        tk.Label(self.frame_right_info,
               font=self.font_step_title,
                 text="Step 3: Save Entry").grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info,
                  text='SAVE',
                  command=self.save_current_face,
                  activebackground='SpringGreen').grid(row=9, column=1, columnspan=3, sticky=tk.W, padx=32, pady=2, ipadx=20)

        # button to run Attendance Taker
        tk.Button(self.frame_right_info,
                  text='Take Attendance',
                  command=self.runAT,
                  activebackground='orange').grid(row=12, column=0, columnspan=3, sticky=tk.W, padx=40, pady=2, ipadx=20, ipady=10)

        # button to run Flask App
        tk.Button(self.frame_right_info,
                  text='Run App',
                  command=self.runApp,
                  activebackground='SpringGreen').grid(row=12, column=1, columnspan=3, sticky=tk.W, padx=80, pady=2, ipadx=20, ipady=10)

        # Show log in GUI
        self.log_all.grid(row=11, column=0, columnspan=20, sticky=tk.W, padx=5, pady=20)

        self.frame_right_info.pack()

    # function for handling directory of CSV file and Student Entries
    def pre_work_mkdir(self):
        if os.path.isdir(self.path_photos_from_camera):
            pass
        else:
            os.mkdir(self.path_photos_from_camera)

    # Start from person_x+1
    def check_existing_faces_cnt(self):
        if os.listdir("data/Registered_Faces/"):
            # Get the order of latest person
            person_list = os.listdir("data/Registered_Faces/")
            person_num_list = []
            for person in person_list:
                person_order = person.split('_')[1].split('_')[0]
                person_num_list.append(int(person_order))
            self.existing_faces_cnt = max(person_num_list)

        # Start from person_1
        else:
            self.existing_faces_cnt = 0

    # refreshing FPS every second
    def update_fps(self):
        now = time.time()
        #  Refresh fps per second
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

        self.label_fps_info["text"] = str(self.fps.__round__(2))

    #  Create the folders for saving faces
    def create_face_folder(self):
        self.existing_faces_cnt += 1
        if self.input_name_char:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt) + "_" + \
                                    self.input_name_char
        else:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt)
        os.makedirs(self.current_face_dir)

        #Showing Successful Message
        self.log_all["text"] = "Entry Successfully Created!"
        self.log_all["fg"] = 'blue'
        logging.info("\n%-40s %s", "Create folders:", self.current_face_dir)

        self.ss_cnt = 0  #  to clear image count
        self.face_folder_created_flag = True  # flag created folder

    def save_current_face(self):
        if self.face_folder_created_flag:
            if self.current_frame_faces_cnt == 1:
                if not self.out_of_range_flag:
                    self.ss_cnt += 1
                    #  Create blank image according to the size of face detected
                    self.face_ROI_image = np.zeros((int(self.face_ROI_height * 2), self.face_ROI_width * 2, 3),
                                                   np.uint8)
                    for ii in range(self.face_ROI_height * 2):
                        for jj in range(self.face_ROI_width * 2):
                            self.face_ROI_image[ii][jj] = self.current_frame[self.face_ROI_height_start - self.hh + ii][
                                self.face_ROI_width_start - self.ww + jj]

                    # to show successfully saved message
                    self.log_all["text"] = "Successfully Saved!"
                    self.log_all["fg"] = 'green'
                    self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2RGB)

                    cv2.imwrite(self.current_face_dir + "/img_face_" + str(self.ss_cnt) + ".jpg", self.face_ROI_image)
                    logging.info("%-40s %s/img_face_%s.jpg", "Save into：",
                                 str(self.current_face_dir), str(self.ss_cnt) + ".jpg")

                    #Calling CSV right after we click SAVE button
                    CreateCSV.main()

                else:
                    #if face is out of ROI
                    self.log_all["text"] = "Try Again: Out of Range!"
                    self.log_all["fg"] = 'red'
            else:
                #if there is no face in the frame
                self.log_all["text"] = "No face detected!"
                self.log_all["fg"] = 'red'
        else:
            # If we click Save before even creating an entry
            self.log_all["text"] = "Please run step 2!"
            self.log_all["fg"] = 'red'

    #generating Camera frames every second
    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640,480))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            #if camera is not available
            print("Error: No video input!!!")

    #   to detect faces and saving them
    def process(self):
        ret, self.current_frame = self.get_frame()
        faces = detector(self.current_frame, 0)
        # Get camera frame
        if ret:
            self.update_fps()
            self.label_face_cnt["text"] = str(len(faces))
            #  if face detected
            if len(faces) != 0:
                #   Show the ROI of faces
                for k, d in enumerate(faces):
                    self.face_ROI_width_start = d.left()
                    self.face_ROI_height_start = d.top()
                    #  Compute the size of ROI
                    self.face_ROI_height = (d.bottom() - d.top())
                    self.face_ROI_width = (d.right() - d.left())
                    self.hh = int(self.face_ROI_height / 2)
                    self.ww = int(self.face_ROI_width / 2)

                    # If the size of ROI > 480x640
                    if (d.right() + self.ww) > 640 or (d.bottom() + self.hh > 480) or (d.left() - self.ww < 0) or (
                            d.top() - self.hh < 0):
                        self.label_warning["text"] = "OUT OF RANGE"
                        self.label_warning['fg'] = 'red'
                        self.out_of_range_flag = True
                        color_rectangle = (255, 0, 0)
                    else:
                        self.out_of_range_flag = False
                        self.label_warning["text"] = ""
                        color_rectangle = (255, 255, 255)
                    self.current_frame = cv2.rectangle(self.current_frame,
                                                       tuple([d.left() - self.ww, d.top() - self.hh]),
                                                       tuple([d.right() + self.ww, d.bottom() + self.hh]),
                                                       color_rectangle, 2)
            self.current_frame_faces_cnt = len(faces)

            # generating image file
            img_Image = Image.fromarray(self.current_frame)
            img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
            self.label.img_tk = img_PhotoImage
            self.label.configure(image=img_PhotoImage)

        # Refresh frame after 20ms
        self.win.after(20, self.process)

    # this function calls all the necessary functions
    def run(self):
        self.pre_work_mkdir()
        self.check_existing_faces_cnt()
        self.GUI_info()
        self.process()
        self.win.mainloop()

#   Creating the Face_Register class variable and calling the run() function
def main():
    logging.basicConfig(level=logging.INFO)
    Face_Register_con = Face_Register()
    Face_Register_con.run()

if __name__ == '__main__':
    main()
