from setuptools import setup

setup(
    name='flake8-holvi',
    # TODO: Get it from flake8_holvi.py.
    version='0.1-dev',
    description='',
    long_description='',
    author='Berker Peksag',
    author_email='bpeksag@holvi.com',
    license='MIT',
    py_modules=['flake8_holvi'],
    zip_safe=False,
    entry_points={
        'flake8.extension': [
            'HLV = flake8_holvi:HolviChecker',
        ],
    },
)
