from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy import or_, and_, extract, select, func
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel
from src.static.colors import GRAY, RESET, CYAN, MAGENTA, WHITE, GRAY_BACK
from typing import List


async def create_contact(contact: ContactModel, user: User, db: Session = Depends(get_db)):
    """
    Create a new contact for an authorized user.

    :param contact: The data for the contact to be created.
    :type contact: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def read_contacts(db: Session = Depends(get_db), q: str = "", user = User):
    """
    Get all contacts of an authorized user.
    If desired, contacts can be filtered by search query.

    :param db: The database session.
    :type db: Session
    :param q: The search query. Defaults to None.
    :type q: str
    :param user: The user to retrieve contacts for.
    :type user: User
    :return: List of contacts matching the search query if provided or all contacts of the user, if query is None.
    :rtype: List[Contact]
    """
    if q:
        return (
            db.query(Contact)
            .filter(
                and_(
                or_(
                    Contact.first_name.ilike(f"%{q}%"),
                    Contact.last_name.ilike(f"%{q}%"),
                    Contact.email.ilike(f"%{q}%"),
                ),
                Contact.user_id == user.id

            ))
            .all()
        )

    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def find_contact(contact_id: int, user: User, db: Session = Depends(get_db)):
    """
    Get one contact with the specified ID for the authorized user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: The found contact.
    :rtype: Contact
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )
    return contact


async def update_contact(contact_id: int, user: User, body: ContactModel, db: Session):
    """
    Update a specified contact's details for a authorized user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param user: The user to whom the contact belongs.
    :type user: User
    :param contact: The updated contact details.
    :type contact: ContactUpdate
    :param db: The database session.
    :type db: Session
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: The updated contact.
    :rtype: Contact
    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.user_id == user.id,  Contact.id == contact_id))
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )

    if contact:
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, user: User, db: Session = Depends(get_db)):
    """
    Deletes one contact with the specified ID for the authorized service.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: A message confirming the deletion.
    :rtype: dict
    """
    db_contact = (
        db.query(Contact)
        .filter(and_(Contact.user_id == user.id, Contact.id == contact_id))
        .first()
    )
    if db_contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact successfully deleted"}


def birthdays_print(result, today_, days_):
    '''
    for debugging: outputting data to the terminal
    '''
    def blank(num:int, data) -> str:
        return str(" " * (num - len(str(data))) + str(data))

    print(GRAY, end="")
    if result == []:
        print(f"     there are no contacts whose birthday is in the next {days_} days")
    else:
        print('------------------------------------------------')
        print('  №   id    birthday   age     fullname        ')
        print('------------------------------------------------')
        for num, res in enumerate(result, 1):
            age = today_.year - res.birthday.year
            print(f"{blank(3, num)}. {blank(4, res.id)} {RESET}", end=' ')
            print(f"{res.birthday.strftime("%d-%m-%Y")}", end=' ')
            print(f"{MAGENTA if res.birthday.day == today_.day else CYAN}", end=' ')
            print(f"{blank(3, age)}{GRAY}", end="  ")
            print(f"{WHITE}{res.first_name } {res.last_name}{GRAY}")
        print('------------------------------------------------')


async def get_next_days_birthdays(user_: User, db: Session = Depends(get_db), days_: int = 7):
    """
    Get all contacts of an authorized user with birthdays in the next N days (default N = 7)
    Contacts are displayed sorted by date

    :param user: The user to retrieve the contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Contacts with birthdays within next 7 days.
    :rtype: List[Contact]
    """
    today_ = datetime.today().date()
    # today_ = datetime(year=2023, month=12, day=27).date() # debugging

    result = []
    for num in range(days_+1):

        date_ = today_ + timedelta(num)

        contacts = db.query(Contact).filter_by(user=user_).filter(
            extract('month', Contact.birthday) == date_.month,
            extract('day', Contact.birthday) == date_.day
        ).where(Contact.birthday != None).all()

        for i in range(len(contacts)):
            result.append(contacts[i])

    birthdays_print(result, today_, days_) # debugging
    return result



# from sqlalchemy.ext.asyncio import AsyncSession

async def get_contact_by_birthday(user_: User, db: Session, days_: int = 7):
    """
    Get all contacts of an authorized user with birthdays in the next N days (default N = 7)
    an alternative option - works faster, but there is no sorting by date of birth

    :param user: The user to retrieve the contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Contacts with birthdays within next 7 days.
    :rtype: List[Contact]
    """
    today_ = datetime.today().date()
    end_date = today_+ timedelta(days=days_)

    result = []

    stmt = select(Contact).filter_by(user=user_).where(Contact.birthday != None)
    contacts = db.execute(stmt)
    contacts = contacts.scalars().all()
    
    for contact in contacts:
        bday_this_year = datetime(year=today_.year, month=contact.birthday.month, day=contact.birthday.day).date()

        if bday_this_year >= today_ and bday_this_year <= end_date:
            result.append(contact)

    birthdays_print(result, today_, end_date) # debugging
    return result
