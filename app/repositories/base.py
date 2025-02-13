from typing import Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, collection: AsyncIOMotorCollection, model: type[ModelType]):
        self.collection = collection
        self.model = model

    async def find_one(self, query: dict) -> ModelType | None:
        result = await self.collection.find_one(query)
        if result:
            return self.model.model_validate(result)
        return None

    async def find_many(self, query: dict) -> list[ModelType]:
        cursor = self.collection.find(query)
        results = await cursor.to_list(length=None)
        return [self.model.model_validate(doc) for doc in results]

    async def create(self, document: ModelType) -> ModelType:
        doc_dict = document.model_dump(exclude={"id"})
        if hasattr(document, "created_at"):
            doc_dict["created_at"] = document.created_at
        if hasattr(document, "updated_at"):
            doc_dict["updated_at"] = document.updated_at

        result = await self.collection.insert_one(doc_dict)
        return await self.find_one({"_id": result.inserted_id})

    async def update(self, query: dict, update_data: dict) -> ModelType | None:
        result = await self.collection.find_one_and_update(
            query, {"$set": update_data}, return_document=True
        )
        if result:
            return self.model.model_validate(result)
        return None

    async def delete(self, query: dict) -> bool:
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
