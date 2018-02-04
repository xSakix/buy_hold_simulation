from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='buy and hold simulator',
    ext_modules=cythonize('bah_simulator.pyx'),
)