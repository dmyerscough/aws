#!/usr/bin/env python

"""
GitHub AWS Secret Scanner
"""

import argparse
import os
import re
import requests
import shutil
import tempfile
import time

from datetime import datetime

from git import Repo
from git.exc import GitCommandError

import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubScanner(object):

    def __init__(self):

        self.pagination_regex = re.compile(
            r'.*<(?P<next_page>https:\/\/api.github.com\/.+)>\;\srel="next"'
        )

        self.aws_regex = re.compile(
            r'(?:AWS)?_?(?:SECRET|ACCOUNT)?_?(?:ACCESS|ID)?_?(?:KEY)?(?:\s*)?(?::|=>|=)?(?:\s*)?(?:\"|\')?(?P<secret>AKIA[0-9A-Z]{16})(?:\"|\')?'
        )

        self.SLEEP_THRESHOLD = 5
        self.GITHUB_URL = "https://api.github.com"

        self.local_repos = {}

    def _query(self, url, etag=None, verify_ratelimit=True, content=None):
        """
        Query GitHub and handle pagination
        """
        headers = {
            "If-None-Match": '' if etag is None else '"{}"'.format(etag)
        }

        if verify_ratelimit:
            sleeptime = self._ratelimit_status()

            if sleeptime is not None:
                logger.info("Sleeping for {} seconds due to rate limit".format(sleeptime))
                time.sleep(sleeptime)
                return self._query(url=url, etag=etag)

        resp = requests.get("{url}".format(url=url), headers=headers)

        if resp.status_code == 304:
            logger.info("{} has no chances, skipping..".format(url))
            return {"etag": etag, "response": {}}
        elif resp.status_code != 200:
            return resp.reason  # Raise Exception

        pagination = self.pagination_regex.match(resp.headers.get('Link', ''))

        if pagination:
            return self._query(
                pagination.group('next_page'), content=resp.json() if content is None else content + resp.json()
            )

        return {"etag": resp.headers.get('ETag', '')[3:-1],
                "response": resp.json() if content is None else content + resp.json()}

    def _ratelimit_status(self):
        """
        Determine a recommended sleep time to avoid hitting Github's rate limit
        """
        recommend = None

        resp = self._query(
            "{github}/rate_limit".format(github=self.GITHUB_URL), verify_ratelimit=False
        )

        if resp['response']['rate']['remaining'] < self.SLEEP_THRESHOLD:
            recommend = datetime.utcfromtimestamp(resp['response']['rate']['reset']) - datetime.utcnow()
            logger.info("Recommending sleeping for {} due to rate limit".format(recommend))

        return round(recommend.total_seconds()) if getattr(recommend, "total_seconds", None) else None

    def get_repo_etag(self, repo_url):
        """
        Get a repositories ETag

        ETag determines if a repository has been modified
        """
        resp = self._query(
            "{repo_url}".format(repo_url=repo_url)
        )

        return resp['etag']

    def get_user_repos(self, username, etag=None):
        """
        Query a users public public repositories
        """
        logger.info("Querying {} GitHub public repositories".format(username))

        resp = self._query(
            "{github}/users/{username}/repos".format(github=self.GITHUB_URL, username=username),
            etag=etag,
        )

        return {
            "etag": resp['etag'],
            "repos": {repo['url']: repo['clone_url'] for repo in resp['response'] if 'clone_url' in repo}
        }

    def clone_user_repo(self, repo_url):
        """
        Clone a users repository
        """
        self.local_repos[repo_url] = tempfile.mkdtemp()

        try:
            logger.info("Cloning {}".format(repo_url))
            Repo.clone_from(repo_url, self.local_repos[repo_url])
        except GitCommandError as err:
            logger.info("Unable to clone {}: {}".format(repo_url, err))
            os.unlink(self.local_repos[repo_url])

            return False
        return True

    def inspect_commit(self, repo_url, last_commit=None):
        """
        Inspect diff for senstive information
        """
        suspicious = {}

        if not self.local_repos.get(repo_url):
            self.clone_user_repo(repo_url)

        repo = Repo(self.local_repos[repo_url])

        logger.info("Scanning repository")
        for commit in repo.iter_commits():
            if last_commit is not None and commit.hexsha == last_commit:
                break

            contents = repo.git.show(commit.hexsha)

            if 'diff --git ' not in contents:
                continue

            contents = filter(None, contents[contents.index("diff --git "):].split("diff --git "))

            for content in contents:
                content = content.splitlines()

                if '/' in content[0]:
                    filename = content[0].split()[0].split('/')[-1]
                else:
                    filename = content[0].split()[0]

                # Skip the content prior to line four as this is just git metadata
                secrets = self.aws_regex.search('\n'.join(content[4:]))

                if secrets:
                    logger.info("Secret Found")
                    if commit.hexsha not in suspicious:
                        suspicious[commit.hexsha] = []

                    suspicious[commit.hexsha].append({
                        "author": commit.author.name,
                        "committer": {"name": commit.committer.name, "email": commit.committer.email},
                        "date": datetime.fromtimestamp(commit.committed_date).strftime("%c"),
                        "url": "{}/commit/{}".format(repo_url[:-4], commit.hexsha),
                        "filename": filename,
                        "secret": secrets.group('secret'),
                    })

        return suspicious

    def cleanup(self):
        """
        Clean up any cloned repositories
        """
        logger.info("Cleaning up cloned repository")
        for repo in self.local_repos.values():
            if os.path.exists(repo):
                try:
                    shutil.rmtree(repo)
                except OSError:
                    pass

        return True


if __name__ == '__main__':

    from pprint import pprint

    requires_scanning = {}

    parser = argparse.ArgumentParser(description='GitHub AWS Secret Scanner')

    parser.add_argument(
        '-r',
        '--repo',
        dest="repo",
        help='GitHub Repository',
        required=True
    )

    args = parser.parse_args()

    scanner = GitHubScanner()

    scanner.clone_user_repo(args.repo)
    pprint(scanner.inspect_commit(args.repo))

    scanner.cleanup()
