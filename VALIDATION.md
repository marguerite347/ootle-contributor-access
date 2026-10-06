# Enrollment validation — 2026-10-06

- Nine local and hosted tests passed: author identity, explicit request, path validation, fixed target/write grants, stop switch, existing members, pending invitations, duplicate requests and partial failure.
- [Hosted workflow run 37502848687](https://github.com/marguerite347/ootle-contributor-access/actions/runs/37502848687) completed successfully with the configured invitation credential.
- [Owner request #1](https://github.com/marguerite347/ootle-contributor-access/issues/1) was read from GitHub, processed automatically, answered with the correct existing-access status for both targets, and closed by the workflow. No new collaborator was invented for testing. Sending a new external invitation and recipient acceptance remain to be observed on the first external application.
- Opened the shared join URL in Chrome and verified the actual issue form displays the correct title, request checkbox, both-repository scope and acceptance instructions.
- The controller's only collaborator is its owner. The existing owner GitHub credential is stored as an Actions secret only in this controller. Its value is not committed, printed, or stored in the product repositories.
- `ENROLLMENT_OPEN=true`; `policy.json` enables invitations until the owner changes policy. The workflow is active, starts on opened/reopened issues, and retries open requests on its 15-minute schedule.
- Lobby `main`: no required status checks, pull-request reviews, or conversation-resolution gates. Ordinary direct pushes are permitted for collaborators. Force-push and branch-deletion safeguards remain.
- Workbench `ootle` and `feat/connected-agents` are unprotected. No added review gate.

## Published policy revisions

- `marguerite347/ootle-lobby-community`, `main`: `b241b9b36cf58eab6adf96a98934170893930521`.
- `marguerite347/ootle-workbench`, `ootle`: `aee5a7d7a0700422dde096f18cb52cbad3bd852c`.
- `marguerite347/ootle-workbench`, `feat/connected-agents`: `956f33c512411882693e9bc39bd81d99e4231906`.

These changes update repository access settings and contributor/agent instructions. They do not rebuild either product's browser application or grant hosting/wallet access.
