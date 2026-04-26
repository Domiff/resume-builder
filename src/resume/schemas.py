from ninja import ModelSchema, Schema
from pydantic import EmailStr, ConfigDict

from resume.models import Resume


# class ResumeSchema(ModelSchema):
#     class Meta:
#         model = Resume
#         exclude = "id",
        
class ResumeSchemaD(Schema):
    title: str = None
    phone_number: str = None
    email: EmailStr = None
    experience: str = None
    education: str = None


class ResumeSchemaR(Schema):
    id: int
    title: str
    phone_number: str
    email: EmailStr
    experience: str
    education: str
