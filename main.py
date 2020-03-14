from skimage import io, draw
import matplotlib.pyplot as plt
import numpy as np
import os
import math
from radon import *
from bresenham import generate_line


def open_all_images():
    """
    Opens all of the test images as numpy arrays.
    :return: A dictionary in which image names (without extensions) are keys
    """
    img_dir = 'zdjecia'
    images = {}
    for img_name in os.listdir(img_dir):
        images[img_name.split('.')[0]] = io.imread(os.path.join(img_dir, img_name), as_gray=True)
    print('--------------------')
    print('Available images:')
    print(list(images.keys()))
    print('--------------------')
    return images


def display_image(image):
    """
    For now it just displays the image in a standard matplotlib way.
    Later it will replaced with a function displaying an image in the GUI.
    :param image: An image as numpy array
    """
    plt.imshow(image, cmap='gray')
    plt.show()


class Tomograph:
    emitter = 0, 0
    detectors = []
    scan_lines = []
    # This is an offset between the original image and the circle circumscribed on it.
    #  It just makes the visualization look nicer.
    circumcircle_offset = 20
    # This copy will be used to display current emitter/detectors position etc.
    vis_image = None

    # TODO: For now it only works for square images
    def __init__(self, image, delta_alpha, n, l):
        self.current_alpha = 0
        self.delta_alpha = delta_alpha
        self.n = n
        self.l = l

        # Diameter of the circle circumscribed on the image. Emitters and detectors will move alongside its perimeter.
        self.circumcircle_diameter = int(math.sqrt(2 * (image.shape[0] ** 2))) + self.circumcircle_offset
        # Extend the image to fit visualization on it
        self.image = np.pad(image, self.circumcircle_diameter - image.shape[0], mode='constant', constant_values=0)
        self.image_width = self.image.shape[0]
        self.image_center = self.image.shape[0] // 2

        self._scan()

    def next_iteration(self):
        """
        Move to the next scan iteration
        """
        # TODO: Implement this
        self.current_alpha += self.delta_alpha
        self._scan()

    def _scan(self):
        # TODO: Implement or maybe move to different function
        self._calculate_emitter_position()
        self._calculate_detectors_position()
        self._calculate_scan_lines()

    def _calculate_emitter_position(self):
        r = self.circumcircle_diameter // 2
        a = int(self.image_center - r * math.cos(math.radians(self.current_alpha)))
        b = int(self.image_center + r * math.sin(math.radians(self.current_alpha)))
        self.emitter = a, b

    def _calculate_detectors_position(self):
        self.detectors = []
        r = self.circumcircle_diameter // 2
        for i in range(self.n):
            # TODO: Works only for odd number of detectors
            angle = self.current_alpha - (i - self.n / 2) * self.l
            a = int(self.image_center + r * math.cos(math.radians(angle)))
            b = int(self.image_center - r * math.sin(math.radians(angle)))
            self.detectors.append((a, b))

    def _calculate_scan_lines(self):
        self.scan_lines = []
        for a, b in self.detectors:
            self.scan_lines.append(generate_line(self.emitter[0], self.emitter[1], a, b))

    def visualize(self):
        # Make a clean copy of the image
        self.vis_image = self.image.copy()
        self._visualize_circumcircle()
        self._visualize_emitter_detector(self.emitter)
        for detector in self.detectors:
            self._visualize_emitter_detector(detector)
        self._visualize_scan_lines()
        display_image(self.vis_image)

    def _visualize_circumcircle(self):
        rr, cc = draw.circle_perimeter(r=self.image_center, c=self.image_center,
                                       radius=int(self.circumcircle_diameter / 2))
        self.vis_image[rr, cc] = 1

    def _visualize_emitter_detector(self, coords):
        rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
        self.vis_image[rr, cc] = 1

    def _visualize_scan_lines(self):
        for line in self.scan_lines:
            for a, b in line:
                self.vis_image[a][b] = 1


def main():
    images = open_all_images()
    image = images['Shepp_logan']

    tomograph = Tomograph(image, delta_alpha=30, n=10, l=10)
    tomograph.visualize()

    for i in range(10):
        tomograph.next_iteration()
        tomograph.visualize()


if __name__ == '__main__':
    main()
