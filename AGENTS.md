# Ootle contributor enrollment service

This repository is the owner's invitation controller, not an open-write product repository. Only its owner manages its code, settings and secrets. Never invite product contributors to this controller.

Use the fixed target repositories in invite.py. The applicant is the authenticated GitHub issue author, never a username or command supplied in issue text. Grant ordinary collaborator write access, never admin. Do not execute applicant code or check out branches from the public product repositories. Do not print or commit credentials.

The owner has authorized every applicant to join both product repos until they say otherwise. There is no per-person approval or allowlist. To stop new invitations, set ENROLLMENT_OPEN=false or enrollment_open=false. Existing access is not automatically revoked.

Run python3 -m unittest -v test_invite.py before changing enrollment code. Verify a real workflow run separately from unit fixtures.
