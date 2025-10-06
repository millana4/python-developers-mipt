num1 = input("Enter a number: ")
num2 = input("Enter another number: ")

try:
    num1 = int(num1)
    num2 = int(num2)
    try:
        result = num1 / num2
        print(result)
    except ZeroDivisionError:
        print("Restricted: division by zero")
except ValueError:
    print("Invalid input")

