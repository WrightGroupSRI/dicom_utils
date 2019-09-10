from setuptools import setup, find_packages

with open("requirements.txt") as req_file:
    requirements = req_file.read().splitlines()

setup(
    name="dicom_utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
)
