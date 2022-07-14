from transformers import pipeline
import requests
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
load_dotenv() 

def initialiseES():
    es = Elasticsearch([os.environ.get("ES_DEV_PATH")])
    if not es.indices.exists(index="smaite"):
        options = {
            "settings": {
	        "number_of_shards": 5,
	        "number_of_replicas": 1
	    }}
        es.indices.create(index = 'smaite', body = options)
        bulk_data = []
        with open(os.environ.get("CORPUS_PATH")) as file:
            for line in file:
                try:
                    lineResults = json.loads(line.rstrip())
                    if("results" not in lineResults):
                        continue 
                    if("items" not in lineResults['results']):
                        continue 
                    lineResults = lineResults['results']['items']
                    for result in lineResults:
                        if("title" not in result or "snippet" not in result ):
                            continue 
                        bulk_data.append({"index": {"_index": 'smaite'}})
                        bulk_data.append({"title":result['title'],"snippet":result['snippet']})
                except:
                    print(lineResults)
                    break
        es.bulk(index = 'smaite', body = bulk_data)


def CheckFact(claim, mode):
    # Process the claim
    explanations = []
    if(mode == "google"):
        summarizer = pipeline("summarization")
        result = summarizer(claim, min_length=5, max_length=30)
        for element in result:
            explanations.append(element['summary_text'])
    elif(mode == "stored"):
        textGenerator = pipeline("text-generation")
        result = textGenerator(claim, max_length=30, num_return_sequences=2)
        for element in result:
            explanations.append(element['generated_text'])
    return explanations
    

def retrieveEvidence(claim):
    url = 'https://www.googleapis.com/customsearch/v1?key=%s&q=%s&cx=%s' % (os.environ.get("FACT_CHECK_API_KEY"), claim, os.environ.get("FACT_CHECK_CX"))
    response = requests.get(url)
    response = response.json()
    results = []
    if(int(response['searchInformation']['totalResults']) > 0):
        for item in response['items']:
            results.append({'title':item['title'], 'url': item['link']})
    return results