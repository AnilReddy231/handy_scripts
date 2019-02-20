#Python script which will scrape the data from a website and output the results to locally running ElasticSearch data base

import json
from time import sleep
import requests
from bs4 import BeautifulSoup
import logging
from elasticsearch import Elasticsearch

def connect_elasticsearch():
	is_connected = True
	_es = Elasticsearch('http://localhost:9200')
	if _es.ping():
		print('Connected Successfully')
	else:
		print('Failed to connect, Please double check')
		is_connected=False
	return is_connected,_es

def create_index(es_object, index_name):
	created = True
	# index settings
	settings = {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		},
		"mappings": {
			"tires": {
				"dynamic": "strict",
				"properties": {
					"season": {
						"type": "text"
					},
					"tire_type": {
						"type": "text"
					},
					"tire_name": {
						"type": "text"
					},
					"starting_price": {
						"type": "text"
					}
				}
			}
		}
	}

	try:
		if not es_object.indices.exists(index_name):
			# Ignore 400 means to ignore "Index Already Exist" error.
			es_object.indices.create(index=index_name, ignore=400, body=settings)
			print('Created Index')
		
	except Exception as ex:
		print(str(ex))
		created = False
	finally:
		return created

def store_record(elastic_object, index_name, record):
	is_stored = True
	try:
		outcome = elastic_object.index(index=index_name, doc_type='tires', body=record)
		print(outcome)
	except Exception as ex:
		print('Error in indexing data')
		print(str(ex))
		is_stored = False
	finally:
		return is_stored

def parse(title,price):
	tire_type=""
	rec={}
	try:
		model_section = title.select('.tire-heading__model')
		
		type_section = title.select('.tire-heading__type')
		
		driving_section = title.select('.tire-heading__driving')
		
		price_dollar = price.select('.tire-price__dollar')
		
		if price_dollar[0].text != "N/A":
			dollar = price_dollar[0].text 
			price_cents = price.select('.tire-price__cents')
			if driving_section:
				driving = driving_section[0].text.strip()
			if type_section:
				tire_type = type_section[0].text.strip()
			if model_section:
				model = model_section[0].text
			if price_cents:
				cents = price_cents[0].text	
			rec = {'season': driving, 'tire_type': tire_type, 'tire_name': model,'starting_price':"Starting at"+" "+str(dollar)+"."+str(cents)}
	except Exception as ex:
		print('Exception while parsing')
		print(str(ex))
	finally:
		if bool(rec):
			return json.dumps(rec)

if __name__ == '__main__':
	logging.basicConfig(level=logging.ERROR)
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36', 'Pragma': 'no-cache'}
	url = 'https://www.bridgestonetire.com/catalog'
	r = requests.get(url, headers=headers)
	if r.status_code == 200:
		html = r.text
		soup = BeautifulSoup(html, 'lxml')
		if len(soup.select(".tire-heading")):
			connected,es = connect_elasticsearch()
			print(connected)
			if connected:
				index = create_index(es, 'bridgestone')
				for heading,price in zip(soup.select(".tire-heading"),soup.select(".tire-price")):
					result=parse(heading,price)
					if result:
						out = store_record(es, 'bridgestone', result)
						if out:
							print('Data indexed successfully')
