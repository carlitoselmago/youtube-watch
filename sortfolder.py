
import random
from curiosity import curiosity
from helpers.helpers import *
import sys
import eel

# SETTINGS ::::::::::::::::::::::::::::::
source_folder = "thumbs"
dest_folder = "sorted"
group_number = 4 # amount of files to process
GUI = True
# :::::::::::::::::::::::::::::::::::::::

cur = curiosity(savemodel=False)

files = read_files(source_folder)


# shuffle files in random order
random.shuffle(files)


sorted_img = []


if GUI:
    # Initialize Eel (ensure the "web" folder contains the frontend)
    eel.init("web")

    # Start the GUI and keep Eel running
    eel.start("index.html", size=(300,300), default_path=source_folder,block=False,mode='firefox')

while len(files)>0:

    group = []
    mse_scores = []

    for i in range(group_number):

        # get a new image
        files, img_uri = get_new_file(files)

        if GUI:
            eel.add_image(img_uri)
            eel.sleep(1.0)

        group.append(img_uri)
        image=cur.prepare_image(img_uri)
        mse=cur.predict_and_calculate_mse(image)
        mse*=1000
        mse_scores.append(mse)

    
    # now update the model
    for img_uri in group:
        image=cur.prepare_image(img_uri)
        cur.update_model_with_new_image(image,1)

    # sort by curiosity score
    maxindex=mse_scores.index(max(mse_scores))
    sorted_indices = sorted(range(len(mse_scores)), key=lambda i: mse_scores[i], reverse=True)
    sorted_mse_scores = [mse_scores[i] for i in sorted_indices]
    sorted_imgs=[group[i] for i in sorted_indices]
    print("sorted_mse_scores",sorted_mse_scores)
    print("sorted_imgs",sorted_imgs)
    best_image = sorted_imgs[0]

    # save best image to folder
    move_image(dest_folder,best_image)
    sorted_img.append(best_image)
    
    files = read_files(source_folder)