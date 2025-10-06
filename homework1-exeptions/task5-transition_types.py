num = input("Enter a number: ")

try:
    num1 = float(num)
    print(num1)
except ValueError:
    print("Value is not a number")