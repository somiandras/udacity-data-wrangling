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

# Top 5 postcodes by count of tags
postcodes = db.budapest.aggregate([
    {'$match': {
        'address.postcode': {'$exists': True}
    }},
    {'$group': {
        '_id': '$address.postcode',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 5},
    {'$project': {
        '_id': 0,
        'postcode': '$_id',
        'count': 1
    }}
])

print('\nTOP 5 POSTCODES\n')
pp.pprint(list(postcodes))

# Number of users
users = db.budapest.distinct('created.user')
print('\nNUMBER OF CONTRIBUTORS: {}\n'.format(len(users)))

# Top 3 users by occurence
agg = db.budapest.aggregate([
    {'$group': {
        '_id': '$created.user',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 3},
    {'$project': {
        '_id': 0,
        'username': '$_id',
        'count': 1
    }}
])
print('\nTOP 3 USERS:\n')
pp.pprint(list(agg))

# Number of amenities
count = db.budapest.find({'amenity': {'$exists': True}}).count()
print('\nNUMBER OF AMENITIES: {}\n'.format(count))

# Type of amenities by count
amenities = db.budapest.aggregate([
    {'$match': {
        'amenity': {'$exists': True}
    }},
    {'$group': {
        '_id': '$amenity',
        'count': {'$sum': 1}
    }},
    {'$sort': {
        'count': -1
    }},
    {'$limit': 10},
    {'$project': {
        '_id': 0,
        'type': '$_id',
        'count': 1
    }}
])
print('\nAMENITIES BY COUNT:\n')
pp.pprint(list(amenities))

# Top 3 cuisines amongst restaurants
cuisines = db.budapest.aggregate([
    {'$match': {
        'amenity': 'restaurant',
        'cuisine': {'$exists': True}
    }},
    {'$group': {
        '_id': '$cuisine',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 3},
    {'$project': {
        '_id': 0,
        'cuisine': '$_id',
        'count': 1
    }}
])

print('\nTOP 3 RESTAURANT CUISINES:\n')
pp.pprint(list(cuisines))
