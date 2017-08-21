# Scanner

This script will scan a GitHub repository for AWS secrets.

# Usage

```bash
$ ./scanner.py -r https://github.com/awslabs/git-secrets.git
2017-08-20 23:05:45,495 - __main__ - INFO - Cloning https://github.com/awslabs/git-secrets.git
2017-08-20 23:05:46,537 - __main__ - INFO - Scanning repository
2017-08-20 23:05:46,609 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,625 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,699 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,714 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,719 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,722 - __main__ - INFO - Secret Found
2017-08-20 23:05:46,739 - __main__ - INFO - Secret Found
{'016fc55b9eb4371b6164075f732ee205790be0d0': [{'author': 'Michael Dowling',
                                               'committer': {'email': 'mtdowling@gmail.com',
                                                             'name': 'Michael '
                                                                     'Dowling'},
                                               'date': 'Thu Dec 10 10:18:10 '
                                                       '2015',
                                               'filename': 'README.rst',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/016fc55b9eb4371b6164075f732ee205790be0d0'},
                                              {'author': 'Michael Dowling',
                                               'committer': {'email': 'mtdowling@gmail.com',
                                                             'name': 'Michael '
                                                                     'Dowling'},
                                               'date': 'Thu Dec 10 10:18:10 '
                                                       '2015',
                                               'filename': 'git-secrets',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/016fc55b9eb4371b6164075f732ee205790be0d0'},
                                              {'author': 'Michael Dowling',
                                               'committer': {'email': 'mtdowling@gmail.com',
                                                             'name': 'Michael '
                                                                     'Dowling'},
                                               'date': 'Thu Dec 10 10:18:10 '
                                                       '2015',
                                               'filename': 'git-secrets.1',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/016fc55b9eb4371b6164075f732ee205790be0d0'},
                                              {'author': 'Michael Dowling',
                                               'committer': {'email': 'mtdowling@gmail.com',
                                                             'name': 'Michael '
                                                                     'Dowling'},
                                               'date': 'Thu Dec 10 10:18:10 '
                                                       '2015',
                                               'filename': 'git-secrets.bats',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/016fc55b9eb4371b6164075f732ee205790be0d0'}],
 '7e8bdf4c13f6660e7774f33631095680d8a5de0b': [{'author': 'Michael Wittig',
                                               'committer': {'email': 'post@michaelwittig.info',
                                                             'name': 'Michael '
                                                                     'Wittig'},
                                               'date': 'Tue May  3 09:16:40 '
                                                       '2016',
                                               'filename': '.gitallowed',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/7e8bdf4c13f6660e7774f33631095680d8a5de0b'}],
 '84c348197b2d105168f133be7d6e1a1c75743f83': [{'author': 'Michael Dowling',
                                               'committer': {'email': 'mtdowling@gmail.com',
                                                             'name': 'Michael '
                                                                     'Dowling'},
                                               'date': 'Thu Dec 10 13:02:24 '
                                                       '2015',
                                               'filename': 'git-secrets.1',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/84c348197b2d105168f133be7d6e1a1c75743f83'}],
 'c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc': [{'author': 'Michael Wittig',
                                               'committer': {'email': 'post@michaelwittig.info',
                                                             'name': 'Michael '
                                                                     'Wittig'},
                                               'date': 'Thu Apr 21 00:02:59 '
                                                       '2016',
                                               'filename': '.gitallowed',
                                               'secret': 'AKIAIOSFODNN7EXAMPLE',
                                               'url': 'https://github.com/awslabs/git-secrets/commit/c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc'}]}
2017-08-20 23:05:46,749 - __main__ - INFO - Cleaning up cloned repository
```
