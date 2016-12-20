from setuptools import setup, find_packages

setup(
        name="HomeAutomation",
        version="0.2",
        packages=find_packages(),
        install_requires=['RPi.GPIO>=0.6.2', 'bottle>=0.12.9','Beaker>=1.8.1','bottle-beaker>=0.1.3','bottle-cork>=0.12.0'],
        author="DanielDelchev",
        author_email="isildur@mordor.rings",
        description="HomeAutomation",
        license="MIT",
        keywords="HomeAutomation",
        url="https://github.com/DanielDelchev/HomeAutomation"
)