# import requests
#
# geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
#
#
# def search_adress(address):
#     user_request = address
#     geocoder_params = {
#         "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
#         "geocode": user_request,
#         "format": "json"}
#     response = requests.get(geocoder_api_server, params=geocoder_params)
#     if not response:
#         raise ConnectionError  # вывести ошибку пдключения
#     json_response = response.json()
#     try:
#         toponym = json_response["response"]["GeoObjectCollection"][
#             "featureMember"][0]["GeoObject"]
#         toponym_coodrinates = toponym["Point"]["pos"]
#         toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
#         return toponym_longitude, toponym_lattitude
#     except IndexError:
#         raise FileNotFoundError  # вывести ошибку ненахождения объекта
#
#
# print(search_adress('askldjksd'))
print([1,2,3][1:])