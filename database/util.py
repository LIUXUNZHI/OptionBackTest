import datetime

def calc_month(a,b):
    x = (a + b) % 12
    if x:
        return x
    else:
        return 12

def str2datetime(date):
    return