import uuid

from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import aget_object_or_404
from ninja import Router

from core.s3 import s3
from resume.models import Resume
from resume.schemas import ResumeIn, ResumeOut
from resume.builder import build_resume

router = Router(tags=["Resume"])


@router.post("/resume")
async def create_resume(request: HttpRequest, resume_schema: ResumeIn) -> JsonResponse:
    """Create a new resume."""
    resume = await Resume.objects.acreate(**resume_schema.dict())
    pdf = build_resume(resume_schema)
    object_key = uuid.uuid4().hex + f"_{resume.title}" + ".pdf"
    url = await s3.upload_bytes_to_s3(pdf, object_key=object_key, content_type="application/pdf")
    resume.s3_url = url
    await resume.asave()
    return JsonResponse(data={"url": url}, status=201)


@router.get("/resume")
async def get_resume(request: HttpRequest) -> JsonResponse:
    """Get all resume s3 links."""
    urls = [s3_url async for s3_url in Resume.objects.values_list("s3_url", flat=True)]
    if not urls:
        raise Http404("No Resume matches the given query.")
    return JsonResponse(data={"urls": urls}, status=200)


@router.get("/resume/{resume_id}")
async def get_resume_by_id(request: HttpRequest, resume_id: int) -> JsonResponse:
    """Get a resume by id."""
    url = [s3_url async for s3_url in Resume.objects.filter(id=resume_id).values_list("s3_url", flat=True)]
    return JsonResponse(data={"url": url}, status=200)


@router.put("/resume/{resume_id}")
async def update_resume(
    request: HttpRequest, resume_id: int, resume_schema: ResumeIn
) -> JsonResponse:
    """Full update a resume."""
    resume = Resume.objects.filter(id=resume_id)
    object_key = uuid.uuid4().hex + f"_{resume_schema.dict().get("title", "resume")}" + ".pdf"
    pdf = build_resume(resume_schema)
    url = await s3.upload_bytes_to_s3(pdf, object_key=object_key, content_type="application/pdf")
    data = resume_schema.dict()
    data["s3_url"] = url
    await resume.aupdate(**data)
    return JsonResponse(data={"url": url}, status=200)


@router.patch("/resume/{resume_id}")
async def patch_resume(
    request: HttpRequest, resume_id: int, resume_schema: ResumeIn
) -> JsonResponse:
    """Partial update a resume."""
    resume = Resume.objects.filter(id=resume_id)
    object_key = uuid.uuid4().hex + f"_{resume_schema.dict().get("title", "resume")}" + ".pdf"
    pdf = build_resume(resume_schema)
    url = await s3.upload_bytes_to_s3(pdf, object_key=object_key, content_type="application/pdf")
    data = resume_schema.dict(exclude_none=True)
    data["s3_url"] = url
    await resume.aupdate(**data)
    return JsonResponse(data={"url": url}, status=200)


@router.delete("/delete/{resume_id}")
async def delete_resume(request: HttpRequest, resume_id: int) -> dict:
    """Delete a resume."""
    employee = await aget_object_or_404(Resume, id=resume_id)
    await employee.adelete()
    return {"success": True}
