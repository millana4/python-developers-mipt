
with open("files/input.txt", encoding="utf-8") as file_input:
    lines = file_input.readlines()
    unique_set = set ()
    for line in lines:
        unique_set.add(line)
    with open("files/unique_output.txt", "w", encoding="utf-8") as file_destination:
        for line in unique_set:
            file_destination.write(line)
