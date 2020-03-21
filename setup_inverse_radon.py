from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('inverse_radon_cythonized.pyx', language_level=3))
