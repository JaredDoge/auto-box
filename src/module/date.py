from datetime import datetime


def log_time():
    return datetime.now().strftime("%H:%M:%S")


def file_time():
    return datetime.now().strftime("%H_%M_%S")
