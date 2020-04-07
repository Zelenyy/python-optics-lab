#!/usr/bin/python

import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

NUMPY_MIN_VERSION = '1.8.2'
SCIPY_MIN_VERSION = '1.3.1'
PYQT_MIN_VERSION = '5.9.2'
MATPLOTLIB_MIN_VERSION = '3.1.1'
# PYTABLES_MIN_VERSION = '3.5.1'

setuptools.setup(
    name="mipt-npm-optics",
    version="0.0.1.dev4",
    author="Mikhail Zelenyi",
    author_email="mihail.zelenyy@phystech.edu",
    url='http://npm.mipt.ru/',
    description="Python scripts for optics lab",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="optics",
    packages=setuptools.find_packages(),
    entry_points = {
      "console_scripts" : [
          "mipt-optics = optics.main:main"
      ]
    },
    package_data = { "optics" : ["data/*.txt"]},
    include_package_data = True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    # project_urls={
    #     "Bug Tracker": "",
    #     "Documentation": "",
    #     "Source Code": "",
    # },
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        "pyqt5",
        "appdirs"
        # 'tables>={0}'.format(PYTABLES_MIN_VERSION),

    ]
    # test_suite='tests'
)
