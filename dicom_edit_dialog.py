import tkinter as tk
from tkinter import ttk
import time
from dicom_handler import dicom_date_dataset_to_display, dicom_time_dataset_to_display, dicom_time_display_to_dataset, \
    dicom_date_display_to_dataset

WINDOW_WIDTH = 200


class DicomEditDialog:
    def __init__(self, master, dataset):
        self.master = master
        self.dataset = dataset
        # TODO: Set name
        self.top = tk.Toplevel(master=master)
        self.error_msg_var = tk.StringVar()
        self._setup_ui()
        self._read_values_from_dataset()

    def _setup_ui(self):
        self.dicom_edit_frame = tk.LabelFrame(master=self.top, text='Edytuj DICOM')
        self.study_id_label = tk.Label(master=self.dicom_edit_frame, text='ID badania')
        self.study_id_field = tk.Entry(master=self.dicom_edit_frame)
        self.series_number_label = tk.Label(master=self.dicom_edit_frame, text='Numer seryjny')
        self.series_number_field = tk.Entry(master=self.dicom_edit_frame)
        self.accession_number_label = tk.Label(master=self.dicom_edit_frame, text='Numer katalogowy')
        self.accession_number_field = tk.Entry(master=self.dicom_edit_frame)
        self.study_date_label = tk.Label(master=self.dicom_edit_frame, text='Data badania')
        self.study_date_field = tk.Entry(master=self.dicom_edit_frame)
        self.study_time_label = tk.Label(master=self.dicom_edit_frame, text='Godzina badania')
        self.study_time_field = tk.Entry(master=self.dicom_edit_frame)
        self.referring_phycisian_label = tk.Label(master=self.dicom_edit_frame, text='Lekarz zlecający')
        self.referring_phycisian_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_id_label = tk.Label(master=self.dicom_edit_frame, text='ID pacjenta')
        self.patient_id_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_name_label = tk.Label(master=self.dicom_edit_frame, text='Dane osobowe pacjenta')
        self.patient_name_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_sex_label = tk.Label(master=self.dicom_edit_frame, text='Płeć pacjenta')
        self.patient_sex_field = ttk.Combobox(master=self.dicom_edit_frame, values=('Kobieta', 'Mężczyzna'))
        self.patient_sex_field.set('Kobieta')
        self.patient_birthday_label = tk.Label(master=self.dicom_edit_frame, text='Data urodzenia pacjenta')
        self.patient_birthday_field = tk.Entry(master=self.dicom_edit_frame)
        self.patient_orientation_label = tk.Label(master=self.dicom_edit_frame, text='Położenie pacjenta')
        self.patient_orientation_field = tk.Entry(master=self.dicom_edit_frame)
        self.comment_label = tk.Label(master=self.dicom_edit_frame, text='Komentarz')
        self.comment_field = tk.Entry(master=self.dicom_edit_frame)
        self.confirm_button = tk.Button(master=self.dicom_edit_frame, text='Zatwierdź', command=self._confirm)
        self.cancel_button = tk.Button(master=self.dicom_edit_frame, text='Anuluj', command=self._cancel)
        self.error_msgbox = tk.Message(master=self.dicom_edit_frame, textvar=self.error_msg_var, width=WINDOW_WIDTH)

        self.dicom_edit_frame.pack()
        self.study_id_label.grid(row=0, column=0, sticky=tk.W)
        self.study_id_field.grid(row=0, column=1)
        self.series_number_label.grid(row=1, column=0, sticky=tk.W)
        self.series_number_field.grid(row=1, column=1)
        self.accession_number_label.grid(row=2, column=0, sticky=tk.W)
        self.accession_number_field.grid(row=2, column=1)
        self.study_date_label.grid(row=3, column=0, sticky=tk.W)
        self.study_date_field.grid(row=3, column=1)
        self.study_time_label.grid(row=4, column=0, sticky=tk.W)
        self.study_time_field.grid(row=4, column=1)
        self.referring_phycisian_label.grid(row=5, column=0, sticky=tk.W)
        self.referring_phycisian_field.grid(row=5, column=1)
        self.patient_id_label.grid(row=6, column=0, sticky=tk.W)
        self.patient_id_field.grid(row=6, column=1)
        self.patient_name_label.grid(row=7, column=0, sticky=tk.W)
        self.patient_name_field.grid(row=7, column=1)
        self.patient_sex_label.grid(row=8, column=0, sticky=tk.W)
        self.patient_sex_field.grid(row=8, column=1)
        self.patient_birthday_label.grid(row=9, column=0, sticky=tk.W)
        self.patient_birthday_field.grid(row=9, column=1)
        self.patient_orientation_label.grid(row=10, column=0, sticky=tk.W)
        self.patient_orientation_field.grid(row=10, column=1)
        self.comment_label.grid(row=11, column=0, sticky=tk.W)
        self.comment_field.grid(row=11, column=1)
        self.error_msgbox.grid(row=12, column=0, sticky=tk.W)
        self.confirm_button.grid(row=13, column=0)
        self.cancel_button.grid(row=13, column=1)

    def _check_values(self):
        if not self._is_not_empty(self.study_id_field.get()):
            return False
        if not self._is_not_empty(self.series_number_field.get()):
            return False
        if not self._is_not_empty(self.accession_number_field.get()):
            return False
        if not self._is_date_correct(self.study_date_field.get()):
            return False
        if not self._is_time_correct(self.study_time_field.get()):
            return False
        if not self._is_not_empty(self.referring_phycisian_field.get()):
            return False
        if not self._is_not_empty(self.patient_id_field.get()):
            return False
        if not self._is_not_empty(self.patient_name_field.get()):
            return False
        if not self._is_date_correct(self.patient_birthday_field.get()):
            return False
        if not self._is_not_empty(self.patient_orientation_field.get()):
            return False
        return True

    def _read_values_from_dataset(self):
        """Get values from the data set stored in self.dataset"""
        try:
            self.study_id_field.insert(0, str(self.dataset.StudyID))
        except AttributeError:
            pass
        try:
            self.series_number_field.insert(0, str(self.dataset.SeriesNumber))
        except AttributeError:
            pass
        try:
            self.accession_number_field.insert(0, str(self.dataset.AccessionNumber))
        except AttributeError:
            pass
        try:
            self.study_date_field.insert(0, dicom_date_dataset_to_display(self.dataset.StudyDate))
        except AttributeError:
            pass
        try:
            self.study_time_field.insert(0, dicom_time_dataset_to_display(self.dataset.StudyTime))
        except AttributeError:
            pass
        try:
            self.referring_phycisian_field.insert(0, str(self.dataset.ReferringPhysicianName))
        except AttributeError:
            pass
        try:
            self.patient_id_field.insert(0, str(self.dataset.PatientID))
        except AttributeError:
            pass
        try:
            self.patient_name_field.insert(0, str(self.dataset.PatientName))
        except AttributeError:
            pass
        try:
            sex = self.dataset.PatientSex
            if sex == 'F':
                self.patient_sex_field.set('Kobieta')
            elif sex == 'M':
                self.patient_sex_field.set('Mężczyzna')
        except AttributeError:
            pass
        try:
            self.patient_birthday_field.insert(0, dicom_date_dataset_to_display(self.dataset.PatientBirthDate))
        except AttributeError:
            pass
        try:
            self.patient_orientation_field.insert(0, str(self.dataset.PatientOrientation))
        except AttributeError:
            pass
        try:
            print('TODO: Implement comments')  # TODO: Seriously, implement comments :)
        except AttributeError:
            pass

    def _write_values_to_dataset(self):
        self.dataset.StudyID = self.study_id_field.get()
        self.dataset.SeriesNumber = self.series_number_field.get()
        self.dataset.AccessionNumber = self.accession_number_field.get()
        self.dataset.StudyDate = dicom_date_display_to_dataset(self.study_date_field.get())
        self.dataset.StudyTime = dicom_time_display_to_dataset(self.study_time_field.get())
        self.dataset.ReferringPhysicianName = self.referring_phycisian_field.get()
        self.dataset.PatientID = self.patient_id_field.get()
        self.dataset.PatientName = self.patient_name_field.get()
        if self.patient_sex_field.get() == 'Kobieta':
            self.dataset.PatientSex = 'F'
        else:
            self.dataset.PatientSex = 'M'
        self.dataset.PatientBirthDate = dicom_date_display_to_dataset(self.patient_birthday_field.get())
        self.dataset.PatientOrientation = self.patient_orientation_field.get()
        # TODO: Add comment support

    def _is_date_correct(self, date):
        try:
            time.strptime(date, '%d-%m-%Y')
            return True
        except ValueError:
            self.error_msg_var.set('Błąd! Data musi mieć format dd-mm-yyyy')
            return False

    def _is_time_correct(self, t):
        try:
            time.strptime(t, '%H:%M:%S')
            return True
        except ValueError:
            self.error_msg_var.set('Błąd! Godzina musi mieć format gg:mm:ss')
            return False

    def _is_not_empty(self, value):
        if value != '':
            return True
        else:
            self.error_msg_var.set('Błąd! Proszę wypełnić wszystkie pola (z wyjątkiem komentarza)')
            return False

    def _confirm(self):
        if self._check_values():
            self._write_values_to_dataset()

    def _cancel(self):
        self.top.quit()


def test():
    from dicom_handler import dicom_load, dicom_list_files
    dcm_files = dicom_list_files('/home/piotr/studia_sem6/IWM/Tomograf/dicom_files')
    dataset, _ = dicom_load(dcm_files['vhf.1501.dcm'])
    # print(dataset)
    root = tk.Tk()
    dialog = DicomEditDialog(master=root, dataset=dataset)
    root.mainloop()

    # is_date_correct('01-02')


if __name__ == '__main__':
    test()
