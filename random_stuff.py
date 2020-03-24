from timeit import default_timer as timer
from main import open_all_images
from skimage import io
import numpy as np
import ct_scanner
import tomograph_cythonized
import inverse_radon
import inverse_radon_cythonized


# import inverse_radon_cythonized


def time_tomograph():
    images = open_all_images()
    image = images['Shepp_logan']

    start = timer()
    t1 = ct_scanner.Tomograph(image, delta_alpha=2.1, n=81, l=75)
    end = timer()
    print('Normal init: ', end - start)

    start = timer()
    t2 = tomograph_cythonized.Tomograph(image, delta_alpha=2.1, n=81, l=75)
    end = timer()
    print('Cythonized init: ', end - start)

    start = timer()
    t1.radon_transform_full()
    end = timer()
    print('Normal transform:', end - start)

    start = timer()
    t2.radon_transform_full()
    end = timer()
    print('Cythonized transform:', end - start)

    start = timer()
    io.imshow(t1.visualize_sinogram())
    end = timer()
    print('Normal visualization:', end - start)
    io.show()

    start = timer()
    io.imshow(t2.visualize_sinogram())
    end = timer()
    print('Cythonized visualization:', end - start)
    io.show()


def time_inverse_radon():
    images = open_all_images()
    # tomograph = Tomograph(images['Shepp_logan'], delta_alpha=1, n=37, l=2.9)
    # tomograph.radon_transform()
    # radon_result = tomograph.visualize_sinogram()
    from radon import cheat_radon
    radon_result = cheat_radon(images['Shepp_logan'])
    radon_result = np.transpose(radon_result)

    start = timer()
    i1 = inverse_radon.filtered_back_projection(radon_result)
    end = timer()
    print('Normal backprojection: ', end - start)

    start = timer()
    i2 = inverse_radon_cythonized.filtered_back_projection(radon_result)
    end = timer()
    print('Cythonized backprojection: ', end - start)

    io.imshow(i1)
    io.show()
    io.imshow(i2)
    io.show()


time_inverse_radon()
