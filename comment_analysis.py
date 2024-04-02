import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import io
import pandas as pd
import numpy as np
import csv
import sys
import os 
import pandas as pd
from textblob import TextBlob



def scrapfyt(url):

  comments_file_path="D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/comments.csv"
  fullcomments_file_path="D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/Full Comments.csv"
  if os.path.exists(comments_file_path):
    os.remove(comments_file_path)
  if os.path.exists(fullcomments_file_path):
    os.remove(fullcomments_file_path)
  option = webdriver.ChromeOptions()
  #option.add_argument('--headless')
  option.add_argument('-no-sandbox')
  option.add_argument("--mute-audio")
  #option.add_argument("--disable-extensions")
  option.add_argument('-disable-dev-shm-usage')

  driver = webdriver.Chrome(service=Service("C:/chrome extension/chromedriver.exe"), options=option)

  driver.set_window_size(960, 800)   
                    
  time.sleep(1)
  driver.get(url)
  time.sleep(2)


  pause = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ytp-play-button')))

  pause.click()
  time.sleep(0.2)
  pause.click()
  time.sleep(4) #change
  driver.execute_script("window.scrollBy(0,500)","")
    
  last_height = driver.execute_script("return document.documentElement.scrollHeight")

  while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    time.sleep(4)
    
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
      break
    last_height = new_height

  driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

  video_title = driver.find_element(By.NAME, 'title').get_attribute('content')

  video_owner1 = driver.find_elements(By.XPATH, '//*[@id="text"]/a')
  video_owner = []
  for owner in video_owner1:
    video_owner.append(owner.text)
  video_owner = video_owner[0]

  video_comment_with_replies = driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]').text + ' Comments'

  users = driver.find_elements(By.XPATH, '//*[@id="author-text"]/span')
  comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

  with io.open('storage/comments.csv', 'w', newline='', encoding="utf-16") as file:
      writer = csv.writer(file, delimiter =",", quoting=csv.QUOTE_ALL)
      writer.writerow(["Comment"])
      for comment in comments:
          writer.writerow([comment.text])
    
  commentsfile = pd.read_csv("storage/comments.csv", encoding ="utf-16") 

  all_comments = commentsfile.replace(np.nan, '-', regex = True)
  all_comments = all_comments.to_csv("storage/Full Comments.csv", index = False)
  video_comment_without_replies = str(len(commentsfile.axes[0])) + ' Comments'

  # print(video_title, video_owner, video_comment_with_replies, video_comment_without_replies)
  driver.close()
  p,n=analyze()
  return p,n



def analyze():
    
    df = pd.read_csv("D:/ENGINEERING/MATERIAL 8TH SEMESTER/PROJECT PHASE 2/Final Project/storage/Full Comments.csv", encoding='latin1')

    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment_score(comment):
        sentiment_scores = analyzer.polarity_scores(comment)
        return sentiment_scores['compound']

    df['sentiment_score'] = df['Comment'].apply(get_sentiment_score)

    threshold = 0
    df['sentiment'] = df['sentiment_score'].apply(lambda x: 'positive' if x >= threshold else 'negative')

    positive_count = df[df['sentiment'] == 'positive'].shape[0] 
    negative_count = df[df['sentiment'] == 'negative'].shape[0]

    positive_proportion=positive_count/df.shape[0]
    negative_proportion=negative_count/df.shape[0]
    #print(f"Proportion of positive comments: {positive_proportion:.2%}")
    #print(f"Proportion of negative comments: {negative_proportion:.2%}")
    return positive_proportion,negative_proportion
