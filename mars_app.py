from flask import Flask, render_template, redirect, jsonify
#import pymongo
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)

# Initialize PyMongo to work with MongoDBs
#conn = 'mongodb://localhost:27017'
#client = pymongo.MongoClient(conn)
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# Define database and collection
#db = client.mars

@app.route('/')
def index():
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrape():
    mars = mongo.db.mars
    data = scrape_mars.scrape()
    mars.update(
        {},
        data,
        upsert=True
    )
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)