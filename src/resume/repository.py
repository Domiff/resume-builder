import uuid

from asgiref.sync import sync_to_async
from django.http import Http404
from django.shortcuts import aget_object_or_404

from core.s3 import s3
from resume.builder import build_resume
from resume.models import Resume
from resume.schemas import ResumeIn


class ResumeRepo:
    @staticmethod
    async def create(resume_schema: ResumeIn) -> str:
        resume = await Resume.objects.acreate(**resume_schema.dict())
        pdf = await sync_to_async(build_resume)(resume_schema)
        object_key = uuid.uuid4().hex + f"_{resume.title}" + ".pdf"
        url = await s3.upload_bytes_to_s3(
            pdf, object_key=object_key, content_type="application/pdf"
        )
        resume.s3_url = url
        await resume.asave()
        return url

    @staticmethod
    async def get(resume_id: int | None = None) -> str | list[str]:
        if resume_id:
            return [
                s3_url
                async for s3_url in Resume.objects.filter(id=resume_id).values_list(
                    "s3_url", flat=True
                )
            ][0]
        return [
            s3_url async for s3_url in Resume.objects.values_list("s3_url", flat=True)
        ]

    @staticmethod
    async def update(
        resume_id: int, resume_schema: ResumeIn, partial: bool = False
    ) -> str:
        try:
            resume = await Resume.objects.aget(id=resume_id)
        except Resume.DoesNotExist:
            raise Http404("Resume does not exist")

        object_key = uuid.uuid4().hex + f"_{resume.title}" + ".pdf"
        pdf = await sync_to_async(build_resume)(resume_schema)
        url = await s3.upload_bytes_to_s3(
            pdf, object_key=object_key, content_type="application/pdf"
        )
        data = resume_schema.dict(exclude_none=partial)
        data["s3_url"] = url

        for key, value in data.items():
            setattr(resume, key, value)

        await resume.asave()
        return url

    @staticmethod
    async def delete(resume_id) -> bool:
        resume = await aget_object_or_404(Resume, id=resume_id)
        await resume.adelete()
        return True
