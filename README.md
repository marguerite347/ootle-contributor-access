# Ootle contribution access

Automatic enrollment closed on 2026-10-09 at the owner's instruction. Opening an issue no longer grants push access. Contribute through a fork and pull request to [Lobby](https://github.com/marguerite347/ootle-lobby-community) or [Workbench](https://github.com/marguerite347/ootle-workbench). The owner grants trusted collaborator access individually.

The product branches require passing checks and independent review, with owner approval for sensitive paths. Developers and agents cannot grant themselves authority or bypass these rules.

The invitation workflow is disabled, its automatic triggers and join form are removed, the repository variable and committed policy both disable enrollment, and its INVITER_TOKEN secret has been removed. Missing enablement configuration fails closed. Removing the stored secret disables this service's use of the credential; it does not claim to revoke the underlying GitHub credential globally. At closure both product repos listed only the owner as collaborator and no pending invitations.

The historical controller is retained for audit and tests. It is not an active request queue. Any future enrollment system requires an explicit new owner policy and an appropriately scoped credential.

Validation: `python3 -m unittest -v test_invite.py`; a direct `python3 invite.py` with the committed policy must exit without API calls. Selection receipt: reuse existing GitHub controls and controller stop behavior; no replacement invitation service.
