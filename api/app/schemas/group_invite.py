from pydantic import BaseModel

class GroupInviteSchema(BaseModel):
    max_uses: int