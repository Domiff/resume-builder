from typing import TypeVar, Generic, Type

from django.db.models import Model
from django.shortcuts import aget_object_or_404

T = TypeVar("T", bound=Model)


class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, **kwargs) -> T:
        return await self.model.objects.acreate(**kwargs)

    async def list(self, **kwargs):
        return [model async for model in self.model.objects.filter(**kwargs)]

    async def get(self, **kwargs) -> T:
        return await aget_object_or_404(self.model, **kwargs)

    async def update(self, model: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(model, key, value)
        await model.asave()
        return model

    async def delete(self, model: T) -> None:
        await model.adelete()
