from setuptools import setup, Extension
import numpy as np

extension = Extension(
    'cextension',
    sources=['cextension.c', 'spectral_processing.c'],
    include_dirs=[np.get_include()],
    extra_compile_args=['-O2']
)

setup(
    name='ccpnmr-minimal-example',
    ext_modules=[extension],
    py_modules=['python_implementation'],
)
