import numpy as np
import math


def filtered_back_projection(sinogram):
    n = sinogram.shape[0]
    m = sinogram.shape[1]
    n, m = m, n

    result = np.zeros((n, n), dtype=np.int)
    angles = range(0, m, 10)

    eses = np.zeros(n*n, dtype=np.double)
    # for angle, line in enumerate(sinogram):
    for angle in angles:
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        # plt.plot(line)
        # plt.show()
        i = 0
        for y in range(n):
            for x in range(n):
                eses[i] = y * cos_angle - x * sin_angle
                i += 1

        min_s = math.ceil(np.min(eses))
        max_s = math.floor(np.max(eses))
        j = 0
        for y in range(n):
            for x in range(n):
                s = int(((eses[j] - min_s) / (max_s - min_s) * (n-1)))
                j += 1
                # try:
                result[x, y] += sinogram[angle, s]
                # except IndexError:
                #     pass
    # result[100, 100] = 290
    return result
