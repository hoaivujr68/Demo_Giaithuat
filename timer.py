import time

start_time = 0
total_time = 0


def start_timer():
    global start_time
    start_time = time.time()


def get_timer():
    global total_time
    tmp = round(time.time() - start_time, 5)
    total_time += tmp
    return tmp


def get_total_time():
    global total_time
    return total_time
