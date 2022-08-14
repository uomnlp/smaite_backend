from os.path import exists
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import os
load_dotenv() 
import shutil  
import json
from bs4 import BeautifulSoup
from Levenshtein import distance as levenshtein_distance, ratio as levenshtein_ratio
import math
from unidecode import unidecode
from server import download_file
import sys

if not os.path.exists(os.environ.get("SCRAPED_DATA_EXTRACTION_PATH")):
    os.makedirs(os.environ.get("SCRAPED_DATA_EXTRACTION_PATH"))

if(not exists(os.environ.get("SCRAPED_DATA_DIRECTORY_1"))):
    download_file(os.environ.get("SCRAPED_DATA_DIRECTORY_1"), os.environ.get("SCRAPED_DATA_DOWNLOAD_1"))
    shutil.unpack_archive(os.environ.get("SCRAPED_DATA_DIRECTORY_1"), os.environ.get("SCRAPED_DATA_EXTRACTION_PATH"))

if(not exists(os.environ.get("SCRAPED_DATA_DIRECTORY_2"))):
    download_file(os.environ.get("SCRAPED_DATA_DIRECTORY_2"), os.environ.get("SCRAPED_DATA_DOWNLOAD_2"))
    shutil.unpack_archive(os.environ.get("SCRAPED_DATA_DIRECTORY_2"), os.environ.get("SCRAPED_DATA_EXTRACTION_PATH"))

def filter_snippets(snippets):
    blacklist_keywords = ["Jan ", "Feb ", "Mar ", "Apr ", "May ", "Jun ", "Jul ", "Aug ", "Sep ", "Oct ", "Nov ", "Dec "]
    snippets = item['snippet'].split("...")
    snippets = list(filter(lambda x: x != None and len(x) > 5 and not any(keyword in x for keyword in blacklist_keywords), snippets))
    return snippets

def filter_results(results):
    if(int(results['searchInformation']['totalResults']) < 1 or len(results['items']) < 1):
        return True
    return False

num_lines_input = sum(1 for line in open(os.environ.get("SCRAPED_DATA_1")))
num_lines_output = sum(1 for line in open(os.environ.get("OUTPUT_FILE_2_NAME"), "a+"))
with open(os.environ.get("SCRAPED_DATA_1")) as file:
    with open(os.environ.get("OUTPUT_FILE_NAME"), 'a+', buffering=1) as output_file, open(os.environ.get("OUTPUT_FILE_2_NAME"), 'a+', buffering=1) as output_file_2:
        for count, line in enumerate(tqdm(file, total=num_lines_input, file=sys.stdout)):
            try:
                if count <= num_lines_output:
                    continue
                refinedData = []
                lineJSON = json.loads(line.strip())

                if(filter_results(lineJSON['results'])):
                    continue

                for item in lineJSON['results']['items']:
                    snippets = filter_snippets(item['snippet'])

                    # Final data of the particular search result
                    finalData = {'link': item['link'],
                                'snippet': '',
                                'title' : item['title'],
                                'originalSnippet' : item['snippet'],
                                'method': None,
                                'distance': 0,
                                'ratio': 0} 
                                # original (distance = None)
                                # exact (distance >= 0) - exact can be a mixture of similar and exact due to sub snippets
                                # similarity (distance > 0)
                    tmpRatios = []
                    
                    if(item['full_website'] == "FETCH_ERROR"):
                        finalData['snippet'] = item['snippet']
                        finalData['method'] = 'original'
                        finalData['distance'] = None
                        finalData['ratio'] = None
                    else:                
                        soup = BeautifulSoup(item['full_website'], features="html.parser")
                        isExactMatch = False # Represents if even one sub snippet has an exact match
                        # Select the best matching <p> tags for each part of the short snippet (delineated by ...)
                        for snip in snippets:
                            # Best match <p> tag for the particular sub-snippet
                            selectedTags = {'distance' : math.inf, 'ratio': 0, 'text' : ''}
                            snip = unidecode(snip).strip()
                            checkSimilarity = True

                            # Select the <p> tag text with the least Edit Distance
                            for tag in soup.find_all(['p', 'div', 'span']):
                                tagText = unidecode(tag.text).strip()

                                # If the paragraph is empty 
                                if(len(tagText) < 1):
                                    continue

                                # Break if exact match
                                if snip in tagText:
                                    if checkSimilarity:
                                        selectedTags['text'] = [tagText]
                                    else:
                                        selectedTags['text'].append(tagText) 
                                    selectedTags['distance'] = 0
                                    selectedTags['ratio'] = 0
                                    checkSimilarity = False
                                    isExactMatch = True

                                # Calculate the levenshtein distance
                                if(checkSimilarity):
                                    editDistance = levenshtein_distance(snip, tagText)
                                    
                                    if(editDistance < selectedTags['distance']):
                                        selectedTags['distance'] = editDistance
                                        selectedTags['text'] = tagText

                                    selectedTags['ratio'] = levenshtein_ratio(snip, tagText)
                            
                            # Append the text to the final text if similarity found
                            if(selectedTags['distance'] != math.inf and checkSimilarity):
                                finalData['snippet'] += selectedTags['text'] + '\n '
                                finalData['distance'] +=  selectedTags['distance']
                                
                                # Record the ratio for averaging later
                                tmpRatios.append(selectedTags['ratio'])

                                # Appending the output for the subsnippet ABC or XYZ in ABC..XYZ  (no append if original)
                                refinedData.append({'link': item['link'],
                                'snippet': selectedTags['text'] + '\n ',
                                'title' : item['title'],
                                'originalSnippet' : snip,
                                'method': "similarity",
                                'distance': selectedTags['distance'],
                                'ratio':selectedTags['ratio']  })
                            # Append the minimum length text to the final text if exact match
                            elif(selectedTags['distance'] != math.inf):
                                finalData['snippet'] += min(selectedTags['text'], key=len) + '\n '
                                
                                tmpRatios.append(1)

                                # Appending the output for the subsnippet ABC or XYZ in ABC..XYZ  (no append if original)
                                refinedData.append({'link': item['link'],
                                'snippet': min(selectedTags['text'], key=len) + '\n ',
                                'title' : item['title'],
                                'originalSnippet' : snip,
                                'method': "exact",
                                'distance': 0,
                                'ratio': 1})
                        # Append the text to the final text for the result only if a result found else append with original snippet
                        if(finalData['snippet'] != ""):
                            if isExactMatch:
                                finalData['method'] = 'exact'
                            else:
                                finalData['method'] = 'similarity'
                            # Averaging out the ratios
                            finalData['ratio'] = sum(tmpRatios)/len(tmpRatios)
                            refinedData.append(finalData)
                        else: 
                            # If snippet is empty, use originalSnippet instead (could happen when there is no HTML text at all)
                            finalData['snippet'] = item['snippet']
                            finalData['method'] = 'original'
                            finalData['distance'] = None
                            finalData['ratio'] = None
                            refinedData.append(finalData)
                    # To output 1 snippet/line (not useful for training)
                    # output_file.write(json.dumps(finalData))
                    # output_file.write('\n')
                lineJSON['results'] = refinedData
                output_file_2.write(json.dumps(lineJSON))
                output_file_2.write('\n')
            except:
                print('Error on line #%s ' % str(count), file=sys.stderr, end='\n')
                continue

                
            
    # print(json.dumps(refinedData))
    # print(len(refinedData))
    # print(len(list(filter(lambda x: x['method'] == "exact", refinedData))))
    # print(len(list(filter(lambda x: x['method'] == "original", refinedData))))
    # print(len(list(filter(lambda x: x['method'] == "similarity", refinedData))))

    