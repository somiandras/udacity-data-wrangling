import pprint as pp
from pymongo import MongoClient
client = MongoClient()
db = client.openstreetmap
collection = db.budapest

count = collection.find().count()
print(count)

grouped = collection.aggregate([
    {'$group': {
        '_id': '$type',
        'count': {'$sum': 1}
    }},
])

pp.pprint(list(grouped))

postcodes = collection.aggregate([
    {'$match': {
        'address.postcode': {'$exists': True}
    }},
    {'$group': {
        '_id': '$address.postcode',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 10}
])

pp.pprint(list(postcodes))
