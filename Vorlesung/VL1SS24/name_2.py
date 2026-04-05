import name_1

print(f"this is name_2: {__name__}, {name_1.__name__}")

if __name__ == "__main__":
    print(f"this is: {__name__}")
    print(f"the other is: {name_1.__name__}")

