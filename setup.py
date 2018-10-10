import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isocor",
    version="2.0.0",
    author="Pierre Millard, Baudoin Delepine, Matthieu Guionnet",
    author_email="millard@insa-toulouse.fr",
    description="Correction of mass spectrometry data for natural abundance of isotopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MetaSys-LISBP/IsoCor/",
    packages=setuptools.find_packages(),
    install_requires=['pandas>=0.17.1', 'scipy>=0.12.1'],
    package_data={'': ['data/*.dat', ], },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
        ],
    entry_points={
        'console_scripts': [
            'isocorcli = isocor.ui.isoCorCli:startCli',
        ],
        'gui_scripts': [
            'isocor = isocor.ui.isoCorGUI:startGUI',
        ]
    }
)