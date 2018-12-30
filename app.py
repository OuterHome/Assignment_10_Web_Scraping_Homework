from flask import Flask, render_template, redirect, jsonify
#import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo
import scrape_mars
from jinja2 import Template
import pandas as pd


app = Flask(__name__)

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = MongoClient(conn)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"
mongo = PyMongo(app)

# Define database and collection
#db = client.mars
#collection = db.mars_data

@app.route('/')
def index():
    mars = mongo.db.mars#.find()
    return render_template('index.html', mars=mars, data=mars.mars_facts.to_html(escape = False))
    #titles = ["Facts", "Criteria"])

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