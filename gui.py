import tkinter as tk
import numpy as np
import PIL.Image
import PIL.ImageTk
import datetime
import time
from tkinter import ttk
from dicom_handler import dicom_date_dataset_to_display, dicom_time_dataset_to_display

# TODO: Set default values

DELTA_ALPHA_STEP_MIN = 0.1
DELTA_ALPHA_STEP_MAX = 30
DELTA_ALPHA_STEP_INCREMENT = 0.1

NUMBER_OF_DETECTORS_MIN = 10
NUMBER_OF_DETECTORS_MAX = 1000
NUMBER_OF_DETECTORS_INCREMENT = 1

SPREAD_MIN = 10
SPREAD_MAX = 180
SPREAD_INCREMENT = 1

IMAGE_WIDTH = 200
IMAGE_HEIGHT = 200

AS_IMG_TEXT = 'Jako obraz JPG'
AS_DICOM_TEXT = 'W formacie DICOM'


class CTScannerGUI:
    def __init__(self, master, input_image_select_clbk, sim_options_confirm_clbk, radon_next_step_clbk,
                 iradon_next_step_clbk, dicom_edit_clbk):
        self.master = master
        master.title('Symulator tomografu')
        # Create widgets
        self._setup_menu_bar(input_image_select_clbk)
        self._setup_input_data_view(dicom_edit_clbk)
        self._setup_simulation_options(sim_options_confirm_clbk)
        self.show_steps_radon_var = tk.IntVar()
        self.enable_filtering_var = tk.IntVar()
        self._setup_show_radon(radon_next_step_clbk)
        self.show_steps_iradon_var = tk.IntVar()
        self._setup_iradon(iradon_next_step_clbk)

    def _setup_menu_bar(self, input_image_select_clbk):
        self.menu_bar = tk.Menu(master=self.master, tearoff=0)
        self.menu_bar.add_command(label='Otwórz plik', command=input_image_select_clbk)
        self.menu_bar_save_menu = tk.Menu(master=self.menu_bar)
        self.menu_bar_save_menu.add_command(label=AS_IMG_TEXT, command=None, state='disabled')
        self.menu_bar_save_menu.add_command(label=AS_DICOM_TEXT, command=None, state='disabled')

        self.menu_bar.add_cascade(label='Zapisz uzyskany obraz', menu=self.menu_bar_save_menu)
        self.master.config(menu=self.menu_bar)

    def _setup_input_data_view(self, dicom_edit_clbk):
        self.input_data_frame = tk.LabelFrame(master=self.master, text='Dane wejściowe')
        self.input_image = tk.Canvas(master=self.input_data_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.dicom_show_frame = tk.LabelFrame(master=self.input_data_frame, text='DICOM')
        self.dicom_show_list = tk.Listbox(master=self.dicom_show_frame, width=50)
        self.dicom_show_list_next_id = 1
        self.dicom_edit_btn = tk.Button(master=self.dicom_show_frame, text='Edytuj', command=dicom_edit_clbk,
                                        state='disabled')
        self.input_data_frame.grid(row=0, column=0, sticky=tk.N + tk.W, pady=0, ipadx=0)
        self.input_image.pack()
        self.dicom_show_frame.pack()
        self.dicom_show_list.pack()
        self.dicom_edit_btn.pack()

    def _setup_simulation_options(self, sim_options_confirm_clbk):
        self.settings_frame = tk.LabelFrame(master=self.input_data_frame, text='Ustawienia skanera')
        # Delta alpha step
        self.delta_alpha_step_label = tk.Label(master=self.settings_frame, text='Krok Δα układu emiter/detektor')
        self.delta_alpha_step = tk.Scale(master=self.settings_frame, from_=DELTA_ALPHA_STEP_MIN,
                                         to=DELTA_ALPHA_STEP_MAX, resolution=DELTA_ALPHA_STEP_INCREMENT,
                                         orient=tk.HORIZONTAL)
        # Number of detectors (n)
        self.number_of_detectors_label = tk.Label(master=self.settings_frame, text='Liczba detektorów (n)')
        self.number_of_detectors = tk.Scale(master=self.settings_frame, from_=NUMBER_OF_DETECTORS_MIN,
                                            to=NUMBER_OF_DETECTORS_MAX, resolution=NUMBER_OF_DETECTORS_INCREMENT,
                                            orient=tk.HORIZONTAL)
        # Emitter / detector spread (l)
        self.detectors_spread_label = tk.Label(master=self.settings_frame,
                                               text='Rozwartość / rozpiętość układu emiter/detektor (l)')
        self.detectors_spread = tk.Scale(master=self.settings_frame, from_=SPREAD_MIN, to=SPREAD_MAX,
                                         resolution=SPREAD_INCREMENT, orient=tk.HORIZONTAL)
        self.options_confirm = tk.Button(master=self.settings_frame, text='Zatwierdź',
                                         command=sim_options_confirm_clbk, state='disabled')

        # self.options_image = tk.Canvas(master=self.settings_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        # self.settings_frame.grid(row=1, column=0, sticky=tk.N + tk.W, pady=0, ipadx=0)
        self.settings_frame.pack()
        self.delta_alpha_step_label.pack()
        self.delta_alpha_step.pack()
        self.number_of_detectors_label.pack()
        self.number_of_detectors.pack()
        self.detectors_spread_label.pack()
        self.detectors_spread.pack()
        self.options_confirm.pack()
        # self.options_image.pack()

    def _radon_show_steps_clbk(self):
        """Called when 'show radon steps' option is changed.
        Used only to change the text on a button"""
        if self.show_steps_radon_var.get() == 1:
            self.next_sim_step.config(text='Następny krok')
        else:
            self.next_sim_step.config(text='Wykonaj')

    def _setup_show_radon(self, radon_next_step_clbk):
        self.radon_frame = tk.LabelFrame(master=self.master, text='Transformata Radona')
        self.show_steps_radon = tk.Checkbutton(master=self.radon_frame, text='Pokazuj kroki pośrednie',
                                               variable=self.show_steps_radon_var,
                                               command=self._radon_show_steps_clbk)
        self.next_sim_step = tk.Button(master=self.radon_frame, text='Wykonaj', command=radon_next_step_clbk,
                                       state='disabled')
        self.radon_progress_frame = tk.Frame(master=self.radon_frame)
        self.radon_total_progress_label = tk.Label(master=self.radon_progress_frame, text='Całkowity postęp')
        self.radon_total_progress = ttk.Progressbar(master=self.radon_progress_frame, value=0, maximum=100)
        self.radon_step_progress_label = tk.Label(master=self.radon_progress_frame, text='Postęp iteracji')
        self.radon_step_progress = ttk.Progressbar(master=self.radon_progress_frame, value=0, maximum=100)
        self.radon_norm_progress_label = tk.Label(master=self.radon_progress_frame, text='Postęp normalizacji')
        self.radon_norm_progress = ttk.Progressbar(master=self.radon_progress_frame, value=0, maximum=100)
        # TODO: Add normalization progress
        self.simulation_step_image = tk.Canvas(master=self.radon_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

        self.radon_frame.grid(row=0, column=2)
        self.show_steps_radon.pack()
        self.next_sim_step.pack()
        self.radon_progress_frame.pack()
        self.radon_total_progress_label.grid(row=0, column=0, sticky=tk.W)
        self.radon_total_progress.grid(row=0, column=1)
        self.radon_step_progress_label.grid(row=1, column=0, sticky=tk.W)
        self.radon_step_progress.grid(row=1, column=1)
        self.radon_norm_progress_label.grid(row=2, column=0, sticky=tk.W)
        self.radon_norm_progress.grid(row=2, column=1)
        self.simulation_step_image.pack()
        self.sinogram_image = tk.Canvas(master=self.radon_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.sinogram_image.pack()

    def _iradon_show_steps_clbk(self):
        """Called when 'show image reconstruction steps' option is changed.
        Used only to change the text on a button"""
        if self.show_steps_iradon_var.get() == 1:
            self.next_reco_step.config(text='Następny krok')
        else:
            self.next_reco_step.config(text='Wykonaj')

    def _setup_iradon(self, iradon_next_step_clbk):
        self.iradon_frame = tk.LabelFrame(master=self.master, text='Odtwarzanie obrazu wejściowego')
        self.show_steps_iradon = tk.Checkbutton(master=self.iradon_frame, text='Pokazuj kroki pośrednie',
                                                variable=self.show_steps_iradon_var,
                                                command=self._iradon_show_steps_clbk)
        self.enable_filtering = tk.Checkbutton(master=self.iradon_frame, text='Włącz filtr',
                                               variable=self.enable_filtering_var)
        self.next_reco_step = tk.Button(master=self.iradon_frame, text='Wykonaj', command=iradon_next_step_clbk,
                                        state='disabled')
        self.iradon_progress_frame = tk.Frame(master=self.iradon_frame)
        self.iradon_total_progress_label = tk.Label(master=self.iradon_progress_frame, text='Całkowity postęp')
        self.iradon_total_progress = ttk.Progressbar(master=self.iradon_progress_frame, value=0, maximum=100)
        self.iradon_step_progress_label = tk.Label(master=self.iradon_progress_frame, text='Postęp iteracji')
        self.iradon_step_progress = ttk.Progressbar(master=self.iradon_progress_frame, value=0, maximum=100)
        self.iradon_norm_progress_label = tk.Label(master=self.iradon_progress_frame, text='Postęp normalizacji')
        self.iradon_norm_progress = ttk.Progressbar(master=self.iradon_progress_frame, value=0, maximum=100)
        self.reco_image = tk.Canvas(master=self.iradon_frame, width=2 * IMAGE_WIDTH, height=2 * IMAGE_HEIGHT)
        self.error_label = tk.Label(master=self.iradon_frame)
        self.iradon_frame.grid(row=0, column=3)
        self.show_steps_iradon.pack()
        self.enable_filtering.pack()
        self.next_reco_step.pack()
        self.iradon_progress_frame.pack()
        self.iradon_total_progress_label.grid(row=0, column=0, sticky=tk.W)
        self.iradon_total_progress.grid(row=0, column=1)
        self.iradon_step_progress_label.grid(row=1, column=0, sticky=tk.W)
        self.iradon_step_progress.grid(row=1, column=1)
        self.iradon_norm_progress_label.grid(row=2, column=0, sticky=tk.W)
        self.iradon_norm_progress.grid(row=2, column=1)
        self.reco_image.pack()
        self.error_label.pack()

    def display_image(self, image_array, image_type):
        # PIL doesn't support floating point inputs
        if image_array.dtype == np.float64:
            image_array = (image_array * 255).astype(np.uint8)
        if image_type == 'input':
            canvas = self.input_image
        elif image_type == 'options':
            # canvas = self.options_image
            canvas = self.simulation_step_image
        elif image_type == 'simulation_step':
            canvas = self.simulation_step_image
        elif image_type == 'sinogram':
            canvas = self.sinogram_image
        elif image_type == 'reco_img':
            canvas = self.reco_image
        else:
            print('This image type doesn\'t exist')
            return
        # Convert image from numpy array to PIL image and resize it
        img = PIL.Image.fromarray(image_array).resize((canvas.winfo_width(), canvas.winfo_height()),
                                                      PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.photo = img

    def get_simulations_options(self):
        delta_alpha_step = self.delta_alpha_step.get()
        number_of_detectors = self.number_of_detectors.get()
        detectors_spread = self.detectors_spread.get()
        return delta_alpha_step, number_of_detectors, detectors_spread

    def dicom_show_display_dataset(self, dataset):  # TODO: Add comment support
        try:
            study_id = dataset.StudyID
        except AttributeError:
            study_id = 'Brak'
        self._dicom_show_add_elem('ID badania', study_id)
        try:
            series_number = str(dataset.SeriesNumber)
        except AttributeError:
            series_number = 'Brak'
        self._dicom_show_add_elem('Numer seryjny', series_number)
        try:
            accession_number = dataset.AccessionNumber
        except AttributeError:
            accession_number = 'Brak'
        self._dicom_show_add_elem('Numer katalogowy', accession_number)
        try:
            study_date = dicom_date_dataset_to_display(dataset.StudyDate)
        except AttributeError:
            study_date = 'Brak'
        self._dicom_show_add_elem('Data badania', study_date)
        try:
            study_time = dicom_time_dataset_to_display(dataset.StudyTime)
        except AttributeError:
            study_time = 'Brak'
        self._dicom_show_add_elem('Godzina badania', study_time)
        try:
            referring_phycician = dataset.ReferringPhysicianName
        except AttributeError:
            referring_phycician = 'Brak'
        self._dicom_show_add_elem('Lekarz zlecający', str(referring_phycician))
        try:
            patient_id = dataset.PatientID
        except AttributeError:
            patient_id = 'Brak'
        self._dicom_show_add_elem('ID pacjenta', patient_id)
        try:
            patient_name = str(dataset.PatientName)
        except AttributeError:
            patient_name = 'Brak'
        self._dicom_show_add_elem('Dane osobowe pacjenta', patient_name)
        try:
            patient_sex = dataset.PatientSex
            if patient_sex == 'F':
                patient_sex = 'Kobieta'
            elif patient_sex == 'M':
                patient_sex = 'Mężczyzna'
        except AttributeError:
            patient_sex = 'Brak'
        self._dicom_show_add_elem('Płeć pacjenta', patient_sex)
        try:
            patient_birthday = dicom_date_dataset_to_display(dataset.PatientBirthDay)
        except AttributeError:
            patient_birthday = 'Brak'
        self._dicom_show_add_elem('Data ur. pacjenta', patient_birthday)
        try:
            patient_orientation = dataset.PatientOrientation
        except AttributeError:
            patient_orientation = 'Brak'
        self._dicom_show_add_elem('Położenie pacjenta', patient_orientation)
        try:
            comment = ''  # TODO: Find which attribute it is
        except AttributeError:
            comment = 'Brak'
        self._dicom_show_add_elem('Komentarz', comment)
        # Adjust list height to fit all fields
        self.dicom_show_list.config(height=self.dicom_show_list_next_id - 1)

    def _dicom_show_add_elem(self, name, value):
        entry = ': '.join([name, value])
        self.dicom_show_list.insert(self.dicom_show_list_next_id, entry)
        self.dicom_show_list_next_id += 1

    def show_dicom_edit_window(self):
        pass

    def set_total_radon_progress(self, cur_val, max_val=None):
        self._set_progress(self.radon_total_progress, cur_val, max_val)

    def set_step_radon_progress(self, cur_val, max_val=None):
        self._set_progress(self.radon_step_progress, cur_val, max_val)

    def set_total_iradon_progress(self, cur_val, max_val=None):
        self._set_progress(self.iradon_total_progress, cur_val, max_val)

    def set_step_iradon_progress(self, cur_val, max_val=None):
        self._set_progress(self.iradon_step_progress, cur_val, max_val)

    def set_normalization_radon_progress(self, cur_val, max_val=None):
        self._set_progress(self.radon_norm_progress, cur_val, max_val)

    def set_normalization_iradon_progress(self, cur_val, max_val=None):
        self._set_progress(self.iradon_norm_progress, cur_val, max_val)

    def _set_progress(self, field, cur_val, max_val=None):
        if max_val:
            field['value'] = 100 * cur_val / max_val
        else:
            field['value'] = cur_val
        field.update()

    def toggle_button(self, name, state):
        """
        :param name:
        :param state: True to enable, False to disable
        """
        if name == 'dicom_edit':
            btn = self.dicom_edit_btn
        elif name == 'options':
            btn = self.options_confirm
        elif name == 'radon':
            btn = self.next_sim_step
        elif name == 'iradon':
            btn = self.next_reco_step
        else:
            print('Error, button doesn\'t exist')
            return
        if state:
            btn['state'] = 'normal'
        else:
            btn['state'] = 'disable'

    def toggle_save_menu(self, state):
        if state:
            self.menu_bar_save_menu.entryconfig(AS_IMG_TEXT, state='normal')
            self.menu_bar_save_menu.entryconfig(AS_DICOM_TEXT, state='normal')
        else:
            self.menu_bar_save_menu.entryconfig(AS_IMG_TEXT, state='disabled')
            self.menu_bar_save_menu.entryconfig(AS_DICOM_TEXT, state='disabled')


def test():
    root = tk.Tk()
    gui = CTScannerGUI(root, None, None, None, None)

    from dicom_handler import dicom_load, dicom_list_files
    dcm_files = dicom_list_files('/home/piotr/studia_sem6/IWM/Tomograf/dicom_files')
    ds = dicom_load(dcm_files['vhf.1501.dcm'])
    gui.dicom_show_display_dataset(ds)

    root.mainloop()
    gui.show_dicom_edit_window()


if __name__ == '__main__':
    test()
