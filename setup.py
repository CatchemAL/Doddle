from setuptools import setup, find_packages

# Package meta-data.
NAME = "nerdle"
DESCRIPTION = "A nerd's approach to playing Wordle."
URL = r"https://github.com/CatchemAl/Nerdle"
EMAIL = "AlexJCross90@gmail.com"
AUTHOR = "Alex Cross"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.1"

REQUIRED = ['numba', 'numpy']

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=REQUIRED,  # external packages as dependencies
    entry_points={
        "console_scripts": [
            "nerdle = nerdle.cli:main",
        ],
    },
)
