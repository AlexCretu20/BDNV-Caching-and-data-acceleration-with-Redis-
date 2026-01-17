from flask import Flask
from routes import api

app = Flask(__name__)

app.register_blueprint(api)

#import singletonul, nu creez altul
from services.prometheus_exporter import exporter
exporter.start()

if __name__ == '__main__':
    app.run(debug=True,port = 5000, use_reloader=False)