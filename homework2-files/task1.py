
with open("files/source.txt") as file_source:
    lines = file_source.readlines()
    with open("files/destination.txt", "w") as file_destination:
        for line in lines:
            file_destination.write(line)