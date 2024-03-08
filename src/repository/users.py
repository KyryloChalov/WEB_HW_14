from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email_: str, db: Session) -> User | None:
    """
    Get the user by email from the database.

    :param email: The email of the user to retrive.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email
    :rtype: User
    """
    return db.query(User).filter(User.email == email_).first()


async def create_user(body: UserModel, db: Session) -> User:
    """Create a new user.

    :param body: The data for the new user to be created.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    # async def update_token(user: User, token: str, db: Session) -> None:
    """
    Update token for the specified user.

    :param user: The user to update token for.
    :type user: User
    :param token: The refreshed token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm user's email.

    :param email: The email to confirm.
    :type email: str
    :param bd: The database session.
    :type bd: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update user's avatar url.

    :param email: The user's email.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
