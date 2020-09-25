from hyssop.web.component import ComponentTypes


class ExampleOrmComponentTypes(ComponentTypes):
    Orm = ('orm', 'hyssop_extension.component.orm', 'OrmDBComponent')
    TestEntity = ('test_entity', 'test_entity', 'TestEntityComponent')
