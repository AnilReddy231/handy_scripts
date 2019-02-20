#Python script which will scrape the data from a website and output a random fact

import requests
from bs4 import BeautifulSoup
import random

base_url = 'https://www.did-you-knows.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
facts=[]

def facts_add(soup):
	for fact in soup.findAll('span', attrs={'class':'dykText'}):
		facts.append(fact.text)

def next_page(soup):
	for links in soup.findAll('div', attrs={'class':'pagePagintionLinks'}):
		if soup.findAll('a', attrs={'class':'next'}):
			nav=links.find_all('a')[-1].get('href')
			return nav

def main():
	next_pg=''
	Proceed=True
	try:
		while Proceed:
			url=base_url+next_pg
			response = requests.get(url, headers=headers, timeout=2)
			if response.status_code != 200:
				return False
			soup = BeautifulSoup(response.content,'html.parser')
			facts_add(soup)
			next_pg=next_page(soup)
			if not next_pg:
				Proceed=False
	except requests.ConnectionError as e:
		print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
		print(str(e))
	except requests.Timeout as e:
		print("OOPS!! Timeout Error")
		print(str(e))
	except requests.RequestException as e:
		print("OOPS!! General Error")
		print(str(e))
	except KeyboardInterrupt:
		print("Someone closed the program")
	finally:
		print(f"Total Records  = {len(facts)}")
		print(random.choice(facts).encode('ascii',errors='ignore').decode())

if __name__=='__main__':
	main()
