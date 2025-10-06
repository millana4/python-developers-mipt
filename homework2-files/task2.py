
sum = 0

with open("files/prices.txt") as file:
    lines = file.readlines()
    for line in lines:
        line = line.split()
        sum += float(line[2])

print(sum)
