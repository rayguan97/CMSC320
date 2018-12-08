from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import re
import json

root = 'http://www.imdb.com'
url = ('http://www.imdb.com/search/title?count=220&view=simple'
    '&boxoffice_gross_us=1,&title_type=feature&release_date={year}')

headers = {'Accept-Language': 'en-US'}


def get_movies(year):
  movies_html = requests.get(url.format(year=year), headers=headers).content
  soup = BeautifulSoup(movies_html, 'html.parser')
  movies = soup.findAll('a', {'href': re.compile('adv_li_i$')})

  return ['http://www.imdb.com' + m['href'] for m in movies]

def go_to_movie(url):
  movie_html = requests.get(url, headers=headers).content

  return movie_html


def get_company(url):
	for i in range(5):
		if '/company/co0677497/' in url:
			return ''
		try:
			html = requests.get(url, headers=headers).content
			soup = BeautifulSoup(html, 'html.parser')
			company = soup.find("meta",  property="og:title")['content'].replace('With', '(').split('(')[1].strip()
			return company
		except ConnectionError:
			continue;
	return ''



def scrap_details(soup, search_year):

	details = soup.find("script", type="application/ld+json")
	js = json.loads(details.text)
	name = js['name']
	genre = ','.join(js['genre'])

	try:
		runtime = int(soup.find('h4', string='Runtime:').parent.contents[3].text[:-3].strip())
	except AttributeError:
		time = re.findall(r'\d+', js['duration'])
		if len(time) > 1:
			runtime = 60 * int(time[0]) + int(time[1])
		else: 
			runtime = 60 * int(time[0])

	try:
		year = js['datePublished'][:4]
		released = js['datePublished']
	except KeyError:
		year = str(search_year)
		released = 'Not specified'


	score = float(js['aggregateRating']['ratingValue'])
	votes = int(js['aggregateRating']['ratingCount'])
	try:
		rating = js['contentRating']
	except KeyError:
		rating = 'Not specified'

	try:
		companies_url = [ c['url'] for c in js['creator'] if c['@type'] == 'Organization' ]
		if companies_url:
			companies = ','.join([ u for u in [ get_company(root+c_url) for c_url in companies_url ] if u != ''])
		else:
			companies = 'Not specified'
	except TypeError:
		if js['creator']['@type'] == 'Organization':
			companies = get_company(root+js['creator']['url'])
		else:
			companies = 'Personal'

	country = soup.find('a', {'href': re.compile('country_of_origin')}).text
	language = ','.join(l.text for l in soup.find_all('a', {'href': re.compile('primary_language')}) )

	try:
		budget = soup.find('h4', string='Budget:').parent.contents[2].strip()
		if not '$' in budget:
			budget = 'Not specified'
		else:
			budget = float(budget.replace('$','').replace(',',''))
	except AttributeError:
		budget = 'Not specified'

	try:
		gross = soup.find('h4', string='Cumulative Worldwide Gross:').parent.contents[2].strip()[:-1]
		gross = float(gross.replace('$','').replace(',',''))
	except (AttributeError, ValueError):
		try:
			gross = soup.find('h4', string='Gross USA:').parent.contents[2].strip()[:-1]
			gross = float(gross.replace('$','').replace(',',''))
		except (AttributeError, ValueError):
			gross = 'Not specified'


	data_line = {'name': name, 'rating': rating, 'genre': genre, 'runtime': runtime, 'year': year,
	 'released': released, 'score': score, 'votes': votes, 'rating': rating, 'companies': companies, 
	 'country': country, 'language': language, 'budget': budget, 'gross': gross}

	return data_line




def write_csv(data):
  df = pd.DataFrame(data)
  df.to_csv('movies_new.csv', mode='a', index=False)


def main():
	# from 1986 to 2018
  for year in range(1986, 2019):
  	data = []
  	movies = get_movies(year)

  	for movie_url in movies:
  		print(year, '&', movie_url)
  		movie_data = {}
  		movie_html = go_to_movie(movie_url)
  		soup = BeautifulSoup(movie_html, 'html.parser')
  		movie_data.update(scrap_details(soup, year))
  		data.append(movie_data)

  	write_csv(data)
  	print(year, 'done.')



if __name__ == '__main__':
  main()