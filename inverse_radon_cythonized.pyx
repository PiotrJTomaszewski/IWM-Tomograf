import numpy as np
import math


cpdef filtered_back_projection(sinogram):
    cdef int n = sinogram.shape[0]
    cdef int m = sinogram.shape[1]
    n, m = m, n

    result = np.zeros((n, n), dtype=np.int)
    angles = range(0, m, 10)

    eses = np.zeros(n*n, dtype=np.double)
    # for angle, line in enumerate(sinogram):
    cdef int y
    cdef int x
    cdef double angle_rad
    cdef int i
    cdef double min_s
    cdef double max_s
    cdef double s
    cdef int j
    cdef int angle
    cdef double cos_angle
    cdef double sin_angle
    for angle in angles:
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        i = 0
        min_s = 1e9
        max_s = 0
        for y in range(n):
            for x in range(n):
                s = y * cos_angle - x * sin_angle
                if s < min_s:
                    min_s = s
                elif s > max_s:
                    max_s = s
                eses[i] = s
                i += 1
        j = 0
        for y in range(n):
            for x in range(n):
                # try:
                result[x, y] += sinogram[angle, int(((eses[j] - min_s) / (max_s - min_s) * (n-1)))]
                j += 1
                # except IndexError:
                #     pass
    return result
