import os
from skimage import io
from gui import TomographGUI
from tomograph import Tomograph
import tkinter as tk

IMG_DIR = 'zdjecia'


def open_all_images():
    """
    Opens all of the test images as numpy arrays.
    :return: A dictionary in which image names (without extensions) are keys
    """
    images = {}
    for img_name in os.listdir(IMG_DIR):
        images[img_name.split('.')[0]] = io.imread(os.path.join(IMG_DIR, img_name), as_gray=True)
    print('--------------------')
    print('Available images:')
    print(list(images.keys()))
    print('--------------------')
    return images


def get_avail_image_names():
    return os.listdir(IMG_DIR)


def open_image(img_name):
    return io.imread(os.path.join(IMG_DIR, img_name), as_gray=True)


class Main:
    input_image = None
    tomograph = None

    def __init__(self):
        # self.tomograph = Tomograph()
        self.tk_root = tk.Tk()
        self.gui = TomographGUI(self.tk_root, input_image_confirm_clbk=self.input_image_selected,
                                sim_options_confirm_clbk=self.simulation_options_changed,
                                radon_next_step_clbk=self.radon_next_step)
        self.avail_img_names = get_avail_image_names()
        self.gui.set_available_input_images(self.avail_img_names)
        self.tk_root.mainloop()

    def input_image_selected(self):
        img_id = self.gui.get_selected_input_image()[0]
        self.input_image = open_image(self.avail_img_names[img_id])
        self.gui.display_image(self.input_image, 'input')

    def simulation_options_changed(self):
        delta_alpha_step, number_of_detectors, detectors_spread = self.gui.get_simulations_options()
        self.tomograph = Tomograph(self.input_image, delta_alpha=float(delta_alpha_step),
                                   n=int(number_of_detectors), l=float(detectors_spread))
        # Visualize the scanner
        self.gui.display_image(self.tomograph.visualize_scanner(), 'options')

    def radon_next_step(self):
        if self.tomograph.radon_transform_step():
            self.gui.display_image(self.tomograph.visualize_scanner(), 'simulation_step')
            self.gui.display_image(self.tomograph.visualize_sinogram(), 'singogram')

def main():
    m = Main()


if __name__ == '__main__':
    main()
