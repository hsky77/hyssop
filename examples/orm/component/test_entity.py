import enum
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Enum

from hyssop.web.component import Component, ComponentManager
from hyssop_extension.component.orm import OrmDBComponent, get_declarative_base, EntityMixin, BasicUW

from . import ExampleOrmComponentTypes

DeclarativeBase = get_declarative_base()


class GenderType(enum.Enum):
    Male = 'male'
    Female = 'female'


class TestEntity(DeclarativeBase, EntityMixin):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderType), nullable=False)
    schedule = Column(DateTime, default=datetime.now)

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Generate dict that is serializable by Json convertor
        """
        data = super().to_json_dict()
        data['gender'] = data['gender'].value
        return data


TestUW = BasicUW(TestEntity)


class TestEntityComponent(Component):

    @property
    def Orm(self) -> OrmDBComponent:
        return self.orm if hasattr(self, 'orm') else None

    def OrmExecutor(self):
        return self.Orm.get_executor(self.db_id, TestUW)

    def init(self, component_manager: ComponentManager, db_id: str, *arugs, **kwargs) -> None:
        self.orm = component_manager.get_component(
            ExampleOrmComponentTypes.Orm)
        self.db_id = db_id
        self.Orm.init_db_declarative_base(self.db_id, DeclarativeBase)

    async def get_test_entity(self, **kwargs) -> List[TestEntity]:
        async with self.OrmExecutor() as executor:
            return await executor.select_async(**kwargs)

    async def merge_test_entity(self, **kwargs) -> TestEntity:
        if 'gender' in kwargs:
            kwargs['gender'] = GenderType(kwargs['gender'])

        async with self.OrmExecutor() as executor:
            await executor.reserve_session_async()
            try:
                entity = await executor.merge_async(**kwargs)
                await executor.commit_async()
                return entity
            except Exception as e:
                await executor.rollback_async()
                raise e from e

    async def delete_test_entity(self, id: int) -> TestEntity:
        async with self.OrmExecutor() as executor:
            entity = await executor.load_async(id=id)
            if entity:
                await executor.reserve_session_async()
                try:
                    await executor.delete_async([entity])
                    await executor.commit_async()
                    return entity
                except Exception as e:
                    await executor.rollback_async()
                    raise e from e
