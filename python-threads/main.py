from time import sleep
from threading import Thread
from random import random


def main():
    print('running main', flush=True)
    for _ in range(0, 128):
        thread = Thread(target=do_nothing)
        thread.start()
        sleep(0.1)  # small sleep to avoid thread creation errors
    i = 0
    while True:
        print(f'sleeping since {i} seconds', flush=True)
        sleep(1)
        i += 1


def do_nothing():
    while True:
        sleep(1)
        i = random()
        i = i + random()
        # print(i)


if __name__ == '__main__':
    main()
