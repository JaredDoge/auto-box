from src.module import date


def log(content):
    print(f'\n[~]{date.log_time()} {content}')


def single(content):
    print(f'[~]{date.log_time()} {content}')
