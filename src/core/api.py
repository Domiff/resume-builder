from ninja import NinjaAPI

from resume.views import router


def create_api() -> NinjaAPI:
    app = NinjaAPI()
    app.add_router("", router)
    return app


api = create_api()
