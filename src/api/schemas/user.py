from pydantic import BaseModel


class UserReportSchema(BaseModel):
    username: str
    report_id: int
