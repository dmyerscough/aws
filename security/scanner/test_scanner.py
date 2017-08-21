
"""
Unit Tests for GitHub Scanner
"""

import logging
import mock
import tempfile
import unittest

from scanner import GitHubScanner


class TestScanner(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @mock.patch('scanner.GitHubScanner._query')
    def test_get_repo_etag(self, mock_query):
        """
        Test getting a repositories ETag
        """
        mock_query.return_value = {"etag": "3fb0a590a1a7f028ad3ada92b03bfa03", "response": {}}

        scanner = GitHubScanner()

        self.assertEqual(
            scanner.get_repo_etag("https://github.com/example.git"),
            "3fb0a590a1a7f028ad3ada92b03bfa03"
        )

    @unittest.skip("Not Implemented")
    def test_get_repo_etag_invalid_repo(self):
        pass

    @mock.patch('scanner.GitHubScanner._query')
    def test_get_user_repos(self, mock_query):
        """
        Test getting all repositories for a specific user
        """
        mock_query.return_value = {
            "etag": "3fb0a590a1a7f028ad3ada92b03bfa03",
            "response":
                [
                  {
                    "id": 12345678,
                    "name": "example1",
                    "full_name": "dmyerscough/example1",
                    "url": "https://api.github.com/repos/dmyerscough/example1",
                    "clone_url": "https://github.com/dmyerscough/example1.git",
                  },
                  {
                    "id": 12345679,
                    "name": "example2",
                    "full_name": "dmyerscough/example2",
                    "url": "https://api.github.com/repos/dmyerscough/example2",
                    "clone_url": "https://github.com/dmyerscough/example2.git",
                  }
                ]
        }

        scanner = GitHubScanner()

        self.assertEqual(
            scanner.get_user_repos("dmyerscough"),
            {
                "etag": "3fb0a590a1a7f028ad3ada92b03bfa03",
                "repos": {
                    "https://api.github.com/repos/dmyerscough/example1": "https://github.com/dmyerscough/example1.git",
                    "https://api.github.com/repos/dmyerscough/example2": "https://github.com/dmyerscough/example2.git"
                }
            }
        )

        mock_query.assert_called_once_with(
            'https://api.github.com/users/dmyerscough/repos', etag=None
        )

    @unittest.skip("Not Implemented")
    def test_get_user_repos_invalid_repo(self):
        pass

    @mock.patch('scanner.Repo')
    @mock.patch('scanner.tempfile.mkdtemp')
    def test_clone_user_repo(self, mock_tmpfile, mock_repo):
        """
        Test cloning a users repository
        """
        mock_tmpfile.return_value = '/tmp/tmpA8btyP'
        mock_repo.return_value = True

        scanner = GitHubScanner()

        self.assertEqual(
            scanner.clone_user_repo("https://github.com/dmyerscough/example1"),
            True
        )

        mock_repo.clone_from.assert_called_once_with(
            'https://github.com/dmyerscough/example1', '/tmp/tmpA8btyP'
        )

    @unittest.skip("Not Implemented")
    def test_clone_user_repo_failure(self):
        pass

    @mock.patch('scanner.GitHubScanner.clone_user_repo')
    @mock.patch('scanner.Repo')
    def test_inspect_commit(self, mock_repo, mock_clone_user_repo):
        """
        Test inspecting a repositories commits
        """
        mock_commit_prop = mock.PropertyMock(return_value="abff1262a6542963263a2cb30cab271b50556683")

        commit = mock.MagicMock()
        type(commit).hexsha = mock_commit_prop

        mock_commit = mock.MagicMock()
        mock_commit.iter_commits.return_value = iter([commit])

        mock_commit.git.show.return_value = ('''
        commit b10e08e5a9e51d1c9b1c2d11783f9c5b893aaebc
        Author: Michael Dowling <mtdowling@gmail.com>
        Date:   Mon Jun 26 16:15:16 2017 -0700

        Trim \n before testing if pattern is empty

        diff --git a/git-secrets b/git-secrets
        index 667219a..9c70c85 100755
        --- a/git-secrets
        +++ b/git-secrets
        @@ -49,10 +49,13 @@ load_patterns() {
           git config --get-all secrets.patterns
           # Execute each provider and use their output to build up patterns
           git config --get-all secrets.providers | while read -r cmd; do
        -    local result="$(export IFS=$'\n\t '; $cmd)"
        +    # Only split words on '\n\t ' and strip "\r" from the output to account
        +    # for carriage returns being added on Windows systems. Note that this
        +    # trimming is done before the test to ensure that the string is not empty.
        +    local result="$(export IFS=$'\n\t '; $cmd | tr -d $'\r')"
             # Do not add empty lines from providers as that would match everything.
             if [ -n "${result}" ]; then
        -      echo "$result" | tr -d "\r"
        +      echo "${result}"
             fi
           done
         }

        ''')

        mock_repo.return_value = mock_commit

        scanner = GitHubScanner()
        scanner.local_repos['https://www.github.com/dmyerscough/example1'] = tempfile.mkdtemp()

        self.assertEqual(
            scanner.inspect_commit("https://www.github.com/dmyerscough/example1"),
            {}
        )

        mock_commit.git.show.assert_called_once_with(
            "abff1262a6542963263a2cb30cab271b50556683"
        )

        self.assertTrue(mock_commit.iter_commits.assert_called_once)

    @mock.patch('scanner.GitHubScanner.clone_user_repo')
    @mock.patch('scanner.Repo')
    def test_inspect_commit_with_secret(self, mock_repo, mock_clone_user_repo):
        """
        Test inspecting a commit with a secret
        """
        self.maxDiff = None
        mock_commit_prop = mock.PropertyMock(return_value="c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc")
        mock_commit_name_prop = mock.PropertyMock(return_value="Damian Myerscough")
        mock_commit_email_prop = mock.PropertyMock(return_value="damian@example.com")
        mock_commit_committed_date_prop = mock.PropertyMock(return_value=0000000000)

        commit = mock.MagicMock()

        type(commit).hexsha = mock_commit_prop
        type(commit.committer).name = mock_commit_name_prop
        type(commit.committer).email = mock_commit_email_prop
        type(commit.author).name = mock_commit_name_prop
        type(commit).committed_date = mock_commit_committed_date_prop

        mock_commit = mock.MagicMock()
        mock_commit.iter_commits.return_value = iter([commit])

        mock_commit.git.show.return_value = ('''
                commit c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc
                Author: Michael Wittig <post@michaelwittig.info>
                Date:   Thu Apr 21 09:02:59 2016 +0200

                    exclude binary files from git grep

                diff --git a/.gitallowed b/.gitallowed
                new file mode 100644
                index 0000000..9cffac0
                --- /dev/null
                +++ b/.gitallowed
                @@ -0,0 +1,2 @@
                +AKIAIOSFODNN7EXAMPLE
                +4b825dc642cb6eb9a060e54bf8d69288fbee4904
                diff --git a/git-secrets b/git-secrets
                index f0d1ad1..4fe28cd 100755
                --- a/git-secrets
                +++ b/git-secrets
                @@ -106,7 +106,7 @@ git_grep() {
                   local options="$1"; shift
                   local files=$@ combined_patterns=$(load_combined_patterns)
                   [ -z "${combined_patterns}" ] && return 1
                -  GREP_OPTIONS= LC_ALL=C git grep -nwHE ${options} "${combined_patterns}" $@
                +  GREP_OPTIONS= LC_ALL=C git grep -nwHEI ${options} "${combined_patterns}" $@
                 }

                 # Performs a regular grep, taking into account patterns and recursion.

                ''')

        mock_repo.return_value = mock_commit

        scanner = GitHubScanner()
        scanner.local_repos['https://www.github.com/dmyerscough/example1.git'] = tempfile.mkdtemp()

        self.assertEqual(
            scanner.inspect_commit("https://www.github.com/dmyerscough/example1.git"),
            {'c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc': [{
                'secret': 'AKIAIOSFODNN7EXAMPLE',
                'committer': {'email': 'damian@example.com',
                              'name': 'Damian Myerscough'},
                'author': 'Damian Myerscough', 'filename': '.gitallowed',
                'url': 'https://www.github.com/dmyerscough/example1/commit/c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc',
                'date': 'Wed Dec 31 16:00:00 1969'
            }]}

        )

        mock_commit.git.show.assert_called_once_with(
            "c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc"
        )

        self.assertTrue(mock_commit.iter_commits.assert_called_once)

    @mock.patch('scanner.GitHubScanner.clone_user_repo')
    @mock.patch('scanner.Repo')
    def test_inspect_commit_with_last_commit(self, mock_repo, mock_clone_user_repo):
        """
        Test inspecting a commit with commit sha supplied
        """
        mock_commit_prop = mock.PropertyMock(return_value="c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc")

        commit = mock.MagicMock()
        type(commit).hexsha = mock_commit_prop

        mock_commit = mock.MagicMock()
        mock_commit.iter_commits.return_value = iter([commit])

        mock_commit.git.show.return_value = ('''
                commit c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc
                Author: Michael Wittig <post@michaelwittig.info>
                Date:   Thu Apr 21 09:02:59 2016 +0200

                    exclude binary files from git grep

                diff --git a/.gitallowed b/.gitallowed
                new file mode 100644
                index 0000000..9cffac0
                --- /dev/null
                +++ b/.gitallowed
                @@ -0,0 +1,2 @@
                +AKIAIOSFODNN7EXAMPLE
                +4b825dc642cb6eb9a060e54bf8d69288fbee4904
                diff --git a/git-secrets b/git-secrets
                index f0d1ad1..4fe28cd 100755
                --- a/git-secrets
                +++ b/git-secrets
                @@ -106,7 +106,7 @@ git_grep() {
                   local options="$1"; shift
                   local files=$@ combined_patterns=$(load_combined_patterns)
                   [ -z "${combined_patterns}" ] && return 1
                -  GREP_OPTIONS= LC_ALL=C git grep -nwHE ${options} "${combined_patterns}" $@
                +  GREP_OPTIONS= LC_ALL=C git grep -nwHEI ${options} "${combined_patterns}" $@
                 }

                 # Performs a regular grep, taking into account patterns and recursion.

                ''')

        mock_repo.return_value = mock_commit

        scanner = GitHubScanner()
        scanner.local_repos['https://www.github.com/dmyerscough/example1'] = tempfile.mkdtemp()

        self.assertEqual(
            scanner.inspect_commit(
                "https://www.github.com/dmyerscough/example1", "c769c5d2e0486b5162daf0cd7d7ad76e1cbd4adc"
            ),
            {}
        )

        self.assertFalse(mock_commit.called)
        self.assertTrue(mock_commit.iter_commits.called)

    @unittest.skip("Not Implemented")
    def test_inspect_commit_invalid_repo(self):
        pass

    @mock.patch('scanner.os.path.exists')
    @mock.patch('scanner.shutil.rmtree')
    def test_cleanup(self, mock_rmtree, mock_exists):
        """
        Test cleaning up repositories
        """
        mock_exists.return_value = True
        mock_rmtree.return_value = True

        scanner = GitHubScanner()
        scanner.local_repos['https://github.com/dmyerscough/example'] = '/tmp/abc123'

        self.assertTrue(scanner.cleanup())

        mock_rmtree.assert_called_once_with(
            "/tmp/abc123"
        )

    @mock.patch('scanner.requests')
    @mock.patch('scanner.GitHubScanner._ratelimit_status')
    def test_query(self, mock_ratelimit, mock_request):
        """
        Test GitHub query
        """
        mock_ratelimit.side_effect = [1, None]

        mock_resp = mock.MagicMock()
        type(mock_resp).status_code = mock.PropertyMock(return_value=200)
        type(mock_resp).headers = mock.PropertyMock(return_value={'ETag': 'W/"d554d09b351dddc7f2ac51b4859a44c4"'})
        mock_resp.json.return_value = {}

        mock_request.get.return_value = mock_resp

        scanner = GitHubScanner()
        self.assertEqual(
            scanner._query("https://github.com/dmyerscough/example"),
            {"etag": "d554d09b351dddc7f2ac51b4859a44c4", "response": {}},
        )

        self.assertEqual(
            mock_ratelimit.call_count,
            2
        )

        mock_request.get.assert_called_once_with(
            'https://github.com/dmyerscough/example', headers={'If-None-Match': ''}
        )

    @mock.patch('scanner.requests')
    @mock.patch('scanner.GitHubScanner._ratelimit_status')
    def test_query_pagination(self, mock_ratelimit, mock_request):
        """
        Test GitHub query with pagination
        """
        mock_ratelimit.return_value = None

        mock_resp_pagination = mock.MagicMock()
        mock_resp_non_pagination = mock.MagicMock()

        type(mock_resp_pagination).status_code = mock.PropertyMock(return_value=200)
        type(mock_resp_non_pagination).status_code = mock.PropertyMock(return_value=200)

        type(mock_resp_pagination).headers = mock.PropertyMock(
                    return_value={
                        'ETag': 'W/"d554d09b351dddc7f2ac51b4859a44c4"',
                        'Link': ('<https://api.github.com/user/repos?page=1&per_page=100>; '
                                 'rel="next", <https://api.github.com/user/repos?page=50&per_page=100>; rel="last"')
                    }
        )

        type(mock_resp_non_pagination).headers = mock.PropertyMock(
            return_value={
                'ETag': 'W/"d554d09b351dddc7f2ac51b4859a44c4"'
            }
        )

        mock_resp_pagination.json.return_value = []
        mock_resp_non_pagination.json.return_value = []

        mock_request.get.side_effect = [mock_resp_pagination, mock_resp_non_pagination]

        scanner = GitHubScanner()
        self.assertEqual(
            scanner._query("https://github.com/dmyerscough/example"),
            {"etag": "d554d09b351dddc7f2ac51b4859a44c4", "response": []},
        )

        self.assertEqual(
            mock_request.get.call_count,
            2
        )
        self.assertEqual(
            mock_ratelimit.call_count,
            2
        )

        mock_request.get.assert_has_calls([
            mock.call('https://github.com/dmyerscough/example', headers={'If-None-Match': ''}),
            mock.call('https://api.github.com/user/repos?page=1&per_page=100', headers={'If-None-Match': ''})
        ])

    @mock.patch('scanner.requests')
    @mock.patch('scanner.GitHubScanner._ratelimit_status')
    def test_query_cache(self, mock_ratelimit, mock_request):
        """
        Test GitHub query with caching
        """
        mock_ratelimit.side_effect = [1, None]

        mock_resp = mock.MagicMock()
        type(mock_resp).status_code = mock.PropertyMock(return_value=304)
        type(mock_resp).headers = mock.PropertyMock(return_value={'ETag': 'W/"d554d09b351dddc7f2ac51b4859a44c4"'})
        mock_resp.json.return_value = {}

        mock_request.get.return_value = mock_resp

        scanner = GitHubScanner()
        self.assertEqual(
            scanner._query("https://github.com/dmyerscough/example", etag="d554d09b351dddc7f2ac51b4859a44c4"),
            {"etag": "d554d09b351dddc7f2ac51b4859a44c4", "response": {}},
        )

        self.assertEqual(
            mock_ratelimit.call_count,
            2
        )

        mock_request.get.assert_called_once_with(
            'https://github.com/dmyerscough/example', headers={'If-None-Match': '"d554d09b351dddc7f2ac51b4859a44c4"'}
        )

    @unittest.skip("Not Implemented")
    def test_query_failured_request(self):
        """
        Test query failure
        """
        pass
