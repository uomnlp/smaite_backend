import lorem
from transformers import pipeline
import requests

def CheckFact(claim, mode):
    # Process the claim
    explanations = []
    if(mode == "summarize"):
        summarizer = pipeline("summarization")
        result = summarizer(claim, min_length=5, max_length=30)
        for element in result:
            explanations.append(element['summary_text'])
    elif(mode == "generate"):
        textGenerator = pipeline("text-generation")
        result = textGenerator(claim, max_length=30, num_return_sequences=2)
        for element in result:
            explanations.append(element['generated_text'])
    return explanations
    

def retrieveEvidence(claim):
    key = "AIzaSyCrhF3JQ_rbEpv1j9rXhUjNypjlrBbmJ2Y"
    cx = "641c8f210757ecadd"
    url = 'https://www.googleapis.com/customsearch/v1?key=%s&q=%s&cx=%s' % (key, claim, cx)
    response = requests.get(url)
    response = response.json()
    results = []
    if(int(response['searchInformation']['totalResults']) > 0):
        for item in response['items']:
            results.append({'title':item['title'], 'url': item['link']})
    return results