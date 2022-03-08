import os
from setuptools import find_packages
from distutils.core import setup



def main():
    limited_deps = os.environ.get("PARSONS_LIMITED_DEPENDENCIES", "")
    if limited_deps.strip().upper() in ("1", "YES", "TRUE", "ON"):
        install_requires = [
            "petl",
            "python-dateutil",
            "requests",
            "simplejson",
        ]
        extras_require = {
            "google": [
                "google-cloud-bigquery",
                "google-cloud-storage",
                "gspread",
                "oauth2client",
            ],
            "ngpvan": [
                "suds-py3",
            ],
        }
        extras_require["all"] = sorted({
            lib
            for libs in extras_require.values()
            for lib in libs
        })
    else:
        THIS_DIR = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(THIS_DIR, 'requirements.txt')) as reqs:
            install_requires = reqs.read().strip().split('\n')
        extras_require = {}

    setup(
        name="parsons",
        version='0.18.1',
        author="The Movement Cooperative",
        author_email="info@movementcooperative.org",
        url='https://github.com/movementcoop/parsons',
        keywords=['PROGRESSIVE', 'API', 'ETL'],
        packages=find_packages(),
        install_requires=install_requires,
        extras_require=extras_require,
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
