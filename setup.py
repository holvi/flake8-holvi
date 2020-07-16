import io

from setuptools import setup

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flake8-holvi',
    version='0.5.1',
    description='flake8 plugin to help writing Pythonic code at Holvi',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Berker Peksag',
    author_email='bpeksag@holvi.com',
    url='https://github.com/holviberker/flake8-holvi',
    py_modules=['flake8_holvi'],
    packages=['holvi_lib2to3'],
    entry_points={
        'flake8.extension': [
            'HLV = flake8_holvi:HolviChecker',
        ],
    },
)
