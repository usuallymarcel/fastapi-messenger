from pydantic import BaseModel

class FriendRequestSchema(BaseModel):
    friend_id: int