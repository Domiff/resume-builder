from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from weasyprint import HTML

from resume.schemas import ResumeIn


class Builder:
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
    builder = Builder(context)
    return HTML(string=builder.build()).write_pdf()
