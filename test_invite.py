import copy
import unittest
from invite import ApiError, CONSENT, CONTROL, TARGETS, TITLE, applicant, enroll, run


def request():
    return {'number': 1, 'state': 'open', 'title': TITLE, 'body': CONSENT,
            'user': {'login': 'new-builder', 'type': 'User'}}


class Fake:
    def __init__(self, issue=None, fail=None):
        self.issue = issue or request()
        self.fail = fail
        self.calls = []

    def call(self, method, path, data=None):
        self.calls.append((method, path, data))
        if path == self.fail:
            raise ApiError(403)
        if method == 'GET' and '/issues/' in path:
            return copy.deepcopy(self.issue)
        if method == 'GET':
            return {'permissions': {'admin': True}}
        if method == 'PUT':
            return {'id': 123, 'invitee': {'login': path.split('/')[-1]}}
        return None

    def pages(self, path):
        if '/issues?' in path:
            return [copy.deepcopy(self.issue)]
        return []


class EnrollmentTests(unittest.TestCase):
    def test_author_is_identity_and_body_cannot_nominate_someone_else(self):
        issue = request()
        issue['body'] += '\nUsername: somebody-else\nrepo: private-secret\n$(malicious command)'
        self.assertEqual(applicant(issue), 'new-builder')

    def test_requires_explicit_checked_request_and_exact_title(self):
        for change in [{'title': 'hello'}, {'body': ''}, {'body': CONSENT.replace('[x]', '[ ]')}, {'state': 'closed'}, {'pull_request': {}}]:
            issue = request(); issue.update(change)
            self.assertIsNone(applicant(issue))

    def test_unusable_identity_rejected(self):
        for login in ['../admin', 'name/other', 'a?permission=admin', '', '-bad', 'bad-', 'x\n']:
            issue = request(); issue['user']['login'] = login
            self.assertIsNone(applicant(issue))
        issue = request(); issue['user']['type'] = 'Bot'
        self.assertIsNone(applicant(issue))

    def test_only_fixed_repos_get_write_permission(self):
        queue, inviter = Fake(), Fake()
        self.assertEqual(run(queue, inviter, True, '1'), 0)
        writes = [call for call in inviter.calls if call[0] == 'PUT']
        self.assertEqual(writes, [('PUT', f'/repos/{repo}/collaborators/new-builder', {'permission': 'push'}) for repo in TARGETS])
        self.assertEqual(queue.calls[-1], ('PATCH', f'/repos/{CONTROL}/issues/1', {'state': 'closed', 'state_reason': 'completed'}))

    def test_closed_policy_makes_no_api_calls(self):
        queue, inviter = Fake(), Fake()
        self.assertEqual(run(queue, inviter, False, '1'), 0)
        self.assertEqual(queue.calls + inviter.calls, [])

    def test_existing_access_and_pending_invites_do_not_reinvite(self):
        inviter = Fake()
        state = {TARGETS[0]: ({'new-builder'}, set()), TARGETS[1]: (set(), {'new-builder'})}
        result = enroll(inviter, 'new-builder', state)
        self.assertEqual(inviter.calls, [])
        self.assertEqual(result[TARGETS[0]], 'already has push access')
        self.assertEqual(result[TARGETS[1]], 'invitation pending')

    def test_duplicate_requests_share_state(self):
        inviter = Fake(); state = {repo: (set(), set()) for repo in TARGETS}
        enroll(inviter, 'new-builder', state)
        enroll(inviter, 'new-builder', state)
        self.assertEqual(len(inviter.calls), 2)

    def test_partial_failure_leaves_request_open(self):
        queue = Fake(); inviter = Fake(fail=f'/repos/{TARGETS[1]}/collaborators/new-builder')
        self.assertEqual(run(queue, inviter, True, '1'), 1)
        self.assertFalse(any(call[0] in ('POST', 'PATCH') for call in queue.calls))

    def test_invalid_issue_number_never_becomes_api_path(self):
        with self.assertRaises(ValueError):
            run(Fake(), Fake(), True, '../1')


if __name__ == '__main__':
    unittest.main()
