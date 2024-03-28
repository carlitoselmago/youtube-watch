from curiosity import curiosity
import numpy as np

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from PIL import Image
from io import BytesIO
import os
from helpers import *
from time import sleep

# Your starting YouTube video URL
video_url = input("Enter starting youtube video: ")

adblockextension='/home/zorin/.var/app/com.google.Chrome/config/google-chrome/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.56.0_0'

cur=curiosity(False,336,188)

# Create the 'thumbs' directory if it doesn't exist
if not os.path.exists('thumbs'):
    os.makedirs('thumbs')

# Define the path to your CSV file
csv_file_path = 'saved_videos.csv'

# Check if the file exists and delete it if it does
if os.path.exists(csv_file_path):
    os.remove(csv_file_path)

# Setting up the WebDriver with webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument(f"load-extension={adblockextension}")
options.headless = False  # Run in headless mode

#add ad blocker


driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

all_videos=[]

try:
    # Navigate to the YouTube video
    driver.get('https://www.youtube.com/')
    sleep(3)
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
    
    index=0
    while True:
        print("---start---",video_url)
        driver.get(video_url)
        sleep(3)
        # Wait for the page to load and for thumbnails to be available
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "ytd-comments"))
        )

        # Find all related video thumbnails
        #thumbnails = driver.find_elements(By.XPATH, '//a[@id="thumbnail"][@class="yt-simple-endpoint inline-block style-scope ytd-thumbnail"]')
        thumbnails = driver.find_elements(By.ID, "thumbnail")

        video_urls = []
        thumbnails_img= []
        mse_scores=[]

        # Iterate over thumbnails, download, and save them
        for i, thumbnail in enumerate(thumbnails):
            video_url = thumbnail.get_attribute("href")
            if video_url:
                if video_url not in all_videos:
                    video_urls.append(video_url)
                    all_videos.append(video_url)
                    # Sometimes, the href might not contain a direct link to the thumbnail.
                    # This is a simple workaround to focus on those with direct image sources.
                    try:
                        img_url = thumbnail.find_element(By.TAG_NAME, "img").get_attribute("src")
                        if img_url:
                            response = requests.get(img_url)
                            img = Image.open(BytesIO(response.content))
                            img_uri=f'thumbs/thumb_{i}.jpg'
                            img.save(img_uri)
                            thumbnails_img.append(img_uri)
                            #print(f'Saved thumb_{i}.jpg')

                            #do the image analysis
                            image=cur.prepare_image(img_uri)
                            mse=cur.predict_and_calculate_mse(image)
                            mse*=1000
                            #print("mse",mse)
                            mse_scores.append(mse)
                    except Exception as e:
                        print(f"Error downloading thumbnail {i}: {e}")

        #now update the model
        for img in thumbnails_img:
            image=cur.prepare_image(img)
            cur.update_model_with_new_image(image)
        
        #get the max curiosity score
        maxindex=mse_scores.index(max(mse_scores))

        besturl=video_urls[maxindex]

        print("best url:",besturl)

        #save the best thumbnail
        save_thumbnail(besturl,index)

        #add video url to csv
        with open(csv_file_path, mode='a') as file:
            # If you have headers, you can write them first as follows:
            # file.write('Header1,Header2,Header3\n')
            file.write(besturl + '\n')

        video_url=besturl

        #generate a clean url
        video_url=f'https://youtube.com/watch?v={extract_video_id(video_url)}'

        index+=1

        #debug
        print("video_urls",video_urls)
        print("mse_scores",mse_scores)
        print("thumbnails_img",thumbnails_img)
        print("#########################################")
        print("")

        

finally:
    pass
    #driver.quit()
