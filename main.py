import os
from skimage import io
from gui import CTScannerGUI
from ct_scanner import CTScanner
import tkinter as tk
import dicom_handler
from tkinter import filedialog

IMG_DIR = 'zdjecia'


def open_image(img_name):
    return io.imread(os.path.join(IMG_DIR, img_name), as_gray=True)


def select_file(path):
    f_path = filedialog.askopenfilename(initialdir=path, title='Proszę wybrać plik wejściowy',
                                        filetypes=(
                                            ('Supported formats', ('*dcm', '*jpg', '*jpeg', '*DCM', '*JPG', '*JPEG')),
                                            ('JPEG files', ('*jpg', '*jpeg')),
                                            ('DICOM files', ('*dcm', '*DCM')),
                                            ('All files', '*')))
    is_dicom_file = False
    if f_path:
        if f_path[-4:].lower() == '.dcm':
            is_dicom_file = True
    return f_path, is_dicom_file


class Main:
    input_image = None
    is_input_file_dicom = False
    dicom_dataset = None
    ct_scanner = None
    iradon_initialized = False
    radon_initialized = False

    def __init__(self):
        self.tk_root = tk.Tk()
        self.gui = CTScannerGUI(self.tk_root, input_image_select_clbk=self.select_input_img,
                                sim_options_confirm_clbk=self.simulation_options_changed,
                                radon_next_step_clbk=self.radon_next_step,
                                iradon_next_step_clbk=self.iradon_next_step)
        self.ct_scanner = CTScanner(self.gui.set_step_radon_progress, self.gui.set_total_radon_progress,
                                    self.gui.set_step_iradon_progress, self.gui.set_total_iradon_progress)
        self.tk_root.mainloop()

    def select_input_img(self):
        file_path, self.is_input_file_dicom = select_file('.')
        if file_path:
            self.restart_app()
            if self.is_input_file_dicom:
                self.dicom_dataset, self.input_image = dicom_handler.dicom_load(file_path)
                # self.gui.dicom_show_frame.pack()
            else:
                self.input_image = open_image(file_path)
                self.dicom_dataset = dicom_handler.dicom_create_new_dataset()
                # self.gui.dicom_show_frame.pack_forget()

            self.gui.dicom_show_display_dataset(self.dicom_dataset)
            self.gui.display_image(self.input_image, 'input')
            self.ct_scanner.set_input_image(self.input_image)

    def simulation_options_changed(self):
        delta_alpha_step, number_of_detectors, detectors_spread = self.gui.get_simulations_options()
        self.ct_scanner.set_params(delta_alpha=float(delta_alpha_step), n=int(number_of_detectors),
                                   l=float(detectors_spread))
        # Visualize the scanner
        self.gui.display_image(self.ct_scanner.visualize_scanner(), 'options')

    def radon_next_step(self):
        if not self.radon_initialized:
            self.ct_scanner.init_radon()
            self.radon_initialized = True
        if self.gui.show_steps_radon_var.get() == 1:
            self.ct_scanner.radon_transform_step()
        else:
            self.ct_scanner.radon_transform_full()
        self.gui.display_image(self.ct_scanner.visualize_scanner(), 'simulation_step')
        self.gui.display_image(self.ct_scanner.visualize_sinogram(), 'sinogram')

    def iradon_next_step(self):
        if not self.iradon_initialized:
            self.ct_scanner.init_iradon()
            self.iradon_initialized = True

        if self.gui.show_steps_iradon_var.get() == 1:
            self.ct_scanner.iradon_step()
        else:
            self.ct_scanner.iradon_full()
        self.gui.display_image(self.ct_scanner.visualize_reconstructed_img(), 'reco_img')

    def restart_app(self):
        # Useful when changing the input image
        self.ct_scanner.restart_scanner()
        self.gui.dicom_show_list.delete(0, self.gui.dicom_show_list_next_id)
        self.gui.dicom_show_list_next_id = 1


def main():
    m = Main()


def test():
    select_file('.')


if __name__ == '__main__':
    main()
    # test()
