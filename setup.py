from setuptools import setup, find_packages

test_requirements = ['sentinels>=0.0.6', 'nose>=1.0', 'python-dateutil>=2.2']

setup(
    name = "youtube_utils",
    version = "0.0.1",
    packages = find_packages(),

    # Dependencies on other packages:
    setup_requires   = ['nose>=1.1.2'],
    tests_require    = test_requirements,
    install_requires = ['google-api-python-client>=1.5.1',
			'isodate>=0.5.4',
			] + test_requirements,

    # Unit tests; they are initiated via 'python setup.py test'
    #test_suite       = 'json_to_relation/test',
    test_suite       = 'nose.collector', 

    #data_files = [('pymysql_utils/data', datafiles)],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Andreas Paepcke",
    author_email = "paepcke@cs.stanford.edu",
    description = "Utilities for interacting with Google's YouTube API",
    license = "BSD",
    keywords = "youtube, google api",
    #url = "https://github.com/paepcke/youtube_utils",   # project home page, if any
)
