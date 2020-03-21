from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('tomograph_cythonized.pyx', language_level=3))
