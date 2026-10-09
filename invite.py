"""Invite authenticated issue authors to the two fixed Ootle repositories."""
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

CONTROL = 'marguerite347/ootle-contributor-access'
TARGETS = ('marguerite347/ootle-lobby-community', 'marguerite347/ootle-workbench')
TITLE = 'Join Lobby and Workbench'
CONSENT = '- [x] I request push access to both Ootle repositories.'
LOGIN = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z')


class ApiError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__(f'GitHub API returned HTTP {status}')


class GitHub:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, data=None):
        if not path.startswith('/repos/'):
            raise ValueError('Only repository API paths are supported')
        request = urllib.request.Request(
            'https://api.github.com' + path,
            data=None if data is None else json.dumps(data).encode(),
            method=method,
            headers={'Authorization': f'Bearer {self.token}',
                     'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json',
                     'User-Agent': 'ootle-contributor-access'})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as error:
            # Do not include request headers, token, or arbitrary response bodies.
            raise ApiError(error.code) from None

    def pages(self, path):
        result = []
        for page in range(1, 101):
            separator = '&' if '?' in path else '?'
            items = self.call('GET', f'{path}{separator}per_page=100&page={page}')
            if not isinstance(items, list):
                raise ValueError('Expected a GitHub list')
            result.extend(items)
            if len(items) < 100:
                return result
        raise ValueError('Pagination limit reached; refusing a partial snapshot')


def applicant(issue):
    if issue.get('state') != 'open' or 'pull_request' in issue:
        return None
    if issue.get('title') != TITLE:
        return None
    if CONSENT not in (issue.get('body') or '').splitlines():
        return None
    user = issue.get('user') or {}
    login = user.get('login', '')
    if user.get('type') != 'User' or not isinstance(login, str) or not LOGIN.fullmatch(login):
        return None
    # Only GitHub's authenticated author identity is used. Never read usernames,
    # repositories, permissions, URLs or commands from issue text.
    return login


def enroll(inviter, login, state):
    results = {}
    for repo in TARGETS:
        members, pending = state[repo]
        identity = login.lower()
        if identity in members:
            results[repo] = 'already has push access'
        elif identity in pending:
            results[repo] = 'invitation pending'
        else:
            # Personal repositories grant collaborators write access. Never admin.
            invitation = inviter.call('PUT', f'/repos/{repo}/collaborators/{login}', {'permission': 'push'})
            if invitation is None:
                members.add(identity)
                results[repo] = 'already has push access'
            elif invitation.get('id') and (invitation.get('invitee') or {}).get('login', '').lower() == identity:
                pending.add(identity)
                results[repo] = 'invitation sent'
            else:
                raise ValueError('Unexpected invitation response; request remains open')
    return results


def run(queue, inviter, enabled, issue_number=None):
    if not enabled:
        print('Enrollment is closed. No permissions changed.')
        return 0
    if issue_number:
        if not str(issue_number).isdigit():
            raise ValueError('Issue number must be numeric')
        issues = [queue.call('GET', f'/repos/{CONTROL}/issues/{issue_number}')]
    else:
        issues = queue.pages(f'/repos/{CONTROL}/issues?state=open&sort=created&direction=asc')
    requests = [(issue, applicant(issue)) for issue in issues]
    requests = [(issue, login) for issue, login in requests if login]
    if not requests:
        print('No open enrollment requests.')
        return 0
    state = {}
    for repo in TARGETS:
        metadata = inviter.call('GET', f'/repos/{repo}')
        if not metadata.get('permissions', {}).get('admin'):
            raise ValueError(f'Invitation credential lacks administration access to {repo}')
        members = inviter.pages(f'/repos/{repo}/collaborators')
        invitations = inviter.pages(f'/repos/{repo}/invitations')
        state[repo] = (
            {member['login'].lower() for member in members if member.get('permissions', {}).get('push')},
            {item['invitee']['login'].lower() for item in invitations if item.get('invitee')})
    failures = 0
    for issue, login in requests:
        try:
            result = enroll(inviter, login, state)
            message = '\n'.join([
                f'@{login}, your request has been processed automatically.', '',
                *[f'- [{repo.split("/")[1]}](https://github.com/{repo}/invitations): {status}.' for repo, status in result.items()],
                '', 'Accept each pending GitHub invitation to activate push access. Collaborators and their agents must follow the current reviewed contribution policy.',
                '', 'This grants repository write access; your agent still needs your own GitHub authentication.'])
            queue.call('POST', f'/repos/{CONTROL}/issues/{issue["number"]}/comments', {'body': message})
            queue.call('PATCH', f'/repos/{CONTROL}/issues/{issue["number"]}', {'state': 'closed', 'state_reason': 'completed'})
            print(f'Processed request #{issue["number"]} for {login}')
        except (ApiError, ValueError, urllib.error.URLError) as error:
            failures += 1
            print(f'Request #{issue["number"]} remains open: {type(error).__name__}' + (f' HTTP {error.status}' if isinstance(error, ApiError) else ''))
    return 1 if failures else 0


if __name__ == '__main__':
    policy = json.loads(Path('policy.json').read_text())
    enabled = policy.get('enrollment_open') is True and os.environ.get('ENROLLMENT_OPEN', 'false').lower() == 'true'
    if enabled and (not os.environ.get('INVITER_TOKEN') or not os.environ.get('QUEUE_TOKEN')):
        raise SystemExit('Invitation credentials are not configured. No access has been granted.')
    try:
        raise SystemExit(run(GitHub(os.environ.get('QUEUE_TOKEN', '')), GitHub(os.environ.get('INVITER_TOKEN', '')), enabled, os.environ.get('ISSUE_NUMBER')))
    except (ApiError, ValueError, urllib.error.URLError) as error:
        raise SystemExit(f'Enrollment failed: {type(error).__name__}' + (f' HTTP {error.status}' if isinstance(error, ApiError) else '')) from None
