import os
import shutil
from urllib.parse import urlparse
import glob

def get_new_file(files):
    new_image = files.pop()
    return files, new_image


def move_image(dest_folder,img):
    parsed= urlparse(img)
    filename = os.path.basename(parsed.path)
    print("filename",filename)
    shutil.move(img, dest_folder+"/"+filename)

def is_img_uri(img_uri):
    img_uri=img_uri.lower()
    valid = ["jpg","jpeg","png"]
    for v in valid:
        if v in img_uri:
            return True
    return False

def read_files(source_folder):
    file_types=["jpg","png","jpeg"]

    files = []
    for ext in file_types:
        files += glob.glob(f"{source_folder}/*.{ext}")
    return files