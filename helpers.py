import re
from urllib.error import HTTPError
from urllib.request import urlretrieve

def extract_video_id(youtube_url):
    # Regular expression for extracting the video ID from the full YouTube URL
    match = re.search(r"(?<=v=)[^&#]+", youtube_url)
    if match is None:
        # Try the short YouTube URL format
        match = re.search(r"(?<=youtu.be/)[^&#]+", youtube_url)
    if match is not None:
        return match.group(0)
    return None

def save_thumbnail(youtube_url,index):
    videoid=extract_video_id(youtube_url)
    image_local_path='saved_thumbs'
    if videoid:
        image_url=f'https://img.youtube.com/vi/{videoid}/maxresdefault.jpg'
        try:
            urlretrieve(image_url, image_local_path+'/'+str(index)+'.jpg')
        except FileNotFoundError as err:
            print(err)   # something wrong with local path
        except HTTPError as err:
            print(err)  # something wrong with url