""" setup module """
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="goodwe2pvoutput",
    version="0.0.6",
    author="James Hodgkinson",
    author_email="yaleman@ricetek.net",
    description="PVOutput.org Goodwe uploader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaleman/goodwe2pvoutput",
    packages=setuptools.find_packages(),
    install_requires=['pvoutput', 'pygoodwe', 'schedule'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    scripts=['goodwe2pvoutput/bin/goodwe2pvoutput']
)

