import tkinter as tk
import numpy as np
import PIL.Image
import PIL.ImageTk
import datetime
import time
from tkinter import ttk

# TODO: Set default values

DELTA_ALPHA_STEP_DEFAULT = 10
DELTA_ALPHA_STEP_MIN = 1
DELTA_ALPHA_STEP_MAX = 50
DELTA_ALPHA_STEP_INCREMENT = 1

NUMBER_OF_DETECTORS_DEFAULT = 400
NUMBER_OF_DETECTORS_MIN = 10
NUMBER_OF_DETECTORS_MAX = 2000
NUMBER_OF_DETECTORS_INCREMENT = 10

SPREAD_DEFAULT = 100
SPREAD_MIN = 10
SPREAD_MAX = 180
SPREAD_INCREMENT = 1

IMAGE_WIDTH = 200
IMAGE_HEIGHT = 200

AS_IMG_TEXT = 'Zapisz obraz wyjściowy w formacie JPG'
AS_DICOM_OUT_TEXT = 'Zapisz obraz wyjściowy w formacie DICOM'
AS_DICOM_IN_TEXT = 'Zapisz obraz wejściowy w formacie DICOM'


class CTScannerGUI:
    def __init__(self, master, input_image_select_clbk, sim_options_confirm_clbk, radon_next_step_clbk,
                 iradon_next_step_clbk, dicom_edit_clbk, dicom_save_in_clbk, dicom_save_out_clbk, jpg_save_clbk):
        self.master = master
        master.title('Symulator tomografu')
        # Create widgets
        self._setup_menu_bar(input_image_select_clbk, dicom_save_in_clbk, dicom_save_out_clbk, jpg_save_clbk)
        self._setup_input_data_view()
        self.error_msg_var = tk.StringVar()
        self._setup_dicom_ui(dicom_edit_clbk)
        self._setup_simulation_options(sim_options_confirm_clbk)
        self.show_steps_radon_var = tk.IntVar()
        self.enable_filtering_var = tk.IntVar()
        self._setup_show_radon(radon_next_step_clbk)
        self.show_steps_iradon_var = tk.IntVar()
        self._setup_iradon(iradon_next_step_clbk)

    def _setup_menu_bar(self, input_image_select_clbk, dicom_save_in_clbk, dicom_save_out_clbk, jpg_save):
        self.menu_bar = tk.Menu(master=self.master, tearoff=0)
        self.menu_bar.add_command(label='Otwórz plik', command=input_image_select_clbk)
        self.menu_bar.add_command(label=AS_DICOM_IN_TEXT, command=dicom_save_in_clbk, state='disabled')
        self.menu_bar.add_command(label=AS_IMG_TEXT, command=jpg_save, state='disabled')
        self.menu_bar.add_command(label=AS_DICOM_OUT_TEXT, command=dicom_save_out_clbk, state='disabled')

        self.master.config(menu=self.menu_bar)

    def _setup_input_data_view(self):
        self.input_data_frame = tk.LabelFrame(master=self.master, text='Dane wejściowe')
        self.input_image = tk.Canvas(master=self.input_data_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

        self.input_data_frame.grid(row=0, column=0, sticky=tk.N + tk.W, pady=0, ipadx=0)
        self.input_image.pack()

    def _setup_dicom_ui(self, dicom_edit_clbk):
        self.dicom_edit_frame = tk.LabelFrame(master=self.input_data_frame, text='Edytuj DICOM')
        # self.study_id_label = tk.Label(master=self.dicom_edit_frame, text='ID badania')
        # self.study_id_field = tk.Entry(master=self.dicom_edit_frame)
        # self.series_number_label = tk.Label(master=self.dicom_edit_frame, text='Numer seryjny')
        # self.series_number_field = tk.Entry(master=self.dicom_edit_frame)
        # self.accession_number_label = tk.Label(master=self.dicom_edit_frame, text='Numer katalogowy')
        # self.accession_number_field = tk.Entry(master=self.dicom_edit_frame)
        self.study_date_label = tk.Label(master=self.dicom_edit_frame, text='Data badania')
        self.study_date_field = tk.Entry(master=self.dicom_edit_frame)
        self.study_time_label = tk.Label(master=self.dicom_edit_frame, text='Godzina badania')
        self.study_time_field = tk.Entry(master=self.dicom_edit_frame)
        # self.referring_phycisian_label = tk.Label(master=self.dicom_edit_frame, text='Lekarz zlecający')
        # self.referring_phycisian_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_id_label = tk.Label(master=self.dicom_edit_frame, text='ID pacjenta')
        self.patient_id_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_name_label = tk.Label(master=self.dicom_edit_frame, text='Imię pacjenta')
        self.patient_name_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_surname_label = tk.Label(master=self.dicom_edit_frame, text='Nazwisko pacjenta')
        self.patient_surname_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_sex_label = tk.Label(master=self.dicom_edit_frame, text='Płeć pacjenta')
        self.patient_sex_field = ttk.Combobox(master=self.dicom_edit_frame, values=('Nieznana', 'Kobieta', 'Mężczyzna'))
        self.patient_sex_field.set('Nieznana')
        self.patient_birthday_label = tk.Label(master=self.dicom_edit_frame, text='Data urodzenia pacjenta')
        self.patient_birthday_field = tk.Entry(master=self.dicom_edit_frame)
        # self.patient_orientation_label = tk.Label(master=self.dicom_edit_frame, text='Położenie pacjenta')
        # self.patient_orientation_field = tk.Entry(master=self.dicom_edit_frame)
        self.comment_label = tk.Label(master=self.dicom_edit_frame, text='Komentarz')
        self.comment_field = tk.Entry(master=self.dicom_edit_frame)
        self.dicom_confirm_btn = tk.Button(master=self.dicom_edit_frame, text='Zatwierdź',
                                           command=dicom_edit_clbk, state='disabled')
        self.error_msgbox = tk.Message(master=self.dicom_edit_frame, textvar=self.error_msg_var, width=200)

        self.dicom_edit_frame.pack()
        # self.study_id_label.grid(row=0, column=0, sticky=tk.W)
        # self.study_id_field.grid(row=0, column=1)
        # self.series_number_label.grid(row=1, column=0, sticky=tk.W)
        # self.series_number_field.grid(row=1, column=1)
        # self.accession_number_label.grid(row=2, column=0, sticky=tk.W)
        # self.accession_number_field.grid(row=2, column=1)
        self.study_date_label.grid(row=3, column=0, sticky=tk.W)
        self.study_date_field.grid(row=3, column=1)
        self.study_time_label.grid(row=4, column=0, sticky=tk.W)
        self.study_time_field.grid(row=4, column=1)
        # self.referring_phycisian_label.grid(row=5, column=0, sticky=tk.W)
        # self.referring_phycisian_field.grid(row=5, column=1)
        self.patient_id_label.grid(row=6, column=0, sticky=tk.W)
        self.patient_id_field.grid(row=6, column=1)
        self.patient_name_label.grid(row=7, column=0, sticky=tk.W)
        self.patient_name_field.grid(row=7, column=1)
        self.patient_surname_label.grid(row=8, column=0, sticky=tk.W)
        self.patient_surname_field.grid(row=8, column=1)
        self.patient_sex_label.grid(row=9, column=0, sticky=tk.W)
        self.patient_sex_field.grid(row=9, column=1)
        self.patient_birthday_label.grid(row=10, column=0, sticky=tk.W)
        self.patient_birthday_field.grid(row=10, column=1)
        # self.patient_orientation_label.grid(row=10, column=0, sticky=tk.W)
        # self.patient_orientation_field.grid(row=10, column=1)
        self.comment_label.grid(row=11, column=0, sticky=tk.W)
        self.comment_field.grid(row=11, column=1)
        self.error_msgbox.grid(row=12, column=0, sticky=tk.W)
        self.dicom_confirm_btn.grid(row=13, column=0)

    def dicom_load_current_values(self, data):
        """Get values from the data set stored in self.dataset"""
        self.study_date_field.delete(0, tk.END)
        self.study_time_field.delete(0, tk.END)
        self.patient_id_field.delete(0, tk.END)
        self.patient_name_field.delete(0, tk.END)
        self.patient_surname_field.delete(0, tk.END)
        self.patient_sex_field.set('Nieznana')
        self.patient_birthday_field.delete(0, tk.END)
        self.comment_field.delete(0, tk.END)

        self.study_date_field.insert(0, data.get('StudyDate'))
        self.study_time_field.insert(0, data.get('StudyTime'))  # TODO: Add placeholders
        self.patient_id_field.insert(0, data.get('PatientID'))
        self.patient_name_field.insert(0, data.get('PatientGivenName'))
        self.patient_surname_field.insert(0, data.get('PatientFamilyName'))
        patient_sex = data.get('PatientSex')
        if patient_sex != '':
            self.patient_sex_field.set(patient_sex)
        self.patient_birthday_field.insert(0, data.get('PatientBirthDate'))
        self.comment_field.insert(0, data.get('ImageComments'))

    def get_dicom_fields_content(self):
        return {'StudyDate': self.study_date_field.get(),
                'StudyTime': self.study_time_field.get(),
                'PatientID': self.patient_id_field.get(),
                'PatientGivenName': self.patient_name_field.get(),
                'PatientFamilyName': self.patient_surname_field.get(),
                'PatientSex': self.patient_sex_field.get(),
                'PatientBirthDate': self.patient_birthday_field.get(),
                'ImageComments': self.comment_field.get()}

    def _setup_simulation_options(self, sim_options_confirm_clbk):
        self.settings_frame = tk.LabelFrame(master=self.input_data_frame, text='Ustawienia skanera')
        # Delta alpha step
        self.delta_alpha_step_label = tk.Label(master=self.settings_frame, text='Krok Δα układu emiter/detektor')
        self.delta_alpha_step = tk.Scale(master=self.settings_frame, from_=DELTA_ALPHA_STEP_MIN,
                                         to=DELTA_ALPHA_STEP_MAX, resolution=DELTA_ALPHA_STEP_INCREMENT,
                                         orient=tk.HORIZONTAL)
        self.delta_alpha_step.set(DELTA_ALPHA_STEP_DEFAULT)
        # Number of detectors (n)
        self.number_of_detectors_label = tk.Label(master=self.settings_frame, text='Liczba detektorów (n)')
        self.number_of_detectors = tk.Scale(master=self.settings_frame, from_=NUMBER_OF_DETECTORS_MIN,
                                            to=NUMBER_OF_DETECTORS_MAX, resolution=NUMBER_OF_DETECTORS_INCREMENT,
                                            orient=tk.HORIZONTAL)
        self.number_of_detectors.set(NUMBER_OF_DETECTORS_DEFAULT)
        # Emitter / detector spread (l)
        self.detectors_spread_label = tk.Label(master=self.settings_frame,
                                               text='Rozwartość / rozpiętość układu emiter/detektor (l)')
        self.detectors_spread = tk.Scale(master=self.settings_frame, from_=SPREAD_MIN, to=SPREAD_MAX,
                                         resolution=SPREAD_INCREMENT, orient=tk.HORIZONTAL)
        self.detectors_spread.set(SPREAD_DEFAULT)
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
        # self.enable_filtering = tk.Checkbutton(master=self.iradon_frame, text='Włącz filtr',
        #                                        variable=self.enable_filtering_var)
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
        # self.enable_filtering.pack()
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
            btn = self.dicom_confirm_btn
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

    def toggle_menu_entry(self, name, state):
        if state:
            self.menu_bar.entryconfig(name, state='normal')
        else:
            self.menu_bar.entryconfig(name, state='disabled')

    def toggle_save_jpg_menu(self, state):
        self.toggle_menu_entry(AS_IMG_TEXT, state)

    def toggle_save_dicom_out_menu(self, state):
        self.toggle_menu_entry(AS_DICOM_OUT_TEXT, state)

    def toggle_save_dicom_in_menu(self, state):
        self.toggle_menu_entry(AS_DICOM_IN_TEXT, state)


def test():
    pass


if __name__ == '__main__':
    test()
