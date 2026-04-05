def addition(x,y):
    print("<>addition")
    return x + y


def subtraction(x,y):
    print("->subtraction")
    print("<-subtraction")
    return x - y


def func(x,y, fc):
    return fc(x,y)


print(func(3,2, addition))
print(func(4,2, subtraction))