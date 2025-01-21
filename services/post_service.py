import os
import requests
from services.news_service import Article
from dotenv import load_dotenv
load_dotenv()


"""
Make Automated Posts to Facebook Page
Written by Arul John
Blog Post: https://aruljohn.com/blog/python-automate-facebook-posts/
"""


# Variables
version = 'v21.0'

# Your App information
access_token = os.getenv("FB_ACCESS_TOKEN")   # Add your Access Token
app_id = os.getenv("FB_APP_ID")         # Add your App ID
app_secret = os.getenv("FB_APP_SECRET")     # Add your App secret
page_id = os.getenv("FB_PAGE_ID")        # Add your Facebook Page ID

#use this
def post_with_url(message="Hello World",url="google.com"):
    baseurl = f'https://graph.facebook.com/{version}/{page_id}/feed'
    payload = {
        'message': message,
        'link': url,
        'access_token': access_token
    }

    # Make Facebook post on your Page
    res = requests.post(baseurl, data=payload, timeout=10)
    print(res.text)

def post_with_img(message='Hello World', image_url=''):
    #To post an image with a caption
    baseurl = f'https://graph.facebook.com/{version}/{page_id}/photos'
    payload = {
        'message': message,
        'url': image_url,
        'published': True,
        'access_token': access_token
    }
    # Make Facebook post on your Page
    res = requests.post(baseurl, data=payload, timeout=10)
    print(res.text)