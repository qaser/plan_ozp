import pymongo


client = pymongo.MongoClient('localhost', 27017)
db = client['ozp_bot']
users = db['users']
works = db['works']
buffer = db['buffer']

'''
структура данных users
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'first_name': имя пользователя,
    'last_name': фамилия пользователя,
    'full_name': имя и фамилия пользователя
    'username':  логин пользователя
    'department': место работы (опционально)
    'is_admin': по умолчанию false
'''
