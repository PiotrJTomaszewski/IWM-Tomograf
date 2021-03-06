from skimage import draw
import numpy as np
import math
from bresenham import generate_line


class CTScanner:
    input_image = None
    input_image_width = 0
    input_image_center = 0
    scanner_vis_img_padding = 0
    circumcircle_diameter = 0
    # Radon transform
    radon_result = None
    current_radon_iteration = 0
    radon_total_iter_no = 0
    delta_alpha = 10
    current_alpha = 0
    max_alpha = 180
    # Scanner
    scan_lines = []
    vis_scan_lines = []  # Scan lines used in visualization (they are just longer)
    em_det_no = 0
    em_det_spread = 0
    # Inverse Radon
    current_iradon_iteration = 0
    iradon_result = None
    iradon_scaling_factor = 0
    rec_img_dirty = True  # True if the reconstructed img needs to be recalculated (used when saving the image)
    rec_img = None
    is_scanner_dirty = True
    current_emitters = []
    current_detectors = []
    current_scan_lines = []

    def __init__(self, radon_step_progress_clbk, radon_total_progress_clbk, iradon_step_progress_clbk,
                 iradon_total_progress_clbk, normalization_radon_progress_clbk, normalization_iradon_progress_clbk):
        self.radon_step_progress_clbk = radon_step_progress_clbk
        self.radon_total_progress_clbk = radon_total_progress_clbk
        self.iradon_step_progress_clbk = iradon_step_progress_clbk
        self.iradon_total_progress_clbk = iradon_total_progress_clbk
        self.normalization_radon_progress_clbk = normalization_radon_progress_clbk
        self.normalization_iradon_progress_clbk = normalization_iradon_progress_clbk

    def set_input_image(self, image):
        if image.dtype == np.float64:
            image = (image * 255).astype(np.uint8)
        self.input_image = make_image_square(image)
        self.circumcircle_diameter = int(self.input_image.shape[0] * math.sqrt(2))
        self.scanner_vis_img_padding = (self.circumcircle_diameter - self.input_image.shape[0]) // 2 + 10
        # We're making the input image larger both to fit the visualizations and to make calculating lines easier
        self.input_image = np.pad(self.input_image, self.scanner_vis_img_padding, mode='constant',
                                  constant_values=0)
        self.input_image_width = self.input_image.shape[0]
        self.input_image_center = self.input_image_width // 2

    def set_params(self, delta_alpha, n, l):
        self.delta_alpha = delta_alpha
        self.em_det_no = n
        self.em_det_spread = l
        self.is_scanner_dirty = True

    def init_radon(self):
        self.scan_lines = []
        self.current_alpha = 0
        self.radon_total_iter_no = math.floor(self.max_alpha / self.delta_alpha)
        self.current_radon_iteration = 0
        self.radon_result = np.zeros((self.em_det_no, self.radon_total_iter_no), dtype=np.int)
        self.is_scanner_dirty = True

    def radon_transform_step(self):
        """
        Calculate the next step of Radom transform
        :return: False if the transform is done, true if there are still steps available
        """
        if self.current_radon_iteration < self.radon_total_iter_no:
            self.current_emitters, self.current_detectors = self._calculate_emitters_detectors_position()
            self.current_scan_lines = self._calculate_scan_lines(self.current_emitters, self.current_detectors)
            self.scan_lines.append(self.current_scan_lines)
            self.is_scanner_dirty = False
            for line_id, line in enumerate(self.current_scan_lines):
                line_integral = np.sum([self.input_image[point] for point in self.current_scan_lines[line_id]])
                self.radon_result[line_id, self.current_radon_iteration] += line_integral
                if line_id % 5 == 0:
                    self.radon_step_progress_clbk(line_id, self.em_det_no)
            self.current_alpha += self.delta_alpha
            self.radon_total_progress_clbk(self.current_radon_iteration, self.radon_total_iter_no - 1)
            self.current_radon_iteration += 1
            return True
        else:
            return False

    def radon_transform_full(self):
        while self.radon_transform_step():
            pass

    def is_radon_finished(self):
        return self.current_radon_iteration >= self.radon_total_iter_no

    def _calculate_emitters_detectors_position(self):
        emitters = []
        detectors = []
        r = self.circumcircle_diameter // 2
        angles = np.linspace(start=self.current_alpha - self.em_det_spread / 2,
                             stop=self.current_alpha + self.em_det_spread / 2, num=self.em_det_no)
        angles_rad = [math.radians(x) for x in angles]
        for i in range(self.em_det_no):
            angle_rad = angles_rad[i]
            emitter_a = int(self.input_image_center + r * math.cos(angle_rad))
            emitter_b = int(self.input_image_center - r * math.sin(angle_rad))
            emitters.append((emitter_a, emitter_b))
        for i in range(self.em_det_no - 1, -1, -1):
            angle_rad = angles_rad[i]
            detector_a = int(self.input_image_center - r * math.cos(angle_rad))
            detector_b = int(self.input_image_center + r * math.sin(angle_rad))
            detectors.append((detector_a, detector_b))
        return emitters, detectors

    def _calculate_scan_lines(self, emitters, detectors):
        return [generate_line(emitters[i][0], emitters[i][1], detectors[i][0], detectors[i][1])
                for i in range(self.em_det_no)]

    def init_iradon(self):
        self.rec_img_dirty = True
        self.current_iradon_iteration = 0
        self.iradon_result = np.zeros((self.input_image_width, self.input_image_width), dtype=np.int)

    def iradon_step(self):
        self.rec_img_dirty = True
        for s, line in enumerate(self.scan_lines[self.current_iradon_iteration]):
            for point in line:
                self.iradon_result[point] += self.radon_result[s, self.current_iradon_iteration]
            if s % 5 == 0:
                self.iradon_step_progress_clbk(s, self.em_det_no)
        self.iradon_total_progress_clbk(self.current_iradon_iteration, self.radon_total_iter_no - 1)
        self.current_iradon_iteration += 1
        if self.current_iradon_iteration < self.radon_result.shape[1]:
            return True
        else:  # End of processing
            return False

    def iradon_full(self):
        while self.iradon_step():
            pass

    def is_iradon_finished(self):
        return self.current_iradon_iteration >= self.radon_total_iter_no

    def visualize_scanner(self):
        scanner_vis_img = self.input_image.copy()
        self._visualize_circumcircle(scanner_vis_img)
        if self.is_scanner_dirty:
            self.current_emitters, self.current_detectors = self._calculate_emitters_detectors_position()
            self.current_scan_lines = self._calculate_scan_lines(self.current_emitters, self.current_detectors)
            self.is_scanner_dirty = False
        for emitter in self.current_emitters:
            _visualize_emitter(scanner_vis_img, emitter)
        for detector in self.current_detectors:
            _visualize_detector(scanner_vis_img, detector)
        _visualize_scan_lines(scanner_vis_img, self.current_scan_lines)
        return scanner_vis_img

    def _visualize_circumcircle(self, image):
        rr, cc = draw.circle_perimeter(r=self.input_image_center, c=self.input_image_center,
                                       radius=int(self.circumcircle_diameter / 2))
        image[rr, cc] = 255

    def visualize_sinogram(self):
        singoram_image = np.zeros((self.radon_result.shape[0], self.radon_result.shape[1]), dtype=np.uint8)
        max_val = np.max(self.radon_result)
        min_val = np.min(self.radon_result)
        for i in range(len(self.radon_result)):
            self.normalization_radon_progress_clbk(i, len(self.radon_result))
            for j in range(len(self.radon_result[i])):
                singoram_image[i, j] = normalize(self.radon_result[i, j], min_val, max_val)
        return singoram_image

    def visualize_reconstructed_img(self):
        if self.rec_img_dirty:
            self.rec_img = np.zeros((self.iradon_result.shape[0], self.iradon_result.shape[1]), dtype=np.uint8)
            max_val = np.max(self.iradon_result)
            min_val = np.min(self.iradon_result)
            for i in range(len(self.iradon_result)):
                self.normalization_iradon_progress_clbk(i, len(self.iradon_result))
                for j in range(len(self.iradon_result[i])):
                    self.rec_img[i, j] = normalize(self.iradon_result[i, j], min_val, max_val)
            self.rec_img_dirty = False
        return self.rec_img

    def restart_scanner(self):
        self.init_radon()
        self.init_iradon()
        pass


def _visualize_emitter(image, coords):
    rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
    image[rr, cc] = 255


def _visualize_detector(image, coords):
    rr, cc = draw.circle(r=coords[0], c=coords[1], radius=10)
    image[rr, cc] = 127


def _visualize_scan_lines(image, scan_lines):
    for line in scan_lines:
        for a, b in line:
            image[a][b] = 255


def normalize(value, min_val, max_val, normalize_to=255):
    try:
        return int((value - min_val) / (max_val - min_val) * normalize_to)
    except ValueError:
        print("NAN in normalize")
        return 0


def make_image_square(image):
    a, b = image.shape
    if a == b:
        return image
    else:
        if a > b:
            padding = ((0, 0), (0, a - b))
        else:
            padding = ((0, b - a), (0, 0))
        return np.pad(image, padding, mode='constant', constant_values=0)
