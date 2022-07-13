from flask import Flask, send_from_directory, request
from flask_cors import CORS, cross_origin
from factchecker import CheckFact, retrieveEvidence;
from os.path import exists
import requests
import zipfile
from tqdm import tqdm

if(not exists("./model/model.zip")):
    model = requests.get('https://kant.cs.man.ac.uk/data/public/smaite/model.zip', stream=True)
    total = int(model.headers.get('content-length', 0))
    with open("./model/model.zip", 'wb') as file, tqdm(
        desc="./model/model.zip",
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in model.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    with zipfile.ZipFile("./model/model.zip", 'r') as zip_ref:
        zip_ref.extractall("./model/")


app = Flask(__name__, static_url_path='', static_folder='../smaite_frontend/build')
CORS(app, support_credentials=True)

@app.route("/myapi/fact_check", methods=['GET'])
@cross_origin(supports_credentials=True)
def explanation():
    claim = request.args.get('claim')
    mode = request.args.get('mode')
    if(mode == "summarize"):
        return {"claim": claim, "explanations":CheckFact(claim, "summarize"), "evidence": retrieveEvidence(claim)}
    elif(mode == "generate"):
        return {"claim": claim, "explanations":CheckFact(claim, "generate"), "evidence": retrieveEvidence(claim)}
    else:
        return {"claim": claim, "explanations":"Invalid mode selected."}


if(__name__ == "__main__"):
    app.run(debug=True)