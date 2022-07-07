from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_url_path='', static_folder='../smaite_frontend/build')
CORS(app, support_credentials=True)

@app.route("/explanation")
@cross_origin(supports_credentials=True)
def explanation():
    return {"explanation":["Explanation1","Explanation2","Explanation3"]}

if(__name__ == "__main__"):
    app.run(debug=True)