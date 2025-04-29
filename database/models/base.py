from contextlib import asynccontextmanager
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator
from surrealdb import AsyncSurrealDB, RecordID, Table

from data.config import SURREAL_DB, SURREAL_NS, SURREAL_PASS, SURREAL_URL, SURREAL_USER


@asynccontextmanager
async def get_session():
    async with (
        AsyncSurrealDB(SURREAL_URL) if SURREAL_URL else AsyncSurrealDB("surrealkv://database.kv")
    ) as session:
        if SURREAL_PASS and SURREAL_USER:
            await session.sign_in(SURREAL_USER, SURREAL_PASS)
        await session.use(SURREAL_NS, SURREAL_DB)
        yield session


def convert_datetime_to_iso(dt: datetime) -> str:
    dt.isoformat()
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def execute(func):
    async def wrapper(*args, **kwargs):
        if not "session" in kwargs:
            async with get_session() as session:
                kwargs["session"] = session
                return await func(*args, **kwargs)

        return await func(*args, **kwargs)

    return wrapper


class BaseMeta(type(BaseModel)):
    def __new__(cls, name, bases, namespace, **kwargs):
        annotations = namespace["__annotations__"]
        if "id" in annotations:
            namespace["id"] = Field(default=0 if annotations["id"] == int else "0")
        return super().__new__(cls, name, bases, namespace, **kwargs)


class Base(BaseModel, metaclass=BaseMeta):
    _table: str

    id: str | int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    @execute
    async def get(cls, id: str | int, session: AsyncSurrealDB = None, **kwargs):
        obj = await session.select(RecordID(cls._table, id))
        return cls(**obj) if obj else None

    @classmethod
    @execute
    async def get_all(cls, session: AsyncSurrealDB = None, **kwargs):
        objs = await session.select(Table(cls._table))
        return [cls(**o) for o in objs]

    @classmethod
    @execute
    async def create(cls, session: AsyncSurrealDB = None, **kwargs):
        id = kwargs.pop("id", None)
        id = RecordID(cls._table, id) if id else Table(cls._table)
        kwargs = cls(**kwargs).model_dump(mode="json", exclude={"id"})
        obj = await session.create(id, kwargs)
        return cls(**(obj[0] if obj is list else obj))

    @classmethod
    @execute
    async def update(cls, id: str | int, session: AsyncSurrealDB = None, **kwargs):
        kwargs["updated_at"] = convert_datetime_to_iso(datetime.now(timezone.utc))
        await session.query(f"UPDATE {RecordID(cls._table, id)} MERGE {kwargs}")
        return await cls.get(id=id, session=session)

    @classmethod
    @execute
    async def delete(cls, id: str | int, session: AsyncSurrealDB = None):
        await session.delete(RecordID(cls._table, id))
        return True

    @classmethod
    @execute
    async def get_or_create(cls, id: str | int, session: AsyncSurrealDB = None, **kwargs):
        if obj := await cls.get(id, session=session):
            return obj
        return await cls.create(id=id, session=session, **kwargs)

    @classmethod
    @execute
    async def update_or_create(cls, id: str | int, session: AsyncSurrealDB = None, **kwargs):
        if user := await cls.update(id=id, **kwargs):
            return user
        return await cls.create(id=id, session=session, **kwargs)

    @classmethod
    def set_collection(cls, collection: str):
        cls._table = collection

    @field_validator("id", mode="before", check_fields=False)
    def parse_id(cls, v: RecordID | str | int):
        id = v
        if isinstance(v, RecordID):
            id = v.id

        if isinstance(cls.__annotations__["id"], int):
            return int(id)
        return id

    model_config = ConfigDict(json_encoders={datetime: convert_datetime_to_iso})
