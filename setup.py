from setuptools import setup

setup(
    name="dicom_utils",
    version="0.1.0",
    packages=["dicom_utils"],
    install_requires=[
        "numpy",
        "pydicom",
    ],
)
