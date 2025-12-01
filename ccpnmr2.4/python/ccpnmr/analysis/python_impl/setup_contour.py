"""
Setup script to compile Cython contour implementation.

Usage:
    python setup_contour.py build_ext --inplace
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        "contour_cython",
        ["contour_cython.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-march=native"],
    )
]

setup(
    name="contour_cython",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
    }),
)
