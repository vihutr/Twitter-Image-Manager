from pathlib import Path
import cv2
import requests
import os

script_dir = os.path.dirname(__file__)

def convert_image_url_to_filename(url):
    file_name = url[28:43] + '.' + url[51:54]

    return(file_name)

def check_dir(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

def create_download_path(file_name, folder_name):
    rel_path = os.path.join('downloads', folder_name)
    folder_path = os.path.join(script_dir, rel_path)
    print(folder_path)
    check_dir(folder_path)

    path = os.path.join(folder_path, file_name)
    return(path)

class ImageDownloader:
    def __init__(self, output_dir='./downloads', sort=False):
        output_dir = Path(output_dir)
        Path.mkdir(output_dir, parents = True, exist_ok = True)
        self.output_dir = str(output_dir)
        self.sort = sort
    
    def download_image(self, url, username):
        file_name = convert_image_url_to_filename(url)
        print(f'filename in dlimg:{file_name}')
        path = os.path.join(self.output_dir, file_name)
        print(path)
        img_data = requests.get(url).content
        print(f"saving {file_name} to {path}")
        with open(path, 'wb') as handler:
            handler.write(img_data)
        if not self.sort:
            return(file_name, path)
        
        img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
        screen_res = 1920, 1080
        scale_width = screen_res[0] / img.shape[1]
        scale_height = screen_res[1] / img.shape[0]
        scale = min(scale_width, scale_height)
        window_width = int(img.shape[1] * scale)
        window_height = int(img.shape[0] * scale)
        cv2.namedWindow(path, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(path, window_width, window_height)
        cv2.moveWindow(path, 0,0)
        cv2.imshow(path, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        pathinput = input('Folder Name:')    
        new_folder_path = os.path.join(folder_path, pathinput) 
        Path.mkdir(new_folder_path, parents = True, exist_ok = True)
        new_path = os.path.join(new_folder_path, file_name)
        if(not os.path.exists(new_path)):
            print(f"moving {path} to {new_path}")
            os.rename(path, new_path)
        else:
            print("file already exists, skipping")
        return(file_name, new_path)


