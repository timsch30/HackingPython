import time


def decorate_print(func):
    def inner(*args, **kwargs):
        print(f"->decorate_print")
        val = func(*args, **kwargs)
        print(f"<-decorate_print")
        return val

    return inner


def decorate_time(func):
    def inner(*args, **kwargs):
        print(f"->decorate_time")
        start = time.time()
        val = func(*args, **kwargs)
        end = time.time()
        print(f"<-decorate_time {end - start}")
        return val

    return inner


@decorate_print
@decorate_time
def addition(x,y):
    print("<>addition")
    return x + y


@decorate_print
@decorate_time
def subtraction(x,y):
    print("<>subtraction")
    return x - y


print(addition(3,3))
print(subtraction(4,3))
