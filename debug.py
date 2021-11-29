
import time

foo = '2021-10-18T11:31:39'


foo = '2021-11-29T03:27'


print(int(time.mktime(time.strptime(foo, '%Y-%m-%dT%H:%M:%S.%f')) * 1000))