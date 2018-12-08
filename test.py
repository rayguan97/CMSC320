from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import re
import json

root = 'http://www.imdb.com'

headers = {'Accept-Language': 'en-US'}
url = 'http://www.imdb.com/title/tt4645330/?ref_=adv_li_i'


def get_company(url):
	html = requests.get(url, headers=headers).content
	soup = BeautifulSoup(html, 'html.parser')
	print(soup.find("meta",  property="og:title")['content'])
	company = soup.find("meta",  property="og:title")['content'].replace('With', '(').split('(')[1].strip()
	return company

movie_html = requests.get(url, headers=headers).content

soup = BeautifulSoup(movie_html, 'html.parser')
genre = soup.find("script", type="application/ld+json")

js = json.loads(genre.text)

companies_url = [ c['url'] for c in js['creator'] if c['@type'] == 'Organization' ]
# test = get_company(root+companies_url[0])

print(companies_url[1])
print(js['creator'])






