class A():
    def __init__(self):
        print("created")
    def __del__(self):
        print ("deleted!")

import time
a = {'a': A()}
a['a'] = 1
print 'sleeping...'
time.sleep(1)
print 'sleep done'

