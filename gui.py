import tkinter as tk
import numpy as np
import PIL.Image
import PIL.ImageTk
import datetime
import time

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

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 300


class CTScannerGUI:
    def __init__(self, master, input_image_select_clbk, sim_options_confirm_clbk, radon_next_step_clbk,
                 iradon_next_step_clbk):
        self.master = master
        master.title('Symulator tomografu')
        # Create widgets
        self._setup_menu_bar(input_image_select_clbk)
        self._setup_input_data_view()
        self._setup_simulation_options(sim_options_confirm_clbk)
        self.show_steps_radon_var = tk.IntVar()
        self._setup_radon_steps(radon_next_step_clbk)
        self._setup_sinogram()
        self.show_steps_iradon_var = tk.IntVar()
        self._setup_iradon_steps(iradon_next_step_clbk)
        self._setup_reconstructed()
        self._setup_dicom_edit()

    def _setup_menu_bar(self, input_image_select_clbk):
        self.menu_bar = tk.Menu(master=self.master, tearoff=0)
        self.menu_bar.add_command(label='Otwórz plik', command=input_image_select_clbk)
        self.master.config(menu=self.menu_bar)

    def _setup_input_data_view(self):
        self.input_data_frame = tk.LabelFrame(master=self.master, text='Dane wejściowe')
        self.input_image = tk.Canvas(master=self.input_data_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.dicom_show_frame = tk.LabelFrame(master=self.input_data_frame, text='DICOM')
        self.dicom_show_list = tk.Listbox(master=self.dicom_show_frame, width=50)
        self.dicom_show_list_last_id = 1
        self.dicom_edit_btn = tk.Button(master=self.dicom_show_frame, text='Edytuj', command=None)
        self.input_data_frame.grid(row=0, column=0)
        self.input_image.pack()
        # self.dicom_show_frame.pack()
        self.dicom_show_list.pack()
        self.dicom_edit_btn.pack()

    def _setup_simulation_options(self, sim_options_confirm_clbk):
        self.settings_frame = tk.LabelFrame(master=self.master, text='Opcje')
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
                                         command=sim_options_confirm_clbk)

        self.options_image = tk.Canvas(master=self.settings_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.settings_frame.grid(row=1, column=0)
        self.delta_alpha_step_label.pack()
        self.delta_alpha_step.pack()
        self.number_of_detectors_label.pack()
        self.number_of_detectors.pack()
        self.detectors_spread_label.pack()
        self.detectors_spread.pack()
        self.options_confirm.pack()
        self.options_image.pack()

    def _setup_radon_steps(self, radon_next_step_clbk):
        self.radon_frame = tk.LabelFrame(master=self.master, text='Transformata Radona')
        self.show_steps_radon = tk.Checkbutton(master=self.radon_frame, text='Pokazuj kroki pośrednie',
                                               variable=self.show_steps_radon_var)
        self.simulation_step_image = tk.Canvas(master=self.radon_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.next_sim_step = tk.Button(master=self.radon_frame, text='Następny krok', command=radon_next_step_clbk)

        self.radon_frame.grid(row=0, column=1)
        self.show_steps_radon.pack()
        self.simulation_step_image.pack()
        self.next_sim_step.pack()

    def _setup_sinogram(self):
        self.sinogram_frame = tk.LabelFrame(master=self.master, text='Singoram')
        self.sinogram_image = tk.Canvas(master=self.sinogram_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

        self.sinogram_frame.grid(row=1, column=1)
        self.sinogram_image.pack()

    def _setup_iradon_steps(self, iradon_next_step_clbk):
        self.iradon_frame = tk.LabelFrame(master=self.master, text='Odwrotna transformata Radona')
        self.show_steps_iradon = tk.Checkbutton(master=self.iradon_frame, text='Pokazuj kroki pośrednie',
                                                variable=self.show_steps_iradon_var)
        self.next_reco_step = tk.Button(master=self.iradon_frame, text='Następny krok', command=iradon_next_step_clbk)

        self.iradon_frame.grid(row=0, column=2)
        self.show_steps_iradon.pack()
        self.next_reco_step.pack()

    def _setup_reconstructed(self):
        self.reco_frame = tk.LabelFrame(master=self.master, text='Odtworzony obraz')
        self.reco_image = tk.Canvas(master=self.reco_frame, width=2 * IMAGE_WIDTH, height=2 * IMAGE_HEIGHT)

        self.reco_frame.grid(row=1, column=2)
        self.reco_image.pack()

    def _setup_dicom_edit(self):
        self.dicom_edit_window = tk.Toplevel(master=self.master)

    def display_image(self, image_array, image_type):
        # PIL doesn't support floating point inputs
        if image_array.dtype == np.float64:
            image_array = (image_array * 255).astype(np.uint8)
        if image_type == 'input':
            canvas = self.input_image
        elif image_type == 'options':
            canvas = self.options_image
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

    def dicom_show_display_dataset(self, dataset):
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
            study_date = time.strptime(dataset.StudyDate, '%Y%m%d')
            study_date_formatted = time.strftime('%d-%m-%Y', study_date)
        except AttributeError:
            study_date_formatted = 'Brak'
        self._dicom_show_add_elem('Data badania', study_date_formatted)
        try:
            study_time = time.strptime(dataset.StudyTime, '%H%M%S.%f')
            study_time_formatted = time.strftime('%H:%M:%S', study_time)
        except AttributeError:
            study_time_formatted = 'Brak'
        self._dicom_show_add_elem('Godzina badania', study_time_formatted)
        try:
            referring_phycician = dataset.ReferringPhysicianName
        except AttributeError:
            referring_phycician = 'Brak'
        if referring_phycician == 'Unknown':
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
            patient_birthday = time.strptime(dataset.PatientBirthDate, '%Y%m%d')
            patient_birthday_formatted = time.strftime('%d-%m-%Y', patient_birthday)
        except AttributeError:
            patient_birthday_formatted = 'Brak'
        self._dicom_show_add_elem('Data ur. pacjenta', patient_birthday_formatted)
        try:
            patient_orientation = dataset.PatientOrientation
        except AttributeError:
            patient_orientation = 'Brak'
        self._dicom_show_add_elem('Położenie pacjenta', patient_orientation)
        # Adjust list height to fit all fields
        self.dicom_show_list.config(height=self.dicom_show_list_last_id-1)

    def _dicom_show_add_elem(self, name, value):
        entry = ': '.join([name, value])
        print(entry)
        self.dicom_show_list.insert(self.dicom_show_list_last_id, entry)

        self.dicom_show_list_last_id += 1

    def show_dicom_edit_window(self):
        self.dicom_edit_window.mainloop()


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
