import math

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


