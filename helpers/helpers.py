import os
import shutil
from urllib.parse import urlparse
import glob
import mimetypes
import base64

def get_new_file(files):
    new_image = files.pop()
    return files, new_image


def move_image(dest_folder,img):
    parsed= urlparse(img)
    filename = os.path.basename(parsed.path)
    print("filename",filename)
    shutil.move(img, dest_folder+"/"+filename)

def copy_image(dest_folder, img):
    parsed = urlparse(img)
    filename = os.path.basename(parsed.path)
    print("filename", filename)
    shutil.copyfile(img, os.path.join(dest_folder, filename))

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

def send_image_to_js(eel,img_path):
    mime_type, _ = mimetypes.guess_type(img_path)
    if mime_type not in ("image/jpeg", "image/png"):
        print("Unsupported image type")
        return

    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    
    # Send both mime type and image string
    eel.add_image({"mime": mime_type, "data": encoded})()

def convertlist_2string(string):
    ret="["
    for s in string:
        ret += f"'{s:.2f}'"
    ret+="]"
    return ret

def add_image_to_group(files,img_uri,group,cur,mse_scores):
    group.append(img_uri)
    image=cur.prepare_image(img_uri)
    
    mse=cur.predict_and_calculate_mse(image)
    mse*=1000
    mse_scores.append(mse)

    return files,group,mse_scores,img_uri