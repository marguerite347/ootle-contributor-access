# Join Ootle development

[**Join Lobby and Workbench**](https://github.com/marguerite347/ootle-contributor-access/issues/new?template=join.yml)

Anyone with a GitHub account can request push access to both:

- [Ootle Lobby](https://github.com/marguerite347/ootle-lobby-community), branch `main`.
- [Ootle Workbench](https://github.com/marguerite347/ootle-workbench), branch `ootle`.

Submit the form while signed in. The invitation workflow uses the issue author's verified GitHub identity, invites that account to both repos, and replies with acceptance links. Accept both invitations to activate write access. GitHub does not provide an account-independent invitation that can be accepted by everybody.

This is open enrollment with no individual approval until the owner changes the policy. Contributors and their agents can create branches, commit, push directly and merge changes. Agents use the contributor's own authorized GitHub account. Branch review and status checks are advisory during this phase; run relevant checks and report failures honestly. Force pushes and deletion of shared history are not part of normal development.

An agent can request access through the same form or GitHub CLI:

```sh
gh issue create --repo marguerite347/ootle-contributor-access \
  --title 'Join Lobby and Workbench' \
  --body '- [x] I request push access to both Ootle repositories.'
```

The issue-open event starts processing. A scheduled run retries open requests every 15 minutes; GitHub scheduling and API limits can delay it. GitHub currently limits personal-repository invitations to 50 per repository per 24 hours. Invitations still need recipient acceptance. Errors remain visible in Actions and the request stays open for retry.

## Owner controls

This controller repository is separate from the two open-write product repositories. Applicants get no write access here. The inviter credential is stored only as the `INVITER_TOKEN` Actions secret here; product repositories contain neither that credential nor privileged enrollment workflows. No contributor code is executed by the controller.

To stop new invitations, set the repository Actions variable `ENROLLMENT_OPEN` to `false`, or change `enrollment_open` in `policy.json` to `false`. Disabling enrollment leaves existing collaborators in place; revoke existing memberships separately when changing that policy. Re-enable by setting the variable to `true` and keeping `policy.json` enabled.

The controller uses an existing owner-authorized GitHub credential. It must be able to read collaborators/invitations and add collaborators to the two fixed targets. Future credential rotation can use a fine-grained token limited to those two repositories with Administration write and Metadata read, or a GitHub App with equivalent permissions. Never put the inviter credential into an open-write repository. The workflow's separate built-in `GITHUB_TOKEN` reads and replies to access requests in this controller.

Future review, branch, commit and access policies are established by updating each product repository's instructions and GitHub settings. These documents do not override GitHub account security or an agent host's permission controls. Hosting accounts and wallet permissions remain separate from GitHub push access.

## Validation and selection receipt

Reuse GitHub's authenticated issue forms, collaborator API, CLI and hosted Actions. The missing capability is a universal native invite: the small controller translates an authenticated join request into GitHub's per-account invitations. It never derives an identity or authority from untrusted free text. Unit tests cover consent/identity, fixed targets, duplicate invitations, failures and stopping enrollment. Hosted workflow execution is recorded separately from unit tests; a successful owner request does not demonstrate acceptance by an external account.

```sh
python3 -m unittest -v test_invite.py
```
