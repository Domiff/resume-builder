import uuid

from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from weasyprint import HTML

from core.s3 import s3
from resume.models import Resume
from resume.schemas import ResumeIn, ResumeOut
from resume.repository import Repository


resume_repository = Repository(Resume)


class ResumeBuilder:
    def __init__(self, context: ResumeIn):
        self.title = context.dict().get("title")
        self.phone_number = context.dict().get("phone_number")
        self.email = context.dict().get("email")
        self.experience = context.dict().get("experience")
        self.education = context.dict().get("education")

    def build(self):
        return render_to_string(
            "main.html",
            {
                "title": self.title,
                "phone_number": self.phone_number,
                "email": self.email,
                "experience": self.experience,
                "education": self.education,
            },
        )


def build_resume(context: ResumeIn):
    builder = ResumeBuilder(context)
    return HTML(string=builder.build()).write_pdf()


class ResumeService:
    @staticmethod
    async def create(resume_schema: ResumeIn) -> str:
        data = resume_schema.dict()
        pdf = await sync_to_async(build_resume)(resume_schema)
        object_key = uuid.uuid4().hex + f"_{data.get("title")}" + ".pdf"
        url = await s3.upload_bytes_to_s3(
            pdf, object_key=object_key, content_type="application/pdf"
        )
        data["s3_url"] = url
        await resume_repository.create(**data)
        return url

    @staticmethod
    async def get(resume_id: int | None = None) -> str | list[str]:
        if resume_id:
            resume = await resume_repository.get(id=resume_id)
            return resume.s3_url
        resumes = await resume_repository.list()
        return [resume.s3_url for resume in resumes]


    @staticmethod
    async def update(
        resume_id: int, resume_schema: ResumeIn, partial: bool = False
    ) -> str:
        resume = await resume_repository.get(id=resume_id)
        data = resume_schema.dict(exclude_none=partial)
        object_key = uuid.uuid4().hex + f"_{data.get("title")}" + ".pdf"
        pdf = await sync_to_async(build_resume)(resume_schema)
        url = await s3.upload_bytes_to_s3(
            pdf, object_key=object_key, content_type="application/pdf"
        )

        data["s3_url"] = url

        await resume_repository.update(resume, **data)
        return url

    @staticmethod
    async def delete(resume_id) -> bool:
        resume = await resume_repository.get(id=resume_id)
        await resume_repository.delete(resume)
        return True


resume_service = ResumeService()
