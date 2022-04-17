########### Проверка на float, для записи в БД ################

def is_float(string):
    try:
        float(string)
        return True

    except ValueError:
        return False


print(is_float('39.2423'))