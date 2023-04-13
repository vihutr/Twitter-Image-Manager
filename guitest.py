import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import sys
import subprocess
import os

#TODO:
# Urgent # 
# Add scrollbar for images displayed 
# Add a search bar, and options to search for based on metadata
# Add mouse interaction with images to open folder/image

# make mouseover image have some animation to show the image being highlighted

def openImage(path):
    wd = os.getcwd()
    path = os.path.join(wd, path)
    path = os.path.normpath(path)
    print("opening " + path)
    if(os.path.isfile(path)):
        imageViewerFromCommandLine = {'linux':'xdg-open',
                                      'win32':'explorer',
                                      'darwin':'open'}[sys.platform]
        subprocess.Popen([imageViewerFromCommandLine, path])

def openImageInExplorer(path):
    if sys.platform == win32:
        FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        wd = os.getcwd()
        path = os.path.join(wd, path)
        path = os.path.normpath(path)
        print("opening " + path)
        print(os.path.isfile(path))
        subprocess.run([FILEBROWSER_PATH, '/select,', path])
    else:
        print(sys.platform)
    

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

class Scrollable(tk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame, width=1600):

        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)


    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width = canvas_width)

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
    
BGCOLOR = "#25242f"

root = tk.Tk()
root.config(bg=BGCOLOR)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

#header = tk.Frame(root)
body = tk.Frame(root)
#footer = tk.Frame(root)

#header.config(bg=BGCOLOR)
body.config(bg=BGCOLOR)
#header.config(bg=BGCOLOR)

body.grid(sticky=tk.N+tk.S+tk.E+tk.W, column=0, row=0, columnspan=2)


#header.pack()
body.pack()
#footer.pack()
#scrollable_body = Scrollable(body, width=10)

#tk.Label(header, text="Header").pack()
#tk.Label(footer, text="Footer").pack()


'''
frame = Frame(root)
frame.config(bg=BGCOLOR)
frame.grid(sticky=N+S+E+W, column=0, row=0, columnspan=2)
'''

def change(e):
    print("entered grid")
    print(e)
    print(image_label)

disp_size = 100
img_folder = "./tempdownloads"
path_list = generate_path_list(img_folder)
grid_r = len(path_list)//10
img_list=[]
img_dict={}

i_row = 0
i_col = 0
index = 0
for i in path_list:
    img = Image.open(i)
    w, h = img.size
    new_size = calculate_resize(w, h, disp_size)
    img = img.resize((new_size), Image.Resampling.LANCZOS)
    img_list.append(ImageTk.PhotoImage(img))
    image_label = tk.Label(body, image=img_list[-1], width=disp_size, height=disp_size, bg=BGCOLOR)
    image_label.grid(row = i_row, column = i_col, padx=10, pady=10)
    image_label.bind("<Enter>", change)
    img_dict[index] = image_label
    i_col += 1
    if i_col == 10:
        i_col = 0
        i_row += 1
    index += 1
#scrollable_body.update()
for key in img_dict:
    img_dict[key].bind("<Enter>", change)
    #for i in img_list:
    #Label(frame, image=img_list[-1], width=disp_size, height=disp_size).grid(row = i_row, column = i_col)
    
#Label(frame, image=img_list[-1], width=disp_size, height=disp_size).grid(row = i_row, column = i_col)


root.mainloop()
