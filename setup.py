import os
from setuptools import find_packages
from distutils.core import setup

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def main():
    with open(os.path.join(THIS_DIR, 'requirements.txt')) as reqs:
        requirements = reqs.read().strip().split('\n')

    setup(
        name="parsons",
        version='0.17.2',
        author="The Movement Cooperative",
        author_email="info@movementcooperative.org",
        url='https://github.com/movementcoop/parsons',
        keywords=['PROGRESSIVE', 'API', 'ETL'],
        packages=find_packages(),
        install_requires=requirements,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8'
        ]
    )


if __name__ == "__main__":
    main()
