"""Product-file validators. Each validator returns (ok: bool, errors: list[str]).

Called from PostToolUse(Edit/Write) dispatchers when a tracked artifact changes,
and again from gate checkers at stage-transition time.
"""
