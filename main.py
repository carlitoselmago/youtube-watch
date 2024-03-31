from curiosity import curiosity
import numpy as np

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from PIL import Image
from io import BytesIO
import os
from helpers import *
from time import sleep
from queue import Queue
from selenium.webdriver.common.keys import Keys


# Your starting YouTube video URL


adblockextension='/home/zorin/.var/app/com.google.Chrome/config/google-chrome/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.56.0_0'
userprofile='/home/zorin/.var/app/com.google.Chrome/config/google-chrome/Default'

thumb_width=320
thumb_height=180

cleanstart=False
dislike_boring_videos=True
play_videos=True

# Define the path to your CSV file
csv_file_path = 'saved_videos.csv'

##########################################################

if cleanstart:
    video_url = input("Enter starting youtube video: ")
else:
    try:
        video_url = get_last_video_from_csv(csv_file_path)
    except:
        video_url = input("Enter starting youtube video: ")

cur=curiosity(not cleanstart,thumb_width,thumb_height)

# Create the 'thumbs' directory if it doesn't exist
if not os.path.exists('thumbs'):
    os.makedirs('thumbs')



if cleanstart:
    # Check if the file exists and delete it if it does
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
else:
    with open(csv_file_path, 'a'):
        pass 

# Setting up the WebDriver with webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument(f"load-extension={adblockextension}")
#options.add_argument(f'user-data-dir={userprofile}')
options.headless = False  # Run in headless mode

#add ad blocker


#driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
fp = webdriver.FirefoxProfile('/home/zorin/.mozilla/firefox/4ryojv0h.default-release')

driver = webdriver.Firefox(fp,executable_path=r'geckodriver')
driver.set_window_position(0, 0)
driver.maximize_window()
#driver = webdriver.Firefox(executable_path=r'geckodriver')

if cleanstart:
    all_videos=[]
else:
    #load videos from csv
    all_videos=load_first_column_from_csv(csv_file_path)
   

try:
    # Navigate to the YouTube video
    driver.get('https://www.youtube.com/')
    sleep(2)
    # Wait for the page to load and for thumbnails to be available
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Check and close the cookies popup if it exists
    try:
        # Wait for the cookies popup button to be clickable
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Accept the use of cookies and other data for the purposes described']"))
        )
        accept_cookies_button.click()
        print("Cookies popup accepted.")
    except Exception as e:
        print("No cookies popup to accept or error clicking accept:", e)
    
    if cleanstart:
        index=0
    else:
        try:
            index=count_lines_in_csv(csv_file_path)
        except:
            index=0

    backup_besturls=[]
    
    while True:
        print("---start---",video_url)
        driver.get(video_url)
        sleep(1)
        # Wait for the video player to be ready
        video_player = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#player"))
        )
        if play_videos:
            #driver.execute_script("document.querySelector('player').play();")
            try:
                # First, find the mute button to check the mute status
                mute_button = driver.find_element(By.CLASS_NAME, 'ytp-mute-button')
                mute_status = mute_button.get_attribute('title')

                # Then, determine whether the video is currently playing
                # Note: This may require adjusting based on how you can best determine play status. This is a placeholder approach.
                play_button = driver.find_element(By.CLASS_NAME, 'ytp-play-button')
                play_status = play_button.get_attribute('aria-label')

                # If the video is playing but muted, unmute it
                print("mute_status",mute_status)
                if 'Unmute' in mute_status:
                    mute_button.click()
                # If the video is not playing (checking if play button says "Play" as an example), and it's not muted, start playing it.
                # This condition might need adjustment based on the actual aria-label or method to determine if playing
                elif 'Pause' in play_status and 'Mute' in mute_status:
                    play_button.click()
            except:
                pass

        # Click on the video player to start playing the video
        #ActionChains(driver).move_to_element(video_player).click().perform()
       
        sleep(1)
        # Wait for the page to load and for thumbnails to be available
        #WebDriverWait(driver, 20).until(
        #    EC.presence_of_element_located((By.TAG_NAME, "ytd-comments"))
        #)

        # Find all related video thumbnails
        #thumbnails = driver.find_elements(By.XPATH, '//a[@id="thumbnail"][@class="yt-simple-endpoint inline-block style-scope ytd-thumbnail"]')
        thumbnails = driver.find_elements(By.ID, "thumbnail")

        video_urls = []
        video_titles=[]
        thumbnails_img= []
        mse_scores=[]
        thumbnails_list=[]

        # Iterate over thumbnails, download, and save them
        for i, thumbnail in enumerate(thumbnails):
            if len(video_titles)<12:
                #print(thumbnail.get_attribute("outerHTML"))
                video_url = thumbnail.get_attribute("href")

                if video_url:
                    try:
                        video_url='https://youtube.com/watch?v='+extract_video_id(video_url)
                    except:
                        video_url=False
                    if video_url:
                        if video_url not in all_videos and "short" not in video_url and "channel" not in video_url:
                            video_urls.append(video_url)
                            
                            thumbnails_list.append(thumbnail)
                            try:
                                title_element =thumbnail.find_element(By.XPATH, ".//ancestor::ytd-compact-video-renderer//h3")
                                video_title = title_element.text if title_element else "No title found"
                                
                            except:
                                video_title="No title"
                            video_titles.append(video_title)
                            # Sometimes, the href might not contain a direct link to the thumbnail.
                            # This is a simple workaround to focus on those with direct image sources.
                            try:

                                #new method
                                img_uri=f'thumbs/thumb_{i}.jpg'
                                if (get_small_thumbnail(video_url,img_uri)):
                                    thumbnails_img.append(img_uri)
                                    image=cur.prepare_image(img_uri)
                                    mse=cur.predict_and_calculate_mse(image)
                                    mse*=1000
                                    #print("mse",mse)
                                    mse_scores.append(mse)

                                    #apply css
                                    opacity=mse/10
                                    #print("opacity",opacity)
                                    #opacity=map_range(opacity,0.3,0.45,0.0,1.0)

                                    print("video_title",video_title,"opacity",opacity)
                                    #if opacity<0.5:
                                    driver.execute_script(f"arguments[0].style.opacity = {opacity};", thumbnail)
                                    if dislike_boring_videos:
                                        if opacity<0.3:
                                            dislikevideo(driver,thumbnail)
                                    
                                
                            except Exception as e:
                                print(f"Error downloading thumbnail {i}: {e}")
                        else:
                            driver.execute_script(f"arguments[0].style.opacity = {0.05};", thumbnail)

        
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.CONTROL + Keys.HOME)

        for img in reversed(thumbnails_img):
            image=cur.prepare_image(img)
            cur.update_model_with_new_image(image,1)
        
        
            
        #get the max curiosity score
        if len(mse_scores)>0:
            
            maxindex=mse_scores.index(max(mse_scores))
            sorted_indices = sorted(range(len(mse_scores)), key=lambda i: mse_scores[i], reverse=True)
            sorted_mse_scores = [mse_scores[i] for i in sorted_indices]
            sorted_video_urls = [video_urls[i] for i in sorted_indices]
            sorted_video_titles=[video_titles[i] for i in sorted_indices]
            sorted_thumbnails_list=[thumbnails_list[i] for i in sorted_indices]
            sorted_thumbnails_img=[thumbnails_img[i] for i in sorted_indices]
            #besturl=video_urls[maxindex]
            besturl=sorted_video_urls[0]
           
            
            if len(backup_besturls)>1:
                print("puttting on queue")
                backup_besturls.append(sorted_video_urls[1])
                if len(backup_besturls)>5:
                    backup_besturls.pop(0)

            print("best url:",besturl)

            #save the best thumbnail
            save_thumbnail(besturl,index)

            #now update the model
            image=cur.prepare_image(sorted_thumbnails_img[0])
            cur.update_model_with_new_image(image,150)

            #add video url to csv
            with open(csv_file_path, mode='a') as file:
                # If you have headers, you can write them first as follows:
                # file.write('Header1,Header2,Header3\n')
                file.write(besturl + ', '+sorted_video_titles[0]+'\n')

            video_url=besturl
            #debug
            #print("video_urls",sorted_video_urls)
            print("mse_scores",sorted_mse_scores)
            #print("sorted_video_titles",sorted_video_titles)
            print("#########################################")
            print("")

        else:
            print("got emtpy mse scores, grabbing a backup one")
            video_url=backup_besturls.pop(0)
            

        #generate a clean url
        video_url=f'https://youtube.com/watch?v={extract_video_id(video_url)}'
        all_videos.append(video_url)
        index+=1

        
        #save model
        if not cleanstart:
            cur.save_model()

        

finally:
    pass
    #driver.quit()

