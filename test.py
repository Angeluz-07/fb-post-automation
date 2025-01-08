#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make Automated Posts to Facebook Page
Written by Arul John
Blog Post: https://aruljohn.com/blog/python-automate-facebook-posts/
"""

import requests

# Explorer
# https://developers.facebook.com/tools/explorer

# Variables
version = 'v21.0'

# Your App information
access_token = ''   # Add your Access Token
app_id = ''         # Add your App ID
app_secret = ''     # Add your App secret
page_id = ''        # Add your Facebook Page ID

# Get long token
print(f'''
curl -i -X GET "https://graph.facebook.com/{version}/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={access_token}"
''')

# To post text with a URL
url= 'google.com'
message = 'Hello World 2' # Update this with the text in your Facebook post

baseurl = f'https://graph.facebook.com/{version}/{page_id}/feed'
payload = {
    'message': message,
    'link': url,
    'access_token': access_token
}

# Make Facebook post on your Page
res = requests.post(baseurl, data=payload, timeout=10)
print(res.text)

# To post an image with a caption
# my_image_url = ''       # Add the URL to the image you want to post
# message = 'Hello World' # Update this with the text in your Facebook post

# baseurl = f'https://graph.facebook.com/{version}/{page_id}/photos'
# payload = {
#     'message': message,
#     'url': my_image_url,
#     'published': True,
#     'access_token': access_token
# }
# # Make Facebook post on your Page
# res = requests.post(baseurl, data=payload, timeout=10)
# print(res.text)