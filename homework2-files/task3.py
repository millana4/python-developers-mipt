
quantity = 0

with open("files/text_file.txt", encoding="utf-8") as file:
    lines = file.readlines()
    for line in lines:
        line = line.split()
        for item in line:
            if item != "—":
                quantity += 1

print(quantity)