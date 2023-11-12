import pymongo

# Create an instance of the MongoDB client
client = pymongo.MongoClient('localhost', 27017)

db = client['ozp_bot']
users = db['users']
works = db['works']
docs = db['documents']
buffer = db['buffer']

'''
структура данных users
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'first_name': имя пользователя,
    'last_name': фамилия пользователя,
    'full_name': имя и фамилия пользователя
    'username':  логин пользователя
    'department': место работы
    'is_admin': по умолчанию false
'''
