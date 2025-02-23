from setuptools import setup, find_packages

setup(
    name="hcentric_interface",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
        'pandas',
    ],
)