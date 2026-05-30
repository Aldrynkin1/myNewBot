from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="app.utils.count.count", 
        sources=["app/utils/count/count.pyx"]
    )
]

setup(
    ext_modules=cythonize(extensions, language_level="3")
)
