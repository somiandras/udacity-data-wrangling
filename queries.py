import pprint as pp
from pymongo import MongoClient
client = MongoClient()
db = client.openstreetmap

# Count of documents in collection
count = db.budapest.find().count()
print('\nCOUNT OF DOCUMENTS: {}\n'.format(count))

# Count of different types of tags
grouped = db.budapest.aggregate([
    {'$group': {
        '_id': '$type',
        'count': {'$sum': 1}
    }},
    {'$project': {
        '_id': 0,
        'type': '$_id',
        'count': 1
    }}
])
print('\nCOUNT BY TAGS\n')
pp.pprint(list(grouped))

# Top 10 postcodes by count of tags
postcodes = db.budapest.aggregate([
    {'$match': {
        'address.postcode': {'$exists': True}
    }},
    {'$group': {
        '_id': '$address.postcode',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 10},
    {'$project': {
        '_id': 0,
        'postcode': '$_id',
        'count': 1
    }}
])

print('\nTOP 10 POSTCODES\n')
pp.pprint(list(postcodes))

# Number of users
users = db.budapest.distinct('created.user')
print('\nNUMBER OF CONTRIBUTORS: {}\n'.format(len(users)))

# Top 10 users by occurence

agg = db.budapest.aggregate([
    {'$group': {
        '_id': '$created.user',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 10},
    {'$project': {
        '_id': 0,
        'username': '$_id',
        'count': 1
    }}
])
print('\nTOP 10 USERS:\n')
pp.pprint(list(agg))
