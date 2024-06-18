import numpy as np
from matplotlib import pyplot as plt


def height(x):
    return (1 / 2) * (9.8 * (x ** 2))

print('第', 6, '秒球位置', height(6))
x = np.arange(0, 10, 0.01)
plt.plot(x, height(x))
plt.grid(True)
plt.show()
