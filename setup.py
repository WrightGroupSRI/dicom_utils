from setuptools import setup

with open("requirements.txt") as req_file:
    requirements = req_file.read().splitlines()

setup(
    name="dicom_utils",
    version="0.1.0",
    packages=["dicom_utils"],
    install_requires=requirements,
)
