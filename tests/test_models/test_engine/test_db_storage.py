#!/usr/bin/python3
import os
import unittest
from models.state import State
from models.engine.db_storage import DBStorage


storage = DBStorage()


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DB Storage test')
class TestDBStorage(unittest.TestCase):
    """Tests for the DBStorage engine"""

    @classmethod
    def setUpClass(cls):
        """Setting up the test environment"""
        storage.reload()
        if not isinstance(storage, DBStorage):
            raise unittest.SkipTest("Not using DBStorage")

    def setUp(self):
        if isinstance(storage, DBStorage):
            self.session = storage._DBStorage__session
            self.session.begin()

    def tearDown(self):
        """Rolls back a transaction"""
        if hasattr(self, 'session'):
            self.session.rollback()

    def test_add_and_commit(self):
        """Testing adding and committing objects to Database"""
        initial_count = self.session.query(State).count()
        new_state = State(name="Texas")
        self.session.add(new_state)
        self.session.commit()
        self.assertEqual(self.session.query(State).count(), initial_count + 1)
        self.session.delete(new_state)
        self.session.commit()

    def test_delete_state(self):
        """Testing deleting a State from the Database"""
        initial_count = self.session.query(State).count()

        new_state = State(name="California")
        self.session.add(new_state)
        self.session.commit()

        self.assertEqual(self.session.query(State).count(), initial_count + 1)

        # Deletes then verifies removal
        self.session.delete(new_state)
        self.session.commit()
        self.assertEqual(self.session.query(State).count(), initial_count)

    def test_get_state(self):
        """Testing retrieving a State from the Database"""
        new_state = State(name="Nevada")
        self.session.add(new_state)
        self.session.commit()

        # Retrieves and verifies retrieval
        retrieved_state = self.session.query(State).get(new_state.id)
        self.assertEqual(retrieved_state.id, new_state.id)
        self.assertEqual(retrieved_state.name, "Nevada")

        # Cleanup
        self.session.delete(new_state)
        self.session.commit()
