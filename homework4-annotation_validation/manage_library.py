from pydantic import BaseModel, field_validator
from typing import Optional, List
from functools import wraps

def log_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Выполняется операция: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Операция {func.__name__} завершена")
        return result
    return wrapper

class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool
    categories: List[str] = []

    @field_validator("categories", mode="before")
    def categories_must_be_in_list(cls, categories: List[str]) -> str:
        if not isinstance(categories, list):
            raise ValueError("Categories must be a list")
        for category in categories:
            if not isinstance(category, str) or not category.strip():
                raise ValueError("Each category must be a non-empty string")
            return categories
        return None


class User(BaseModel):
    name: str
    email: str
    membership_id: str

    @field_validator("email", mode="before")
    def email_must_contain_atsign_symbol(cls, email) -> str:
        if "@" not in email:
            raise ValueError("Email must contain @")
        return email

class Library(BaseModel):
    books: List[Book] = []
    users: List[User] = []

    def total_books(self) -> int:
        return len(self.books)


def add_book(title: str, author: str, year: int, categories: List[str] = None) -> str:
    if categories is None:
        categories = []

    book = Book(
        title=title,
        author=author,
        year=year,
        available=True,
        categories=categories,
    )
    library.books.append(book)
    return (f"{title} by {author} is added to Library")


def find_book(title: str) -> bool:
    for book in library.books:
        if book.title == title:
            return True
    return False


def is_book_borrow(title: str) -> bool:
    for book in library.books:
        if book.title == title:
            if not book.available:
                raise BookNotAvailable(f"Book '{title}' is not available for borrowing")
            return book.available
    return False


@log_operation
def return_book(title: str) -> bool:
    for book in library.books:
        if book.title == title:
            book.available = True
            return True
    return False

class BookNotAvailable(Exception):
    pass


if __name__ == "__main__":
    books: List[Book] = []
    library = Library()

    library_categories = ["Классика", "Ужасы", "Фантастика"]

    print(add_book("Спецоперация и мир", "Лев Толстой", 1867, ["Классика"]))

    print("Book is finded -", find_book("Спецоперация и мир"))

    try:
        print("Book is available -", is_book_borrow("Спецоперация и мир"))
    except BookNotAvailable as e:
        print(f"Error: {e}")

    print("Book returned -", return_book("Спецоперация и мир"))

    print("Total books in library:", library.total_books())





