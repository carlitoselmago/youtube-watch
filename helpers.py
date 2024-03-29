import re
from urllib.error import HTTPError
from urllib.request import urlretrieve
import csv

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

def get_small_thumbnail(youtube_url,uri):
    videoid=extract_video_id(youtube_url)
    image_local_path='saved_thumbs'
    if videoid:
        image_url=f'https://img.youtube.com/vi/{videoid}/mqdefault.jpg'
        try:
            urlretrieve(image_url, uri)
        except FileNotFoundError as err:
            print(err)   # something wrong with local path
            return False
        except HTTPError as err:
            print(err)  # something wrong with url
            return False 
        return True 
    return False

def count_lines_in_csv(file_path):
    """
    Counts the number of lines in a CSV file.

    Parameters:
    - file_path: str, the path to the CSV file.

    Returns:
    - int, the number of lines in the CSV file.
    """
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        line_count = sum(1 for row in csv_reader)
    return line_count

def get_last_video_from_csv(file_path):
    """
    Retrieves the last line of a CSV file.

    Parameters:
    - file_path: str, the path to the CSV file.

    Returns:
    - list, the last line of the CSV file as a list of values.
    """
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        last_line = None
        for row in csv_reader:
            last_line = row  # This will end up being the last row
    return last_line[0]

def load_first_column_from_csv(file_path):
    # This list will hold the first element of each row
    first_column_data = []
    
    # Open the CSV file in read mode
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        # Create a CSV reader object
        csv_reader = csv.reader(csv_file)
        
        # Iterate over each row in the CSV file
        for row in csv_reader:
            if row:  # Check if the row is not empty
                # Append the first element of the row to the list
                first_column_data.append(row[0])
    
    return first_column_data