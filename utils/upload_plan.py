import pymongo
import os
import json


client = pymongo.MongoClient('localhost', 27017)
# Connect to our database
db = client['ozp_bot']
works = db['works']

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../fixtures"
cur_path = os.path.join(script_dir, rel_path)
filename = 'plan_works.json'

with open(os.path.join(cur_path, filename), 'r', encoding="utf-8") as f:
    name, _ = filename.split('.')
    data = json.load(f)
    works.insert_many(data)
