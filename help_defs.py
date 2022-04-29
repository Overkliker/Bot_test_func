import math
import requests

########### Проверка на float, для записи в БД ################

def is_float(string):
    try:
        float(string)
        return True

    except ValueError:
        return False


########## Нахождение ближайших координат ####################
EARTH_RADIUS = 6371210
DISTANCE = 3000

#https://en.wikipedia.org/wiki/Longitude#Length_of_a_degree_of_longitude
def compute_delta(degrees):
    return math.pi / 180 * EARTH_RADIUS * math.cos(deg2(degrees))

def deg2(deg):
    return deg * math.pi / 180


def around(cord):
    return DISTANCE / cord #Вычисляем диапазон координате


############### Нахождение широты и долготы по адресу ##########

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"


def search_adress(address):
    user_request = address
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": user_request,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        raise ConnectionError  # вывести ошибку пдключения
    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        return toponym_lattitude, toponym_longitude
    except IndexError:
        raise FileNotFoundError  # вывести ошибку ненахождения объекта


################### FOR POINTS ON MAP ###############

map_api_server = "http://static-maps.yandex.ru/1.x/"
