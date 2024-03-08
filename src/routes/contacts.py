from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contacts import ContactModel, ContactResponse
from src.services.auth import auth_service
from typing import List

router = APIRouter(prefix="/contacts", tags=["contacts"])


# @router.post("/", response_model=ContactResponse)
@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description="No more than 2 requests per minute",
    dependencies=[Depends(RateLimiter(times=2, seconds=60))],
)
async def create_contact(
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Create a new contact for the authorized user.

    :param contact: The data for the contact to be created.
    :type contact: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The user to create the contact for.
    :type current_user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(contact, current_user, db)


# всі контакти без зайвих питань - чи воно треба?
# @router.get("/", response_model=List[ContactResponse])
# async def read_all_contacts(db: Session = Depends(get_db)):
#     contacts = await repository_contacts.read_contacts(db)
#     return contacts


# пошук рядка find_string в полях first_name, last_name, email
# якшо рядок пошуку порожній - виводяться всі контакти
@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def read_contacts(
    db: Session = Depends(get_db),
    find_string: str = "",
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieve all contacts for the authorized user, optionally filtered by a search query.

    :param q: The search query. Defaults to None.
    :type q: str
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve contacts for.
    :type user: User
    :return: List of contacts matching the search query if provided or all contacts of the user, if query is None.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.read_contacts(db, find_string, current_user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def find_contact_id(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a single contact with specified ID for the authorized user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The user to retrieve contact for.
    :type current_user: User
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: The found contact.
    """
    contact = await repository_contacts.find_contact(contact_id, current_user, db)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def update_contact(
    contact_id: int,
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Update a specified contact's details for a authorized user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated contact details.
    :type contact: ContactUpdate
    :param db: The database session.
    :type db: Session
    :param current_user: The user to whom the contact belongs.
    :type current_user: User
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: The updated contact.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.update_contact(
        contact_id, current_user, contact, db
    )
    return contact


@router.delete(
    "/{contact_id}",
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Removes a single contact with the specified ID for a authorized user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param current_user: The user to remove the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException: If the contact with the specified ID is not found.
    :return: A message confirming the deletion.
    :rtype: dict
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    return contact


@router.get(
    "/birthdays/",
    response_model=List[ContactResponse],
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_next_days_birthdays(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
    days: int = 7,
):
    """
    Get all contacts of an authorized user with birthdays in the next N days (default N = 7)
    Contacts are displayed sorted by date

    :param user: The user to retrieve the contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Contacts with birthdays within next N days.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.get_next_days_birthdays(current_user, db, days)
    return contacts

    # @router.get(
    #     "/birthdays_4/",
    #     response_model=List[ContactResponse],
    #     description="No more than 5 requests per minute",
    #     dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    # )
    # async def get_contact_by_birthday(
    #     current_user: User = Depends(auth_service.get_current_user),
    #     db: Session = Depends(get_db),
    #     days: int = 7,
    # ):
    # """
    # Get all contacts of an authorized user with birthdays in the next N days (default N = 7)
    # an alternative option - works faster, but there is no sorting by date of birth

    # :param user: The user to retrieve the contacts for.
    # :type user: User
    # :param db: The database session.
    # :type db: Session
    # :return: Contacts with birthdays within next N days.
    # :rtype: List[Contact]
    # """
    # contacts = await repository_contacts.get_contact_by_birthday(current_user, db, days)
    # return contacts
