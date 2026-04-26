from django.http import HttpRequest, JsonResponse
from django.shortcuts import aget_object_or_404, aget_list_or_404
from ninja import Router

from resume.models import Resume
from resume.schemas import ResumeSchemaD, ResumeSchemaR

router = Router(tags=["Resume"])


@router.post("/resume")
async def create_resume(request: HttpRequest, resume_schema: ResumeSchemaD):
    """Create a new resume."""
    resume = await Resume.objects.acreate(**resume_schema.dict())
    return JsonResponse(data={"status": True, "resume_id": resume.id}, status=201)


@router.get("/resume")
async def get_resume(request: HttpRequest) -> list[ResumeSchemaR]:
    """Get all resumes."""
    resume_orm = await aget_list_or_404(Resume)
    resume_schemas = [ResumeSchemaR.from_orm(resume) for resume in resume_orm]
    return resume_schemas


@router.get("/resume/{resume_id}")
async def get_resume_by_id(request: HttpRequest, resume_id: int) -> ResumeSchemaR:
    """Get a resume by id."""
    resume = await aget_object_or_404(Resume, id=resume_id)
    return ResumeSchemaR.from_orm(resume)


@router.put("/resume/{resume_id}")
async def update_resume(request: HttpRequest, resume_id: int, resume_schema: ResumeSchemaD) -> dict:
    """Full update a resume."""
    await Resume.objects.filter(id=resume_id).aupdate(**resume_schema.dict())
    return {"success": True}


@router.patch("/resume/{resume_id}")
async def patch_resume(request: HttpRequest, resume_id: int, resume_schema: ResumeSchemaD) -> dict:
    """Partial update a resume."""
    resume_data = resume_schema.dict(exclude_unset=True)
    await Resume.objects.filter(id=resume_id).aupdate(**resume_data)
    return {"success": True}


@router.delete("/delete/{resume_id}")
async def delete_resume(request: HttpRequest, resume_id: int) -> dict:
    """Delete a resume."""
    employee = await aget_object_or_404(Resume, id=resume_id)
    await employee.adelete()
    return {"success": True}
