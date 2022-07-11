from flask import Flask, send_from_directory, request
from flask_cors import CORS, cross_origin
from factchecker import CheckFact;

app = Flask(__name__, static_url_path='', static_folder='../smaite_frontend/build')
CORS(app, support_credentials=True)

@app.route("/myapi/fact_check", methods=['GET'])
@cross_origin(supports_credentials=True)
def explanation():
    claim = request.args.get('claim')
    mode = request.args.get('mode')
    if(mode == "summarize"):
        return {"claim": claim, "explanations":CheckFact(claim, "summarize"), "evidence": ["Evidence 1", "Evidence 2"]}
    elif(mode == "generate"):
        return {"claim": claim, "explanations":CheckFact(claim, "generate"), "evidence": ["Evidence 1", "Evidence 2"]}
    else:
        return {"claim": claim, "explanations":"Invalid mode selected."}


if(__name__ == "__main__"):
    app.run(debug=True)