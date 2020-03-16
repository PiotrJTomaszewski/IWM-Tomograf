from skimage import io, draw
import matplotlib.pyplot as plt
import numpy as np
import os
import math
from radon import *
from bresenham import generate_line


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
        # Alpha is in degrees
        self.current_alpha = 0
        self.delta_alpha = delta_alpha
        self.n = n
        self.l = l
        # TODO: Find which angle works best
        self.radon_iterations = int(180 // delta_alpha)

        # Diameter of the circle circumscribed on the image. Emitters and detectors will move alongside its perimeter.
        self.circumcircle_diameter = int(math.sqrt(2 * (image.shape[0] ** 2))) + self.circumcircle_offset
        # Extend the image to fit visualization on it
        self.image = np.pad(image, self.circumcircle_diameter - image.shape[0], mode='constant', constant_values=0)
        self.image_width = self.image.shape[0]
        self.image_center = (self.image.shape[0] // 2, self.image.shape[1] // 2)
        self.radon_result = np.zeros((self.n, self.radon_iterations), dtype=np.int)
        self.current_radon_iteration = 0

    def radon_transform_step(self):
        """
        Calculate the next step of Radom transform
        :return: False if the transform is done, true if there are still steps available
        """
        """Inspired by https://www.clear.rice.edu/elec431/projects96/DSP/bpanalysis.html
        Theta is called alpha in this code"""
        # TODO: Calculate s
        if self.current_radon_iteration < self.radon_iterations:
            self._calculate_emitters_detectors_position()
            self._calculate_scan_lines()
            for line_id, line in enumerate(self.scan_lines):
                line_integral = sum([self.image[point[0]][point[1]] for point in line])
                self.radon_result[line_id, self.current_radon_iteration] += line_integral
            self.current_alpha += self.delta_alpha
            self.current_radon_iteration += 1
            return True
        else:
            return False

    def radon_transform(self):
        while self.radon_transform_step():
            pass

    def _calculate_emitters_detectors_position(self):
        self.emitters = []
        self.detectors = []
        r = self.circumcircle_diameter // 2
        for i in range(self.n):
            # TODO: Angle calculation works ok only for odd number of detectors/emitters
            # TODO: Should emitters be on top or bottom?
            angle_rad = math.radians(self.current_alpha + (i - self.n // 2) * self.l)
            emitter_a = int(self.image_center[0] + r * math.cos(angle_rad))
            emitter_b = int(self.image_center[1] - r * math.sin(angle_rad))
            self.emitters.append((emitter_a, emitter_b))
        for i in range(self.n - 1, -1, -1):
            angle_rad = math.radians(self.current_alpha + (i - self.n // 2) * self.l)
            detector_a = int(self.image_center[0] - r * math.cos(angle_rad))
            detector_b = int(self.image_center[1] + r * math.sin(angle_rad))
            self.detectors.append((detector_a, detector_b))

    def _calculate_scan_lines(self):
        self.scan_lines = []
        for i in range(len(self.emitters)):
            self.scan_lines.append(
                generate_line(self.emitters[i][0], self.emitters[i][1], self.detectors[i][0], self.detectors[i][1]))

    def visualize_scanner(self):
        # Make a clean copy of the image
        self.vis_image = self.image.copy()
        self._calculate_emitters_detectors_position()
        self._calculate_scan_lines()
        self._visualize_circumcircle()
        for emitter in self.emitters:
            self._visualize_emitter(emitter)
        for detector in self.detectors:
            self._visualize_detector(detector)
        self._visualize_scan_lines()
        return self.vis_image

    def _visualize_circumcircle(self):
        rr, cc = draw.circle_perimeter(r=self.image_center[0], c=self.image_center[1],
                                       radius=int(self.circumcircle_diameter / 2))
        self.vis_image[rr, cc] = 1

    def _visualize_emitter(self, coords):
        rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
        self.vis_image[rr, cc] = 1

    def _visualize_detector(self, coords):
        rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
        self.vis_image[rr, cc] = 0.5

    def _visualize_scan_lines(self):
        for line in self.scan_lines:
            for a, b in line:
                self.vis_image[a][b] = 1

    def visualize_sinogram(self):
        singoram_image = self.radon_result.astype(np.uint8)
        max_val = np.max(self.radon_result)
        min_val = np.min(self.radon_result)
        for i in range(len(self.radon_result)):
            for j in range(len(self.radon_result[i])):
                singoram_image[i][j] = normalize(self.radon_result[i][j], min_val, max_val)
        return singoram_image


def normalize(value, min_val, max_val):
    return int((value - min_val) / (max_val - min_val) * 255)

# def main():
#     images = open_all_images()
#     image = images['Shepp_logan']
#
#     tomograph = Tomograph(image, delta_alpha=10, number_of_iterations=180, n=81, l=1)
#     tomograph.visualize_scanner()
#     tomograph.radon_transform()
#     tomograph.visualize_radon()
#
#     display_image(cheat_radon(image))
#
#
# if __name__ == '__main__':
#     main()
