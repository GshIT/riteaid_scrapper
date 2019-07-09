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
			scategories = read_file('scategories.json')
			scategories.append(category)
			write_file('scategories.json',scategories)
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

def get_products(html):
	soup = BeautifulSoup(html,'html.parser')                                                                                                                        
	products = soup.select('ul.products-grid li a.product-image')
	return products

def copy_scategories():
	scategories = read_file('scategories.json')
	write_file('leftscategories.json', scategories)

def get_purl(products):
	return [product.get('href') for product in products]

def paginate(html):
	soup = BeautifulSoup(html,'html.parser')
	nextb = soup.select_one('li.next-btn')
	return True if nextb else False

@retry('products_url.json')
def get_product_links():
	categories = [] if not read_file('leftscategories.json') else read_file('leftscategories.json')
	cookies = {'CATEGORY_INFO': '{"is_ajax":"1","limit":"36"}'}
	fstring = "?limit=36&p={}" 
	products = [] if not read_file("products_url.json") else read_file("products_url.json")                                                                            

	while categories:
		nextp = True
		i = read_file('state.json').get('state')
		while nextp:
			temp = []
			nextp = False
			url = categories[-1]['url']
			print(f"Scrapping: {url}{fstring.format(i)}")
			res = rq.get(f"{url}{fstring.format(i)}", cookies=cookies)
			write_file('state.json', {"state": i})
			if not res.ok: raise Exception("Categories Url Failed")

			products_container = get_products(res.text)
			purls = get_purl(products_container)
			temp = [{'product_url': purl, 'category': categories[-1]['path'], "category_url": f"{url}{fstring.format(i)}"} for purl in purls]
			products.extend(temp)
			write_file('products_url.json', products)
			if paginate(res.text): nextp = True
			i = i + 1

		categories.pop()
		write_file('leftscategories.json',categories)
		write_file('state.json', {"state": 1})

	return products
