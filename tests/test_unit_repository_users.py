import sys
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from src.database.models import User
from src.schemas.users import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        email = "test@example.com"
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        user_data = UserModel(username="Test Name", email="test@example.com", password="test_123")
        self.session.commit.return_value = None
        result_user = await create_user(body=user_data, db=self.session)
        self.assertIsInstance(result_user, User)
        self.assertEqual(result_user.email, user_data.email)
        self.assertEqual(result_user.password, user_data.password)

    async def test_update_token(self):
        token = "test_token"
        await update_token(user=self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)


    async def test_confirmed_email(self):
        email = "test@example.com"
        user = MagicMock(confirmed=False)
        self.session.query().filter().first.return_value = user
        await confirmed_email(email, db=self.session)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        url = "https://example.com/avatar.jpg"
        self.user.avatar = None
        self.session.query().filter().first.return_value = self.user
        result_user = await update_avatar(self.user.email, url, db=self.session)
        self.assertEqual(result_user.avatar, url)


if __name__ == "__main__":
    unittest.main()
