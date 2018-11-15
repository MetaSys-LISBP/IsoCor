import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Do not forget to update doc/conf.py version

setuptools.setup(
    name="IsoCor",
    version="2.0.3",
    author="Pierre Millard, Baudoin Delépine, Matthieu Guionnet",
    author_email="millard@insa-toulouse.fr",
    description="IsoCor: Isotope Correction for mass spectrometry labeling experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MetaSys-LISBP/IsoCor/",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires=['pandas>=0.17.1', 'scipy>=0.12.1'],
    package_data={'': ['data/*.dat', ], },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
    entry_points={
        'console_scripts': [
            'isocorcli = isocor.ui.isocorcli:start_cli',
        ],
        'gui_scripts': [
            'isocor = isocor.ui.isocorgui:start_gui',
        ]
    }
)
