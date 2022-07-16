from transformers import pipeline
import requests
# from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
load_dotenv() 

# es = Elasticsearch([os.environ.get("ES_DEV_PATH")])
# def initialiseES():
#     if not es.indices.exists(index="smaite"):
#         options = {
#             "settings": {
# 	        "number_of_shards": 5,
# 	        "number_of_replicas": 1
# 	    }}
#         es.indices.create(index = 'smaite', body = options)
#         bulk_data = []
#         with open(os.environ.get("CORPUS_PATH")) as file:
#             for line in file:
#                 try:
#                     lineResults = json.loads(line.rstrip())
#                     if("results" not in lineResults):
#                         continue 
#                     if("items" not in lineResults['results']):
#                         continue 
#                     lineResults = lineResults['results']['items']
#                     for result in lineResults:
#                         if("title" not in result or "snippet" not in result or "link" not in result):
#                             continue 
#                         bulk_data.append({"index": {"_index": 'smaite'}})
#                         bulk_data.append({"title":result['title'],"snippet":result['snippet'], "link": result["link"]})
#                 except:
#                     print(lineResults)
#                     break
#         es.bulk(index = 'smaite', body = bulk_data)
    

def CheckFact(claim, mode):
    # Retrieve evidence
    if(mode == "google"):
        evidences = retrieveGoogleEvidence(claim)
    # elif(mode == "stored"):
    #     evidences = retrieveCorpusEvidence(claim)

    finalEvidence = claim + "\n"
    for evidence in evidences:
        finalEvidence += evidence['title'] + "\n"
        finalEvidence += evidence['snippet'] + "\n"

    explanations = []
    if(len(evidences) > 0):
        # textGenerator = pipeline("text-generation")
        # result = textGenerator(claim, max_length=30, num_return_sequences=2)
        # for element in result:
        #     explanations.append(element['generated_text'])
        summarizer = pipeline("summarization", model=os.environ.get("EXTRACTED_MODEL_PATH"))
        results = summarizer(finalEvidence)
        for result in results:
            explanations.append(result['summary_text'])
        return {"claim": claim, "explanations":explanations, "evidence": evidences, "status": "success"}
    else:
        return {"claim": claim, "explanations":[], "evidence": [], "status": "No evidence found."}

def retrieveGoogleEvidence(query):
    url = 'https://www.googleapis.com/customsearch/v1?key=%s&q=%s&cx=%s' % (os.environ.get("FACT_CHECK_API_KEY"), query, os.environ.get("FACT_CHECK_CX"))
    response = requests.get(url)
    response = response.json()
    evidences = []
    if(int(response['searchInformation']['totalResults']) > 0):
        for item in response['items']:
            evidences.append({'title':item['title'], 'link': item['link'], 'snippet':item['snippet']})
    return evidences

# def retrieveCorpusEvidence(query):
#     hits = es.search(body={"query": { "multi_match": { "query": query, "fields": ["snippet", "title"] } } }, index = 'smaite')["hits"]["hits"]
#     evidences = []
#     for hit in hits:
#         evidences.append(hit['_source'])
#     return evidences