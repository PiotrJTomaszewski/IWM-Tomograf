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
    emitters = []
    detectors = []
    scan_lines = []
    # This is an offset between the original image and the circle circumscribed on it.
    #  It just makes the visualization look nicer.
    circumcircle_offset = 0
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
        self.image_center = (self.image.shape[0] // 2, self.image.shape[1] // 2)

        self.radon_image = np.zeros((n, 211), dtype="uint8")
        self.radon_result = np.zeros((n, 211), dtype=np.int)
        self._scan()

    def next_iteration(self):
        """
        Move to the next scan iteration
        """
        # TODO: Implement this
        self.current_alpha += self.delta_alpha
        self._scan()
        self.radon_transform()

    def _scan(self):
        # TODO: Implement or maybe move to different function
        self._calculate_emitter_position()
        self._calculate_detectors_position()
        self._calculate_scan_lines()

    def _calculate_emitter_position(self):
        # r = self.circumcircle_diameter // 2
        # a = int(self.image_center[0] - r * math.cos(math.radians(self.current_alpha)))
        # b = int(self.image_center[1] + r * math.sin(math.radians(self.current_alpha)))
        # self.emitter = a, b

        self.emitters = []
        r = self.circumcircle_diameter // 2
        for i in range(self.n):
            # TODO: Works only for odd number of detectors
            angle = self.current_alpha - (i - self.n / 2) * self.l + 180
            a = int(self.image_center[0] + r * math.cos(math.radians(angle)))
            b = int(self.image_center[1] - r * math.sin(math.radians(angle)))
            self.emitters.append((a, b))
        self.emitters.reverse()

    def _calculate_detectors_position(self):
        self.detectors = []
        r = self.circumcircle_diameter // 2
        for i in range(self.n):
            # TODO: Works only for odd number of detectors
            angle = self.current_alpha - (i - self.n / 2) * self.l
            a = int(self.image_center[0] + r * math.cos(math.radians(angle)))
            b = int(self.image_center[1] - r * math.sin(math.radians(angle)))
            self.detectors.append((a, b))

    def _calculate_scan_lines(self):
        self.scan_lines = []
        for i in range(len(self.emitters)):
            self.scan_lines.append(
                generate_line(self.emitters[i][0], self.emitters[i][1], self.detectors[i][0], self.detectors[i][1]))

    def radon_transform(self):
        """Inspired by https://www.clear.rice.edu/elec431/projects96/DSP/bpanalysis.html
        Theta is called alpha in this code"""
        iteration_result = []
        for i, line in enumerate(self.scan_lines):
            s = distance_point_line(self.image_center, line[0], line[-1])
            line_integral = sum([self.image[point[0]][point[1]] for point in line])
            self.radon_result[int(i), self.current_alpha] += line_integral

    def visualize(self):
        # Make a clean copy of the image
        self.vis_image = self.image.copy()
        self._visualize_circumcircle()
        for emitter in self.emitters:
            self._visualize_emitter_detector(emitter)
        for detector in self.detectors:
            self._visualize_emitter_detector(detector)
        self._visualize_scan_lines()
        display_image(self.vis_image)

    def _visualize_circumcircle(self):
        rr, cc = draw.circle_perimeter(r=self.image_center[0], c=self.image_center[1],
                                       radius=int(self.circumcircle_diameter / 2))
        self.vis_image[rr, cc] = 1

    def _visualize_emitter_detector(self, coords):
        rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
        self.vis_image[rr, cc] = 1

    def _visualize_scan_lines(self):
        for line in self.scan_lines:
            for a, b in line:
                self.vis_image[a][b] = 1

    def _visualize_radon(self):
        max_val = np.max(self.radon_result)
        min_val = np.min(self.radon_result)
        for i in range(len(self.radon_result)):
            for j in range(len(self.radon_result[i])):
                self.radon_image[i][j] = normalize(self.radon_result[i][j], min_val, max_val)
        display_image(self.radon_image)


def distance_point_line(point, line_point1, line_point2):
    """
    Calculates distance between a point and a line defined by two points
    """
    x0 = point[1]
    y0 = point[0]
    x1 = line_point1[1]
    y1 = line_point1[0]
    x2 = line_point2[1]
    y2 = line_point2[0]
    return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def normalize(value, min_val, max_val):
    return int((value - min_val) / (max_val - min_val) * 255)


def main():
    images = open_all_images()
    image = images['Shepp_logan']

    tomograph = Tomograph(image, delta_alpha=1, n=200, l=1)
    tomograph.visualize()

    for i in range(180):
        tomograph.next_iteration()
        # tomograph.visualize()

    tomograph._visualize_radon()
    display_image(cheat_radon(image))


if __name__ == '__main__':
    main()
