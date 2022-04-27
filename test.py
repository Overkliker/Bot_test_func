import datetime

delta = datetime.timedelta(days=23,
                           seconds=2,
                           microseconds=0,
                           milliseconds=0,
                           minutes=0,
                           hours=0,)

print(delta)
print(datetime.datetime.now())
print(datetime.datetime.now() - delta)