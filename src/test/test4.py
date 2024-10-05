import sys
import traceback


def func1(num1, num2):
        x = num1 * num2
        y = num1 / num2
        return x, y
def func2():
    func1(1, 0)


if __name__ == '__main__':
    try:
        func2()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
