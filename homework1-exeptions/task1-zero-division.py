num1 = int(input("Enter a number: "))
num2 = int(input("Enter another number: "))

try:
    result = num1 / num2
    print(result)
except ZeroDivisionError:
    print("Restricted: division by zero")