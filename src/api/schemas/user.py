from pydantic import BaseModel


class UserReportSchema(BaseModel):
    username: str
