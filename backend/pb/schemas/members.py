from ninja import Schema

class MemberOut(Schema):
    """Member representation for the members modal."""
    username: str
    name: str
    role: str
    is_owner: bool
