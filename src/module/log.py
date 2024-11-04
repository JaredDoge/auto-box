from datetime import datetime


def log_time():
    return datetime.now().strftime("%H:%M:%S")


def log(content):
    print(f'[~]{log_time()} {content}')


def single(content):
    print(f'[~]{log_time()} {content}')
