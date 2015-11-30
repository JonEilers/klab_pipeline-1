from setuptools import setup, find_packages

setup(name='kaboodle',
      version='0.1.0',
      description='Metagenome analysis tools',
      author='Connor McCoy <cmccoy@fhcrc.org>',
      packages=find_packages(),
      entry_points={'console_scripts':
                        ['kaboodle-search-recruit = kaboodle.scripts.recruit:main',
                         'kaboodle-recruit-nest = kaboodle.scripts.recruit_nest:main',
                         'kaboodle-search-analysis = kaboodle.scripts.analyze:main']},
      install_requires=['biopython', 'nestly'],
      )
