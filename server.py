from flask import Flask, request
from flask_cors import CORS, cross_origin
# from factchecker import CheckFact, initialiseES
from factchecker import CheckFact
from os.path import exists
import requests
import zipfile
from tqdm import tqdm
from dotenv import load_dotenv
import os
load_dotenv() 

if(not exists(os.environ.get("MODEL_PATH"))):
    model = requests.get(os.environ.get("MODEL_LINK"), stream=True)
    total = int(model.headers.get('content-length', 0))
    with open(os.environ.get("MODEL_PATH"), 'wb') as file, tqdm(
        desc=os.environ.get("MODEL_PATH"),
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in model.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    with zipfile.ZipFile(os.environ.get("MODEL_PATH"), 'r') as zip_ref:
        zip_ref.extractall(os.environ.get("MODEL_EXTRACTION_PATH"))

if(not exists(os.environ.get("CORPUS_PATH"))):
    corpus = requests.get(os.environ.get("CORPUS_LINK"), stream=True)
    total = int(corpus.headers.get('content-length', 0))
    with open(os.environ.get("CORPUS_PATH"), 'wb') as file, tqdm(
        desc=os.environ.get("CORPUS_PATH"),
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in corpus.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

# initialiseES()

app = Flask(__name__, static_url_path='', static_folder=os.environ.get("FRONTEND_PATH"))
CORS(app, support_credentials=True)

@app.route("/myapi/fact_check", methods=['GET'])
@cross_origin(supports_credentials=True)
def explanation():
    claim = request.args.get('claim')
    mode = request.args.get('mode')
    if(mode == "google" or mode == "stored" ):
        return CheckFact(claim, mode)
    else:
        return {"claim": claim, "explanations":[], "evidence": [], "status": "Invalid mode selected."}

@app.route("/")
def homepage():
    return "<h1>Backend is up and running</h1>"

if(__name__ == "__main__"):
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)