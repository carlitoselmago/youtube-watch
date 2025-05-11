
import random
from curiosity import curiosity
from helpers.helpers import *
import sys
import eel


# SETTINGS ::::::::::::::::::::::::::::::
source_folder = "images/input" # without ending slash
dest_folder = "images/output" # without ending slash
group_number = 3 # amount of files to process
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

runs=0

while len(files)>0:

    group_count=0
    group = []
    mse_scores = []

    if runs==1:
        # if second run limit to minus winner
        group_number-=1
    if runs>0:
        eel.remove_all_medals()
        # add winner to first position
        files,group,mse_scores,img_uri=add_image_to_group(files,best_image,group,cur,mse_scores)

    while group_count < group_number:
    #for i in range(group_number):
        # get a new image
        try:
            files, img_uri = get_new_file(files)
            files,group,mse_scores,img_uri=add_image_to_group(files,img_uri,group,cur,mse_scores)
            if GUI:
                send_image_to_js(eel,img_uri)
            group_count+=1
        except Exception as e:
            pass
    
        
    
    if GUI:
        eel.send_message("COMPUTING LESS-BORING RANK...")
        eel.sleep(5.0)  

    # now update the model
    for img_uri in group:
        try:
            image=cur.prepare_image(img_uri)
            
            cur.update_model_with_new_image(image,1)
        except Exception as e:
            print("coundn't update model with image",e)

    if GUI:
        mse_scores_norm=[float(i)/sum(mse_scores) for i in mse_scores]
        scores_str="["
        for s in mse_scores_norm:
            scores_str+=str(round(s,2))+","
        scores_str=scores_str[0:-1]
        scores_str+="]"
        eel.send_message(f"RESULTS: {scores_str}")
        eel.rank(mse_scores)
        eel.sleep(5.0)


    # sort by curiosity score
    maxindex=mse_scores.index(max(mse_scores))
    sorted_indices = sorted(range(len(mse_scores)), key=lambda i: mse_scores[i], reverse=True)
    sorted_mse_scores = [mse_scores[i] for i in sorted_indices]
    sorted_imgs=[group[i] for i in sorted_indices]
    print("sorted_mse_scores",sorted_mse_scores)
    print("sorted_imgs",sorted_imgs)
    best_image = sorted_imgs[0]

    # save best image to folder
    #move_image(dest_folder,best_image)
    copy_image(dest_folder,best_image)
    sorted_img.append(best_image)
    
    if GUI:
        eel.end_round()
        eel.sleep(2.0)

    #files = read_files(source_folder)

    runs +=1
    

    if len(files)==1:
        if len(sorted_img)>0:
            files=sorted_img
        else:
            print("FIN")
            files = read_files(source_folder)
            # shuffle files in random order
            random.shuffle(files)
            sorted_img = []
