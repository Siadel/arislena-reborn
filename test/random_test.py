from numpy import random

for i in range(10):
    print(
        random.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4], p=[0.04, 0.07, 0.12, 0.17, 0.20, 0.17, 0.12, 0.07, 0.04])
    )
