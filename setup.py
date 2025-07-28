import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cavass",
    version="1.2.3",
    author="Dai Jian",
    author_email="daijian@stumail.ysu.edu.cn",
    description="CAVASS python APIs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires="~=3.11",
    install_requires=[
        "numpy >= 1.21.0",
        "scipy >= 1.7.3",
        "pydicom >= 2.4.3",
        "nibabel >= 4.0.1",
    ]
)
