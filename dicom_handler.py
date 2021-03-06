import tempfile
import time

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
import pydicom.uid


def dicom_date_dataset_to_display(date):
    return time.strftime('%d-%m-%Y', time.strptime(date, '%Y%m%d'))


def dicom_date_display_to_dataset(date):
    return time.strftime('%Y%m%d', time.strptime(date, '%d-%m-%Y'))


def dicom_time_dataset_to_display(t):
    return time.strftime('%H:%M:%S', time.strptime(t, '%H%M%S.%f'))


def dicom_time_display_to_dataset(t):
    return time.strftime('%H%M%S.0000', time.strptime(t, '%H:%M:%S'))


def dicom_load(path):
    ds = pydicom.dcmread(path)
    image = ds.pixel_array
    # Convert the image data type to uint8
    if image.dtype != np.uint8:
        img_max = np.max(image)
        img_min = np.min(image)
        image = 255 * (image - img_min) / (img_max - img_min)
    return ds, image.astype(np.uint8)


def dicom_create_new_dataset():
    suffix = '.dcm'
    file_name = tempfile.NamedTemporaryFile(suffix=suffix).name
    file_meta = Dataset()
    # Set the required values
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    file_meta.MediaStorageSOPInstanceUID = "1.3.6.1.4.1.5962.1.1.1.1.1.20040119072730.12322"
    file_meta.ImplementationClassUID = "1.3.6.1.4.1.5962.2"
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'
    ds = FileDataset(file_name, {}, file_meta=file_meta, preamble=b"\0" * 128)
    return ds


def dicom_save(file_name, dataset, image):
    """
    Saves a dataset to a .dcm file.
    This function checks whether the dataset contains a pixelarray field (an input image).
    If it doesn't the image parameter is used as one.
    """
    if image.dtype != np.uint8:
        img_max = np.max(image)
        img_min = np.min(image)
        image = ((image - img_min) / (img_max - img_min) * 255)
        image = image.astype(np.uint8)

    dataset.SpecificCharacterSet = 'utf-8'
    dataset.PixelData = image.tobytes()
    dataset.Rows, dataset.Columns = image.shape
    dataset.BitsStored = 8
    dataset.BitsAllocated = 8
    dataset.HighBit = 7
    dataset.SamplesPerPixel = 1
    dataset.PhotometricInterpretation = "MONOCHROME2"
    dataset.PixelRepresentation = 0
    dataset.save_as(file_name, write_like_original=False)


def dicom_read_dataset(dataset):
    """Get all interesting fields from the dataset and convert some fields to a more user friendly format"""
    data = {}
    if dataset.get('StudyDate'):
        data['StudyDate'] = dicom_date_dataset_to_display(dataset.get('StudyDate'))
    else:
        data['StudyDate'] = ''
    if dataset.get('StudyTime'):
        data['StudyTime'] = dicom_time_dataset_to_display(dataset.get('StudyTime'))
    else:
        data['StudyTime'] = ''
    data['PatientID'] = str(dataset.get('PatientID') or '')
    if dataset.get('PatientName'):
        patient_name = dataset.get('PatientName')
        try:
            data['PatientGivenName'] = patient_name.given_name
        except AttributeError:
            data['PatientGivenName'] = ''
        try:
            data['PatientFamilyName'] = patient_name.family_name
        except AttributeError:
            data['PatientFamilyName'] = ''
    else:
        data['PatientGivenName'] = ''
        data['PatientFamilyName'] = ''
    sex = dataset.get('PatientSex')
    if sex:
        if sex == 'F':
            data['PatientSex'] = 'Kobieta'
        elif sex == 'M':
            data['PatientSex'] = 'Mężczyzna'
    else:
        data['PatientSex'] = 'Nieznana'
    bday = dataset.get('PatientBirthDate')
    if bday:
        data['PatientBirthDate'] = dicom_date_dataset_to_display(bday)
    else:
        data['PatientBirthDate'] = ''
    data['ImageComments'] = dataset.get('ImageComments') or ''
    return data


def dicom_store_data(data, dataset):
    """Stores data from the data dictionary to a provided DICOM dataset.
    This function assumes that the provided data is correct and thus won't check it"""
    if data.get('StudyDate'):
        dataset.StudyDate = dicom_date_display_to_dataset(data.get('StudyDate'))
    if data.get('StudyTime'):
        dataset.StudyTime = dicom_time_display_to_dataset(data.get('StudyTime'))
    if data.get('PatientGivenName') or data.get('PatientFamilyName'):
        patient_given_name = data.get('PatientGivenName') or ''
        patient_family_name = data.get('PatientFamilyName') or ''
        dataset.PatientName = '^'.join((patient_family_name, patient_given_name))
    if data.get('PatientID'):
        dataset.PatientID = data.get('PatientID')
    if data.get('PatientSex'):
        if data.get('PatientSex') == 'Mężczyzna':
            dataset.PatientSex = 'M'
        elif data.get('PatientSex') == 'Kobieta':
            dataset.PatientSex = 'F'
    if data.get('PatientBirthDate'):
        dataset.PatientBirthDate = dicom_date_display_to_dataset(data.get('PatientBirthDate'))
    if data.get('ImageComments'):
        dataset.ImageComments = data.get('ImageComments')
    return dataset


def dicom_check_data(data):
    """Checks if data is correct"""
    if data.get('StudyDate') and data.get('StudyDate') != '':
        result, error_msg = _is_date_correct(data.get('StudyDate'))
        if not result:
            return False, error_msg
    if data.get('StudyTime') and data.get('StudyTime') != '':
        result, error_msg = _is_time_correct(data.get('StudyTime'))
        if not result:
            return False, error_msg
    if data.get('PatientBirthDate') and data.get('PatientBirthDate') != '':
        result, error_msg = _is_date_correct(data.get('PatientBirthDate'))
        if not result:
            return False, error_msg
    return True, ''


def _is_date_correct(date):
    try:
        time.strptime(date, '%d-%m-%Y')
        return True, ''
    except ValueError:
        return False, 'Błąd! Data musi mieć format dd-mm-yyyy'


def _is_time_correct(t):
    try:
        time.strptime(t, '%H:%M:%S')
        return True, ''
    except ValueError:
        return False, 'Błąd! Godzina musi mieć format gg:mm:ss'
