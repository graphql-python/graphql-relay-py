"""graphql_relay.utils"""


def resolve_maybe_thunk(f):  # TODO: do we need that?
    return f() if callable(f) else f

