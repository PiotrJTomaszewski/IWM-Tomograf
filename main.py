import os
from skimage import io
from gui import CTScannerGUI
from ct_scanner import CTScanner
import tkinter as tk
import dicom_handler
from tkinter import filedialog
import numpy as np
from dicom_edit_dialog import DicomEditDialog


def open_image(img_path):
    return io.imread(img_path, as_gray=True)


def select_file(path):
    f_path = filedialog.askopenfilename(initialdir=path, title='Proszę wybrać plik wejściowy',
                                        filetypes=(
                                            ('Supported formats',
                                             ('*.dcm', '*.jpg', '*.jpeg', '*.DCM', '*.JPG', '*.JPEG')),
                                            ('JPEG files', ('*.jpg', '*.jpeg')),
                                            ('DICOM files', ('*.dcm', '*.DCM')),
                                            ('All files', '*')))
    is_dicom_file = False
    if f_path:
        if f_path[-4:].lower() == '.dcm':
            is_dicom_file = True
    return f_path, is_dicom_file


def calculate_mse(in_img, out_img):
    """Calculates the Mean Squared Error of the two images"""
    error = 0
    for x in range(in_img.shape[0]):
        for y in range(in_img.shape[1]):
            error += (in_img[x, y] - out_img[x, y]) ** 2
    return error / (in_img.shape[0] * in_img.shape[1])


class Main:
    input_image = None
    is_input_file_dicom = False
    dicom_dataset = None
    ct_scanner = None
    iradon_initialized = False
    radon_initialized = False
    radon_currently_running = False
    iradon_currently_running = False

    def __init__(self):
        self.tk_root = tk.Tk()
        self.gui = CTScannerGUI(self.tk_root, input_image_select_clbk=self.select_input_img,
                                sim_options_confirm_clbk=self.simulation_options_changed,
                                radon_next_step_clbk=self.radon_next_step,
                                iradon_next_step_clbk=self.iradon_next_step,
                                dicom_edit_clbk=self.dicom_edit_clbk,
                                dicom_save_in_clbk=self.dicom_save_in,
                                dicom_save_out_clbk=self.dicom_save_out,
                                jpg_save_clbk=self.jpg_save)
        self.ct_scanner = CTScanner(self.gui.set_step_radon_progress, self.gui.set_total_radon_progress,
                                    self.gui.set_step_iradon_progress, self.gui.set_total_iradon_progress,
                                    self.gui.set_normalization_radon_progress,
                                    self.gui.set_normalization_iradon_progress)
        self.tk_root.mainloop()

    def select_input_img(self):
        file_path, self.is_input_file_dicom = select_file('.')
        if file_path:
            if self.is_input_file_dicom:
                self.dicom_dataset, self.input_image = dicom_handler.dicom_load(file_path)
                # self.gui.dicom_show_frame.pack()
            else:
                self.input_image = open_image(file_path)
                self.dicom_dataset = dicom_handler.dicom_create_new_dataset()
                # self.gui.dicom_show_frame.pack_forget()

            self.gui.display_image(self.input_image, 'input')
            self.ct_scanner.set_input_image(self.input_image)
            # "Restart" the app
            self.ct_scanner.restart_scanner()
            # self.gui.dicom_show_list.delete(0, self.gui.dicom_show_list_next_id)
            # self.gui.dicom_show_list_next_id = 1
            self.gui.dicom_load_current_values(dicom_handler.dicom_read_dataset(self.dicom_dataset))

            self.gui.display_image(np.zeros((100, 100), dtype=np.uint8), 'simulation_step')
            self.gui.display_image(np.zeros((100, 100), dtype=np.uint8), 'sinogram')
            self.gui.display_image(np.zeros((100, 100), dtype=np.uint8), 'reco_img')
            self.gui.set_step_radon_progress(0)
            self.gui.set_total_radon_progress(0)
            self.gui.set_step_iradon_progress(0)
            self.gui.set_total_iradon_progress(0)
            self.gui.set_step_radon_progress(0)
            self.gui.set_normalization_radon_progress(0)
            self.gui.set_normalization_iradon_progress(0)
            self.gui.error_label.config(text='')
            self.gui.toggle_button('dicom_edit', True)
            self.gui.toggle_button('options', True)
            self.gui.toggle_button('radon', False)
            self.gui.toggle_button('iradon', False)
            self.gui.toggle_save_jpg_menu(False)
            self.gui.toggle_save_dicom_out_menu(False)
            self.gui.toggle_save_dicom_in_menu(True)

    def simulation_options_changed(self):
        delta_alpha_step, number_of_detectors, detectors_spread = self.gui.get_simulations_options()
        self.ct_scanner.set_params(delta_alpha=float(delta_alpha_step), n=int(number_of_detectors),
                                   l=float(detectors_spread))
        # Visualize the scanner
        self.gui.display_image(self.ct_scanner.visualize_scanner(), 'options')
        self.ct_scanner.restart_scanner()
        self.gui.display_image(np.zeros((100, 100), dtype=np.uint8), 'sinogram')
        self.gui.display_image(np.zeros((100, 100), dtype=np.uint8), 'reco_img')
        self.gui.set_step_radon_progress(0)
        self.gui.set_total_radon_progress(0)
        self.gui.set_step_iradon_progress(0)
        self.gui.set_total_iradon_progress(0)
        self.gui.set_normalization_radon_progress(0)
        self.gui.set_normalization_iradon_progress(0)
        self.gui.toggle_button('radon', True)
        self.gui.toggle_button('iradon', False)
        self.gui.toggle_save_jpg_menu(False)
        self.gui.toggle_save_dicom_out_menu(False)

    def radon_next_step(self):
        if not self.radon_currently_running:  # If I spam the button weird things happen, so a quick workaround
            self.radon_currently_running = True
            self.gui.toggle_button('radon', False)
            self.gui.set_normalization_radon_progress(0)
            if not self.radon_initialized:
                self.ct_scanner.init_radon()
                self.radon_initialized = True
            if self.gui.show_steps_radon_var.get() == 1:
                self.ct_scanner.radon_transform_step()
            else:
                self.ct_scanner.radon_transform_full()
            self.gui.display_image(self.ct_scanner.visualize_scanner(), 'simulation_step')
            self.gui.display_image(self.ct_scanner.visualize_sinogram(), 'sinogram')
            self.gui.toggle_button('radon', True)
            if self.ct_scanner.is_radon_finished():
                self.gui.toggle_button('radon', False)
                self.gui.toggle_button('iradon', True)
                self.gui.toggle_save_jpg_menu(False)
                self.gui.toggle_save_dicom_out_menu(False)
            self.radon_currently_running = False

    def iradon_next_step(self):
        if not self.iradon_currently_running:  # If I spam the button weird things happen, so a quick workaround
            self.iradon_currently_running = True
            self.gui.toggle_button('iradon', False)
            self.gui.set_normalization_iradon_progress(0)
            if not self.iradon_initialized:
                self.ct_scanner.init_iradon()
                self.iradon_initialized = True

            if self.gui.show_steps_iradon_var.get() == 1:
                self.ct_scanner.iradon_step()
            else:
                self.ct_scanner.iradon_full()
            reconstructed_img = self.ct_scanner.visualize_reconstructed_img()
            self.gui.display_image(reconstructed_img, 'reco_img')
            self.gui.toggle_button('iradon', True)
            if self.ct_scanner.is_iradon_finished():
                mse = calculate_mse(self.ct_scanner.input_image, reconstructed_img)  # TODO: Add a button for mse
                self.gui.error_label.config(text='Błąd średniokwadratowy: ' + str(np.round(mse, 3)))
                self.gui.toggle_button('iradon', False)
                self.gui.toggle_save_jpg_menu(True)
                self.gui.toggle_save_dicom_out_menu(True)
            self.iradon_currently_running = False

    def dicom_edit_clbk(self):
        data = self.gui.get_dicom_fields_content()
        is_data_ok, error_msg = dicom_handler.dicom_check_data(data)
        if is_data_ok:
            self.dicom_dataset = dicom_handler.dicom_store_data(data, self.dicom_dataset)
            self.gui.error_msg_var.set('Pomyślnie zaktualizowano dane')
        else:
            self.gui.error_msg_var.set(error_msg)

    # TODO: Auto add extension
    def dicom_show_save_dialog(self, image):
        f_path = filedialog.asksaveasfilename(initialdir='.', title='Zapisz plik w formacie DICOM',
                                              filetypes=[['DICOM files', ('*.dcm', '*.DCM')]])
        if f_path and f_path != '':
            dicom_handler.dicom_save(f_path, self.dicom_dataset, image)

    def dicom_save_in(self):
        self.dicom_show_save_dialog(self.input_image)

    def dicom_save_out(self):
        self.dicom_show_save_dialog(self.ct_scanner.visualize_reconstructed_img())

    def jpg_save(self):
        f_path = filedialog.asksaveasfilename(initialdir='.', title='Zapisz plik w formacjie JPG',
                                              filetypes=[['JPG files', ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG')]])
        if f_path and f_path != '':
            io.imsave(f_path, self.ct_scanner.visualize_reconstructed_img())


def main():
    m = Main()


def test():
    select_file('.')


if __name__ == '__main__':
    main()
    # test()
