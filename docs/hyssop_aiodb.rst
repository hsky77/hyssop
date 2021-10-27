hyssop-aiodb
******************

.. contents:: Table of Contents


**hyssop-aiodb** provides the hyssop components that integrates sqlalchemy, aiomysql, aiosqlite to access SQL database asynchronously.

**prerequest**: python 3.6+, pip

**Install** hyssop with pip: ``pip install hyssop_aiodb``


Usage
=============================

* Add the AioDBComponentTypes into ``component/__init__.py`` of your hyssop project.

    .. code-block:: python

        # component/__init__.py

        from hyssop_aiodb.component import AioDBComponentTypes

    If your component has to depend on AioDBComponent, you could do the following way to be sure the object of AioDBComponent will be initialized at the first cleaned up at the last.

    .. code-block:: python

        # component/__init__.py

        from hyssop.project.component import ComponentTypes

        class YourProjectComponentTypes(ComponentTypes):
            AioDB = ('aiodb', 'hyssop_aiodb.component.aiodb', 'AioDBComponent')
            YourComponent = ('your_component', 'your_component', 'YourComponent')

* Configuration

    .. parsed-literal::

        # project_config.yml

        component:
            aiodb:
                db_1:
                    module: 'sqlite'
                    file_name: "db.sqlite3"
                db_2:
                    module: 'mysql'
                    connections: 1
                    host: <your mysql server ip>
                    port: <your mysql server port>
                    db_name: <your mysql server db>
                    user: <user account>
                    password: <user password>

* Define the orm class of sqlalchemy.

    .. code-block:: python

        from hyssop_aiodb.component.aiodb import get_declarative_base, SQLAlchemyEntityMixin, AsyncEntityUW

        MODULES = get_declarative_base()

        class AccountEntity(MODULES, SQLAlchemyEntityMixin):
            __tablename__ = 'account'

            id = Column(Integer, primary_key=True)
            account = Column(String(40), nullable=False, unique=True, index=True)
            password = Column(String(40), nullable=False)

        AccountUW = AsyncEntityUW(AccountEntity)    # provide simple methods to access database tables

* Access database by AioDBComponent.

    .. code-block:: python

        import asyncio

        from hyssop_aiodb.component import AioDBComponentTypes
        from hyssop.project.mixin import ProjectMixin

        project = ProjectMixin()
        project.load_project("path to your project directory")

        aiodb_comp = project.component_manager.get_component(AioDBComponentTypes.AioDB)
        aiodb_comp.init_db_declarative_base("db_1", MODULES)

        async_db = aiodb_comp.get_async_database("db_1")

        async def test_async():
            async with async_db.get_connection_proxy() as connection:
                async with connection.get_cursor_proxy() as cursor:
                    account_data = {
                        'account': "account1",
                        'password': '1234',
                    }

                    account = await AccountUW.load(cursor, **account_data)

                    if account is not None:
                        account = await AccountUW.add(cursor, **account_data)

                    account = await AccountUW.update(cursor, account, password='5678')
                    await AccountUW.delete(cursor, [account])

                    await cursor.commit()


        asyncio.get_event_loop().run_until_complete(test_async())
