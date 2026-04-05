def myfunc(*args, **kwargs):

    for arg in args:
        print(arg)

    for key, val in kwargs.items():
        print(key, val)


myfunc(5,6,7,4,"Derk", [3,4,5], name = "Luke")