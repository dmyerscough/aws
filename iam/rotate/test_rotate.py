#!/usr/bin/env python

import logging
import mock
import os
import tempfile
import unittest

from rotate import main


class TestIamRotation(unittest.TestCase):

    def setUp(self):
        """

        """
        self.tempfile = tempfile.mktemp()

        logging.disable(logging.CRITICAL)

        with open(self.tempfile, "w") as config_fh:
            config_fh.write(
                "[default]\naws_secret_access_key = abc123\naws_access_key_id = ABC123\n"
            )

    def tearDown(self):
        """

        """
        os.unlink(self.tempfile)

    @mock.patch('rotate.boto3.client')
    def test_main(self, mock_boto3):
        """
        Test successful rotation
        """
        mock_client = mock.MagicMock()
        mock_client.create_access_key.return_value = {
            'AccessKey': {
                'UserName': 'damian.myerscough',
                'AccessKeyId': 'ABCDEF',
                'Status': 'Active',
                'SecretAccessKey': 'abcdef',
            }
        }
        mock_client.delete_access_key.return_value = {}

        mock_boto3.return_value = mock_client

        self.assertEqual(
            main("damian.myerscough", "default", self.tempfile),
            0
        )

        mock_boto3.assert_called_once_with(
            'iam', aws_access_key_id='ABC123', aws_secret_access_key='abc123'
        )

        mock_client.create_access_key.assert_called_once_with(
            UserName='damian.myerscough'
        )

        mock_client.delete_access_key.assert_called_once_with(
            UserName='damian.myerscough', AccessKeyId='ABC123'
        )

    def test_main_invalid_credential_path(self):
        """
        Test reading an invalid credentials path
        """
        self.assertEqual(
            main("damian.myerscough", "default", "/tmp/this/does/not/exist"),
            1
        )
