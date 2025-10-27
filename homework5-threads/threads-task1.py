from threading import Thread

def cubes() -> dict[str, list[int]]:
    cubes_list = []
    sqr_list = []
    for i in range(1, 11):
        sqr_list.append(i ** 2)
        cubes_list.append(i ** 3)
    res = {"cubes_list": cubes_list, "sqr_list": sqr_list}
    return print(res)

if __name__ == "__main__":

    thread1 = Thread(target=cubes)
    print(f"Расчет из первого потока:")
    thread1.start()

    thread2 = Thread(target=cubes)
    print()
    print(f"Расчет из второго потока:")
    thread2.start()
