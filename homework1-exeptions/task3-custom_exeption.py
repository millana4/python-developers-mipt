num_list = [1, 3, -5, 7, 9]

class NegativeNumberExeption(Exception):
    pass

class EvenNumberExeption(Exception):
    pass

sum = 0
for num in num_list:
    if num % 2 == 0:
        raise EvenNumberExeption("Invalid input: used even number")
    elif num < 0:
        raise NegativeNumberExeption("Invalid input: used negative number")
    else:
        sum += num

print(sum)





