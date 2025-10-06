search_list = [1, 3, 1, 5, 8, 88]

needed_index = int(input("Enter the index of the item you wish to search: "))

try:
    print(search_list[needed_index])
except IndexError:
    print("Index out of range")

