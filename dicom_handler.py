import pydicom
import os
import numpy as np
from skimage import io
import tempfile
import datetime
from pydicom.dataset import Dataset, FileDataset


def dicom_list_files(path):
    dcm_files = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            if file[-4:].lower() == '.dcm':
                dcm_files[file] = os.path.join(root, file)
    return dcm_files


def dicom_load(path):
    ds = pydicom.dcmread(path)
    return ds, ds.pixel_array.astype(np.uint8)


def dicom_save():
    pass


def dicom_create_new(file_name, patient_name, patient_id):
    suffix = '.dcm'
    file_name = tempfile.NamedTemporaryFile(suffix=suffix).name
    # Set the required values
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.816.0.1.1680011.2.1322.1.11064548883040.3205072610123282805'
    file_meta.MediaStorageSOPInstanceUID = '1.2.3'
    file_meta.ImplementationClassUID = '7.4.3.5'
    ds = FileDataset(file_name, {}, file_meta=file_meta, preamble=b"\0"*128)
    ds.PatientName = patient_name
    ds.PatientID = patient_id

    ds.is_little_endian = True
    ds.is_implicit_VR = True
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    time_str = dt.strftime('%H%M%S.%f')
    ds.ContentTime = time_str
    ds.save_as(file_name)


def test():
    dcm_files = dicom_list_files('/home/piotr/studia_sem6/IWM/Tomograf/dicom_files')
    print(dcm_files)
    dicom_load(dcm_files['vhf.1501.dcm'])
    dicom_load(dcm_files['vhf.1505.dcm'])


if __name__ == '__main__':
    test()
