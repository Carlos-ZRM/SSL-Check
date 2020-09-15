from flask import Flask
import ssl
from ssl import *
from flask import Flask, request, json, Response

app = Flask(__name__)
@app.route("/protocols", methods=["GET"])
def verify_protocol():
    ssl_obj = sslcheck()
    return Response(response=json.dumps(ssl_obj.hosts),
                    status=200,
                    mimetype='application/json')

@app.route("/hosts", methods=["GET"])
def host_info():
    ssl_obj = sslcheck()
    js = ssl_obj.main()
    return Response(response=json.dumps(js),
                    status=200,
                    mimetype='application/json')

@app.route("/hosts_txt", methods=["GET"])
def host_info_txt():
    ssl_obj = sslcheck()
    st = ssl_obj.main_text()
    return st

@app.route("/certificates", methods=["GET"])
def cert_info():
    ssl_obj = sslcheck()
    ssl_obj.main()
    js = ssl_obj.dic_vencidos()
    return Response(response=json.dumps(js),
                    status=200,
                    mimetype='application/json')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)

