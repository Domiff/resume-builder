from ninja import ModelSchema

from resume.models import Resume


class ResumeIn(ModelSchema):
    class Meta:
        model = Resume
        exclude = ("id",)
        fields_optional = "__all__"


class ResumeOut(ModelSchema):
    class Meta:
        model = Resume
        fields = "__all__"
