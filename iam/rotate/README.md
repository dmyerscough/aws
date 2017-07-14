# Rotate

This script will read your AWS secrets from the credential file (`~/.aws/credentials`) and rotate the keypair, replacing the old with the new.

# Usage

```bash
$ ./rotate.py -u damian.myerscough -p default
2017-07-14 15:34:57,923 - __main__ - INFO - Creating new credentials
2017-07-14 15:34:58,477 - __main__ - INFO - Deleting old credentials
2017-07-14 15:34:58,589 - __main__ - INFO - Writing new credentials
```
