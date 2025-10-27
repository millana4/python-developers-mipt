import time
from threading import Thread

def sleeping_nums() -> None:
    for i in range(1, 11):
        print(i)
        time.sleep(1)
    return None

if __name__ == "__main__":
    t1 = Thread(target=sleeping_nums)
    t2 = Thread(target=sleeping_nums)
    t3 = Thread(target=sleeping_nums)
    t4 = Thread(target=sleeping_nums)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()