try:
    import math
except ModuleNotFoundError:
    print("Невозможно импортировать math")

num = int(input("Enter a number: "))


if num >= 0:
    num_sqrt = math.sqrt(num)
    print(num_sqrt)
else:
    raise ValueError("Number must be positive")


