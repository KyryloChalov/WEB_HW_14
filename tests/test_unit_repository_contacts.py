import sys
import os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
from fastapi import HTTPException

import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel
from src.repository.contacts import (
    create_contact,
    read_contacts,
    find_contact,
    delete_contact,
    update_contact,
    get_next_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(
            id=1,
            username="test_user",
            password="password",
            email="test@user.com",
            confirmed=True,
        )
        self.session = MagicMock(spec=Session)

    def _print(self, result):
        """for debugging"""
        # print(self.user.id, self.user.username)
        print("vv =========================================== vv")
        if isinstance(result, (Contact)):
            print(f"{result = }")
            print(result.id, end=" ")
            print(result.first_name, end=" ")
            print(result.last_name, end=" ")
            print(result.email, end=" ")
            print(result.birthday)
        elif isinstance(result, (ContactModel)):
            print(f"{result = }")
            # print(result.id, end=" ")
            print(result.first_name, end=" ")
            print(result.last_name, end=" ")
            print(result.email, end=" ")
            print(result.birthday)
        else:
            for res in result:
                print(f"{res = }")
                print(res.id, end=" ")
                print(res.first_name, end=" ")
                print(res.last_name, end=" ")
                print(res.email, end=" ")
                print(res.birthday)
        print("^^ =========================================== ^^")

    def call_from(self):
        stack = traceback.extract_stack()
        print(f">>> function '{stack[-2].name}' called by '{stack[-3].name}'")

    def assert_fields(
        self, result: ContactModel, object_: ContactModel, to_print=False
    ):
        if to_print:
            self.call_from()
            print(2 * "\t", "result", 3 * "\t", "contact")

        for field_name in [
            "first_name",
            "last_name",
            "email",
            "phone",
            "birthday",
            "notes",
        ]:
            self.assertEqual(getattr(result, field_name), getattr(object_, field_name))
            if to_print:
                print(f"{field_name}:", end="")
                print(f"{'\t\t' if len(field_name) < 8 else '\t'}", end="")
                print(f"{getattr(result, field_name)}", end="")
                print(
                    f"{'\t\t' if len(str(getattr(object_, field_name))) < 18 else '\t'}",
                    end="",
                )
                print(f"  ==   {getattr(object_, field_name)}")

    # ===========================================
    async def test_create_contact(self):
        contact = ContactModel(
            first_name="first_name_test",
            last_name="last_name_test",
            email="email_contact@test.com",
            phone="+380671234567",
            birthday=date.today() + timedelta(days=2),
            notes="test note contact 1",
        )
        result = await create_contact(contact=contact, user=self.user, db=self.session)

        self.assertIsInstance(result, Contact)
        self.assertTrue(hasattr(result, "id"))
        self.assert_fields(result, contact)

    async def test_read_contacts_all(self):
        contacts = [Contact(), Contact(), Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await read_contacts(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_read_contacts_with_query(self):
        query = "test"
        contacts = [
            Contact(
                id=0,
                first_name="test_first_0",
                last_name="test_last_0",
                email="user_0@test.com",
            ),
            Contact(
                id=1,
                first_name="test_first_1",
            ),
            Contact(
                id=2,
                email="user_2@test.com",
            ),
        ]
        self.session.query().filter().all.return_value = contacts
        result = await read_contacts(q=query, user=self.user, db=self.session)
        # self._print(result)
        self.assertEqual(result, contacts)

    async def test_find_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await find_contact(contact_id=1, user=self.user, db=self.session)
        # self._print(result)
        self.assertEqual(result, contact)

    async def test_find_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await find_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(context.exception.status_code, 404)

    async def test_remove_contact_found(self):
        contact = Contact(id=1)
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, {"message": "Contact successfully deleted"})

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(context.exception.status_code, 404)

    async def test_update_contact(self):
        contact = ContactModel(
            first_name="first_name_test",
            last_name="last_name_test",
            email="email_contact@test.com",
            phone="+380671234567",
            birthday=date.today() + timedelta(days=2),
            notes="test note contact 1",
        )
        contact_upd = ContactModel(
            first_name="Сергій",
            last_name="Голобородько",
            email="kostiantynsaienko@meta.ua",
            phone="+380996735724",
            birthday=date.today() + timedelta(days=12),
            notes="Тривога рішення ставити міф бак безглуздий деякий",
        )
        self.session.query().filter().first.return_value = Contact()
        result = await update_contact(
            contact_id=1, user=self.user, body=contact, db=self.session
        )
        self.assert_fields(result, contact)

        self.assertIsInstance(result, Contact)
        result = await update_contact(
            contact_id=1, user=self.user, body=contact_upd, db=self.session
        )
        self.assertIsInstance(result, Contact)
        self.assert_fields(result, contact_upd)

    async def test_update_contact_not_found(self):
        contact_body = ContactModel(
            first_name="Сергій",
            last_name="Голобородько",
            email="kostiantynsaienko@meta.ua",
            phone="+380996735724",
            birthday=date.today(),
            notes="Тривога рішення ставити міф бак безглуздий деякий",
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        with self.assertRaises(HTTPException) as context:
            await update_contact(
                contact_id=1,
                user=self.user,
                body=contact_body,
                db=self.session,
            )
        self.assertEqual(context.exception.status_code, 404)

    async def test_get_next_days_birthdays(self):
        future_birthday_contacts = [
            Contact(birthday=datetime.today().date()),
            Contact(birthday=datetime.today().date() + timedelta(5)),
        ]
        self.session.query().filter().all.return_value = future_birthday_contacts

        future_birthdays = await get_next_birthdays(
            user=self.user, db=self.session
        )
        self.assertEqual(future_birthdays, future_birthday_contacts)


if __name__ == "__main__":
    unittest.main()
