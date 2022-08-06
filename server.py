from flask import Flask, request
from flask_cors import CORS, cross_origin
from factchecker import CheckFact, initialiseES
from os.path import exists
import requests
import zipfile
from tqdm import tqdm
from dotenv import load_dotenv
import os
load_dotenv() 


def download_file(path, link):
    response = requests.get(link, stream=True)
    total = int(response.headers.get('content-length', 0))
    with open(path, 'wb') as file, tqdm(
        desc=path,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

if not os.path.exists(os.environ.get("MODEL_EXTRACTION_PATH")):
    os.makedirs(os.environ.get("MODEL_EXTRACTION_PATH"))

if(not exists(os.environ.get("MODEL_PATH"))):
    download_file(os.environ.get("MODEL_PATH"), os.environ.get("MODEL_LINK"))
    with zipfile.ZipFile(os.environ.get("MODEL_PATH"), 'r') as zip_ref:
        zip_ref.extractall(os.environ.get("MODEL_EXTRACTION_PATH"))

if(not exists(os.environ.get("CORPUS_PATH"))):
    download_file(os.environ.get("CORPUS_PATH"), os.environ.get("CORPUS_LINK"))

initialiseES()

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


if(__name__ == "__main__"):
    app.run(debug=True)