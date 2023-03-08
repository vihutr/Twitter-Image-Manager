from tkinter import *
from PIL import ImageTk, Image
import os

#TODO:
# Urgent # 
# Add scrollbar for images displayed
# Add a search bar, and options to search for based on metadata
# Add mouse interaction with images to open folder/image

def generate_path_list(dir):
    result = []
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            result.append(os.path.join(subdir, file))
    return result

def calculate_resize(w, h, max):
    ratio = min(max/w, max/h)
    result_w = int(w*ratio)
    result_h = int(h*ratio)
    return result_w, result_h

root = Tk()
root.config(bg="#26242f")
Grid.rowconfigure(0, weight=1)
Grid.columnconfigure(0, weight=1)

frame = Frame(root)
frame.config(bg="#26242f")
frame.grid(sticky=N+S+E+W, column=0, row=0, columnspan=2)

disp_size = 100
img_folder = "./tempdownloads/"
path_list = generate_path_list(img_folder)
grid_r = len(path_list)//10
img_list=[]

i_row = 0
i_col = 0
index = 0

for i in path_list:
    img = Image.open(i)
    w, h = img.size
    new_size = calculate_resize(w, h, disp_size)
    img = img.resize((new_size), Image.ANTIALIAS)
    img_list.append(ImageTk.PhotoImage(img))
    i_col += 1
    if i_col == 10:
        i_col = 0
        i_row += 1
    index += i

#Label(root, image=img_list[-1], width=disp_size, height=disp_size).grid(row = i_row, column = i_col)



mainloop()
