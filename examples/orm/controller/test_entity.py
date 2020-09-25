from hyssop.web.controller.tornado import RequestController

from component import ExampleOrmComponentTypes
from component.test_entity import TestEntityComponent


class TestEntityController(RequestController):
    SUPPORTED_METHODS = ("GET", "DELETE", "PUT")

    @property
    def comp_test_entity(self) -> TestEntityComponent:
        return self.component_manager.get_component(ExampleOrmComponentTypes.TestEntity)

    async def get(self, id: int = None):
        """
        ---
        tags:
        - test entity
        summary: get list of test entities
        produces:
        - application/json
        responses:
            200:
              description: return list of test entities
            400:
              description: entity does not exist
        """
        if id:
            entities = await self.comp_test_entity.get_test_entity(id=id)
            if len(entities) > 0:
                self.write(entities[0].to_json_dict())
            else:
                self.set_status(404)
        else:
            kwargs = self.get_arguments_dict(
                ['name', 'age', 'gender', 'schedule'])
            entities = await self.comp_test_entity.get_test_entity(**kwargs)
            self.write({
                'test_entities': [e.to_json_dict() for e in entities]
            })

    async def put(self, id: int = None):
        """
        ---
        tags:
        - test entity
        summary: add / update test entity
        produces:
        - application/json
        responses:
            200:
              description: return updated test entity
            400:
              description: required parameters are not in body
        """
        kwargs = {
            'name': self.get_argument('name'),
            'age': self.get_argument('age'),
            'gender': self.get_argument('gender')
        }

        if id:
            kwargs['id'] = id

        entity = await self.comp_test_entity.merge_test_entity(**kwargs)
        self.write(entity.to_json_dict())

    async def delete(self, id: int = None):
        """
        ---
        tags:
        - test entity
        summary: delete test entity
        produces:
        - application/json
        responses:
            200:
              description: return deleted test entity
            404:
              description: test entity does not exist
        """
        entity = await self.comp_test_entity.delete_test_entity(id)
        if entity:
            self.write(entity.to_json_dict())
        else:
            self.set_status(404)
