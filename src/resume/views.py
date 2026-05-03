from django.http import Http404, HttpRequest, JsonResponse
from ninja import Router

from resume.schemas import ResumeIn
from resume.repository import ResumeRepo

router = Router(tags=["Resume"])


@router.post("/resume")
async def create_resume(request: HttpRequest, resume_schema: ResumeIn) -> JsonResponse:
    """Create a new resume."""
    url = await ResumeRepo.create(resume_schema=resume_schema)
    return JsonResponse(data={"url": url}, status=201)


@router.get("/resume")
async def get_all_resumes(request: HttpRequest) -> JsonResponse:
    """Get all resume."""
    urls = await ResumeRepo.get()
    if not urls:
        raise Http404("No Resume matches the given query.")
    return JsonResponse(data={"urls": urls}, status=200)


@router.get("/resume/{resume_id}")
async def get_one_resume(request: HttpRequest, resume_id: int) -> JsonResponse:
    """Get a resume by id."""
    url = await ResumeRepo.get(resume_id)
    if not url:
        raise Http404("No Resume matches the given query.")
    return JsonResponse(data={"url": url}, status=200)


@router.put("/resume/{resume_id}")
async def put_resume(
    request: HttpRequest, resume_id: int, resume_schema: ResumeIn
) -> JsonResponse:
    """Full update a resume."""
    url = await ResumeRepo.update(resume_id, resume_schema)
    return JsonResponse(data={"url": url}, status=200)


@router.patch("/resume/{resume_id}")
async def patch_resume(
    request: HttpRequest, resume_id: int, resume_schema: ResumeIn
) -> JsonResponse:
    """Partial update a resume."""
    url = await ResumeRepo.update(resume_id, resume_schema, True)
    return JsonResponse(data={"url": url}, status=200)


@router.delete("/delete/{resume_id}")
async def delete_resume(request: HttpRequest, resume_id: int):
    """Delete a resume."""
    await ResumeRepo.delete(resume_id)
