from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        name="app.utils.count.count", 
        sources=["app/utils/count/count.pyx"]
    ),
    Extension(
        name="app.fractals.fractal",
        sources=["app/fractals/fractal.pyx"],
        include_dirs=[np.get_include()] 
    )
]

setup(
    ext_modules=cythonize(extensions, language_level="3")
)
