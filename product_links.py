import requests as rq
from bs4 import BeautifulSoup
import vpn_connect as vc
import json
import time
import re

def retry(file):
	def inner(func):
		def wrapper():
			ret = True
			while ret:
				ret = False

				try: 
					data = func()
				except Exception as e:
					print(e)
					change_country()
					ret = True

			vc.kill()
			write_file(file,data)

			return data
		return wrapper
	return inner

def get_url(container):
	url_container = container.select_one("a")
	return url_container.get('href')

def get_name(container):
	url_container = container.select_one("a")
	return url_container.text.replace('\n','') if url_container else None

def get_path(url):
	path = ""
	if url:
		path_container = re.search(r'.com\/shop\/(.*)', url)
		path = path_container.group(1) if path_container else None
	return path

def get_name_url(html, actual):
	soup = BeautifulSoup(html,'html.parser')
	cat_containers = soup.select("div.left-categories ul#left-navi li")

	temp = []
	same = False

	for cat_container in cat_containers:
		category = {}
		
		category['url'] = get_url(cat_container)
		category['name'] = get_name(cat_container)
		category['path'] = get_path(category['url'])
		temp.append(category)

		if category['name'] == actual:
			scategories = read_file('scategories.py')
			scategories.append(category)
			write_file('scategories.py',scategories)
			temp = []
			break
	return temp

def write_file(file,data):
	with open(file,'w') as f:
		json.dump(data, f, indent=4)

def read_file(file):
	data = []
	with open(file) as f: 
		data = json.load(f)
	return data

@retry('categories.json')
def get_categories():
	categories = [] if not read_file('categories.json') else read_file('categories.json')
	lefts = [{'name':'','url':"https://www.riteaid.com/shop/"}] if not read_file('lefts.json') else read_file('lefts.json')

	while lefts:
		left = lefts[-1]
		url = left['url']

		write_file('lefts.json',lefts)

		print(f'Scrapping: {url}')
		res = rq.get(url)

		if not res.ok: raise Exception("Categories Url Failed")
		lefts.pop()

		temp = get_name_url(res.text, left['name'])
		lefts.extend(temp)
		categories.extend(temp)
		write_file('categories.json',categories)

	return categories

def change_country():
	vc.kill()
	vc.connect('vpn')
	print('Changin Country..')
	time.sleep(4)