from skimage import io, draw
import numpy as np
import math
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
    max_alpha = 180

    current_iradon_iteration = 0
    iradon_result = None
    iradon_tmp_eses = None

    # TODO: For now it only works for square images
    def __init__(self, image, delta_alpha, n, l):
        # Alpha is in degrees
        self.current_alpha = 0
        self.delta_alpha = delta_alpha
        self.n = n
        self.l = l
        # TODO: Find which angle works best
        self.radon_iterations = int(self.max_alpha // delta_alpha)

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
        cdef int radon_iterations = self.radon_iterations
        cdef int current_radon_iteration = self.current_radon_iteration
        cdef int n = self.n
        cpdef double line_integral
        cdef int delta_alpha = self.delta_alpha
        cdef int line_id
        if current_radon_iteration < radon_iterations:
            self._calculate_emitters_detectors_position()
            self._calculate_scan_lines()
            line_id = 0
            for line_id in range(n):
                line_integral = np.sum([self.image[point] for point in self.scan_lines[line_id]])
                self.radon_result[line_id, self.current_radon_iteration] += line_integral
            self.current_alpha += delta_alpha
            self.current_radon_iteration += 1
            return True
        else:
            return False

    def radon_transform_full(self):
        while self.radon_transform_step():
            pass

    def _calculate_emitters_detectors_position(self):
        self.emitters = []
        self.detectors = []
        cdef int r
        cdef int current_alpha = self.current_alpha
        cdef double l = self.l
        cdef int n = self.n
        cdef int image_center_a = self.image_center[0]
        cdef int image_center_b = self.image_center[1]
        r = self.circumcircle_diameter // 2
        # TODO: Look at this division
        angles = np.linspace(start=current_alpha - l / 2, stop=current_alpha + l / 2, num=n)
        cdef double x
        angles_rad = [math.radians(x) for x in angles]
        cdef int i
        for i in range(n):
            # TODO: Should emitters be on top or bottom?
            # angle_rad = math.radians(self.current_alpha + (i - self.n // 2) * self.l)
            angle_rad = angles_rad[i]
            emitter_a = int(image_center_a + r * math.cos(angle_rad))
            emitter_b = int(image_center_b - r * math.sin(angle_rad))
            self.emitters.append((emitter_a, emitter_b))
        for i in range(n - 1, -1, -1):
            # angle_rad = math.radians(self.current_alpha + (i - self.n // 2) * self.l)
            angle_rad = angles_rad[i]
            detector_a = int(image_center_a - r * math.cos(angle_rad))
            detector_b = int(image_center_b + r * math.sin(angle_rad))
            self.detectors.append((detector_a, detector_b))

    def _calculate_scan_lines(self):
        self.scan_lines = []
        cdef int i
        cdef int n = self.n
        for i in range(n):
            self.scan_lines.append(
                generate_line(self.emitters[i][0], self.emitters[i][1], self.detectors[i][0], self.detectors[i][1]))

    def iradon_init(self):
        self.current_iradon_iteration = 0
        self.iradon_result = np.zeros((self.n, self.n), dtype=np.int)
        self.iradon_tmp_eses = np.zeros(self.n * self.n, dtype=np.double)
        self.radon_result = np.transpose(self.radon_result)

    def iradon_step(self):
        cdef int n = self.n
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
        angle = self.current_iradon_iteration

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
                self.iradon_tmp_eses[i] = s
                i += 1
        j = 0
        for y in range(n):
            for x in range(n):
                self.iradon_result[x, y] += self.radon_result[
                   angle, int(((self.iradon_tmp_eses[j] - min_s) / (max_s - min_s) * (n - 1)))]
                j += 1
        if self.current_iradon_iteration == self.radon_iterations:
            return True
        else:
            self.current_iradon_iteration += 1
            return False

    def iradon_full(self):
        while self.iradon_step():
            pass

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
        singoram_image = np.zeros((self.radon_result.shape[0], self.radon_result.shape[1]), dtype=np.uint8)
        max_val = np.max(self.radon_result)
        min_val = np.min(self.radon_result)
        for i in range(len(self.radon_result)):
            for j in range(len(self.radon_result[i])):
                singoram_image[i, j] = normalize(self.radon_result[i, j], min_val, max_val)
        return singoram_image

    def visualize_reconstructed_img(self):
        rec_img = np.zeros((self.iradon_result.shape[0], self.iradon_result.shape[1]), dtype=np.uint8)
        max_val = np.max(self.iradon_result)
        min_val = np.min(self.iradon_result)
        for i in range(len(self.iradon_result)):
            for j in range(len(self.iradon_result[i])):
                rec_img[i, j] = normalize(self.iradon_result[i, j], min_val, max_val)
        return rec_img


def normalize(value, min_val, max_val):
    return int((value - min_val) / (max_val - min_val) * 255)

def main():
    from timeit import default_timer as timer
    from main import open_all_images
    images = open_all_images()
    image = images['Shepp_logan']

    start = timer()
    tomograph = Tomograph(image, delta_alpha=2.1, n=81, l=75)
    tomograph.radon_transform_full()
    end = timer()
    print(end - start)

    io.imshow(tomograph.visualize_sinogram())
    io.show()

if __name__ == '__main__':
    main()
