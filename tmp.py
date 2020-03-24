from main import open_all_images
from radon import cheat_radon
import numpy as np
import math
from skimage import io
import matplotlib.pyplot as plt
from ct_scanner import Tomograph
import pprint


# radon_result = cheat_radon(images['Paski2'])
# radon_result = cheat_radon(images['CT_ScoutView'])


def filter(sinogram):
    result = sinogram.copy()
    filter = [0 for i in range(result.shape[1])]
    cutoff = 10
    a = np.linspace(start=0, stop=1, num=result.shape[1] // 2 - cutoff)
    for i in range(cutoff, result.shape[1] // 2):
        filter[i] = a[-(i - cutoff)]
        filter[result.shape[1] // 2 + i - cutoff] = a[i - cutoff]

    for i, line in enumerate(sinogram):
        sinogram_fft = np.fft.fft(line)
        filtered_line = sinogram_fft * filter
        filtered_line = np.fft.ifft(filtered_line)
        # plt.plot(sinogram_fft)
        # plt.show()
        # plt.plot(filtered_line)
        # plt.show()
        # if i >= 0:
        #     break
        result[i] = filtered_line
    return result


# def filtered_back_projection(sinogram):
#     result = np.zeros((1500, 1500), dtype=np.int)
#     for phi in range(0, 100, 10):
#         for x, line in enumerate(result):
#             for y, point in enumerate(line):
#                 s = 500 + x * math.sin(math.radians(phi)) - y * math.cos(math.radians(phi))
#                 s = int(s)
#                 # s = abs(s)
#                 if s < sinogram.shape[1] and s >=0:
#                     result[x, y] += sinogram[phi, s]
#             # plt.plot(line)
#             # plt.show()
#             # if i >= 0:
#             #     break
#     return result


# def filtered_back_projection(sinogram):
#     # np.zeros((1000, 1000), dtype=np.uint8)
#     result = np.zeros((1500, 1500), dtype=np.int)
#     # projections = singogram.transponse()
#     a = np.linspace(start=-1, stop=3.14, num=100)
#     for phi in a:
#         for y, line in enumerate(sinogram):
#             for x in range(len(line)):
#                 for phi in a:
#                     g = int(y* math.cos(phi))
#                     h = int(x*math.sin(phi))
#                     result[x+200, y+200] = sum(sinogram[int(y * math.cos(phi)), int(x * math.sin(phi))] for phi in a)
#
#     return result


# def filtered_back_projection(sinogram):
#     n = sinogram.shape[0]
#     m = sinogram.shape[1]
#     sinogram = np.transpose(sinogram)
#     print(n, m)
#     fuckups = 0
#     result = np.zeros((400, 400), dtype=np.int)
#     eses = []
#
#     angles = [0, 45, 90]
#     # for angle, line in enumerate(sinogram):
#     for angle in angles:
#         line = sinogram[angle]
#         plt.plot(line)
#         plt.show()
#         for y in range(len(result)):
#             for x in range(len(result[y])):
#                 angle_rad = math.radians(angle)
#                 s = y * math.sin(angle_rad) + x * math.cos(angle_rad)
#                 s = y * math.cos(angle_rad) - x * math.sin(angle_rad)
#                 s = int(s)
#                 # s = abs(s)
#                 eses.append(s)
#                 try:
#                     result[y, x] += line[s]
#                 except IndexError:
#                     fuckups += 1
#
#     print('No. fuckups: ', fuckups)
#     print('Eses_min: ', min(eses))
#     print('Eses max: ', max(eses))
#     # result[100, 100] = 290
#     return result


def filtered_back_projection(sinogram):
    n = sinogram.shape[0]
    m = sinogram.shape[1]
    n,m = m,n

    print(n, m)
    fuckups = 0
    result = np.zeros((n, n), dtype=np.int)
    eses = []

    angles = range(0, m, 10)
    # for angle, line in enumerate(sinogram):
    for angle in angles:
    # for angle in angles:
        line = sinogram[angle]
        eses.append([])
        # plt.plot(line)
        # plt.show()
        for y in range(len(result)):
            for x in range(len(result[y])):
                angle_rad = math.radians(angle)
                s = y * math.cos(angle_rad) - x * math.sin(angle_rad)
                # s = abs(s)
                eses[-1].append(s)
    print('start normalizing')
    eses_norm = []
    for i, ss in enumerate(eses):
        min_s = min(ss)
        max_s = max(ss)
        print(min_s, max_s)
        norm = [int(((s - min_s) / (max_s - min_s)) * n) for s in ss]
        eses_norm.append(norm)

    print('normalized')
    for i, angle in enumerate(angles):
        line = sinogram[angle]
        j = 0
        for y in range(len(result)):
            for x in range(len(result[y])):
                s = eses_norm[i][j]
                j += 1
                try:
                    result[x, y] += line[s]
                except IndexError:
                    fuckups += 1
    print('No. fuckups: ', fuckups)
    # result[100, 100] = 290
    return result


# radon_result = np.zeros((10, 5), np.int)
# filtered = filter(radon_result)
# r = filter(filtered)

# print(np.packbits(radon_result))

#
images = open_all_images()
# tomograph = Tomograph(images['Shepp_logan'], delta_alpha=1, n=37, l=2.9)
# tomograph.radon_transform()
# radon_result = tomograph.visualize_sinogram()

radon_result = cheat_radon(images['Shepp_logan'])
radon_result = np.transpose(radon_result)

io.imshow(radon_result)
io.show()

# radon_result = cheat_radon(images['Shepp_logan'])

# radon_result = np.transpose(radon_result)

# radon_result = io.imread('Kropka_radon.png', as_gray=True)


# io.imshow(radon_result)
# io.show()
# io.imsave('Kropka_radon.png', radon_result)
# radon_result = filter(radon_result)
print('filtered')

r = filtered_back_projection(radon_result)
io.imshow(r)
io.show()
# a = np.zeros((10, 5))
# a[3, 2] = 1
# a[0, 3] = 1
# print(a)
# a = a.transpose()
# print(a)
