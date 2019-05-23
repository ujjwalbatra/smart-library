from configuration import db, ma
from sqlalchemy import ForeignKey, Enum, or_, and_, cast, Date
import datetime
import enum


class MyEnum(enum.Enum):
    borrowed = "borrowed"
    returned = "returned"


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(1000))
    isbn = db.Column(db.String(20))
    published_year = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(1000))
    total_copies = db.Column(db.Integer, default=1)
    copies_available = db.Column(db.Integer, default=1)

    def __init__(self, title, isbn, published_year, author, total_copies):
        self.title = title
        self.isbn = isbn
        self.published_year = published_year
        self.author = author
        self.total_copies = total_copies
        self.copies_available = total_copies

    def add_book(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def query_book(query):
        result = Book.query.with_entities(Book.id, Book.title, Book.isbn, Book.author, Book.published_year,
                                          Book.total_copies, Book.copies_available). \
            filter(or_(Book.id.like("%" + query + "%"), Book.title.like("%" + query + "%"),
                       Book.author.like("%" + query + "%"), Book.isbn.like("%" + query + "%"))).all()

        book_schema = BookSchema(many=True)
        return book_schema.dump(result).data


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), index=True)
    email = db.Column(db.String(320), unique=True)


class BorrowRecord(db.Model):
    __tablename__ = 'borrow_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, ForeignKey('book.id'), nullable=False)
    status = db.Column(Enum(MyEnum))
    issue_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    actual_return_date = db.Column(db.DateTime)

    @staticmethod
    def get_stats():
        today = datetime.datetime.now().__str__()
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)

        books_borrowed_today = db.session.query(BorrowRecord). \
            filter(BorrowRecord.status == MyEnum.borrowed). \
            filter(BorrowRecord.issue_date.like(today)).count()

        books_returned_today = db.session.query(BorrowRecord). \
            filter(BorrowRecord.status == MyEnum.returned). \
            filter(BorrowRecord.actual_return_date.like(today)).count()

        books_borrowed_this_week = db.session.query(BorrowRecord). \
            filter(BorrowRecord.status == MyEnum.returned). \
            filter(and_(BorrowRecord.issue_date <= today, BorrowRecord.issue_date >= last_week)).count()

        books_returned_this_week = db.session.query(BorrowRecord). \
            filter(BorrowRecord.status == "returned"). \
            filter(and_(BorrowRecord.actual_return_date <= today, BorrowRecord.actual_return_date >= last_week)).count()

        result = {
            "books_borrowed_today": books_borrowed_today,
            "books_returned_today": books_returned_today,
            "books_borrowed_this_week": books_borrowed_this_week,
            "books_returned_this_week": books_returned_this_week
        }

        return result

    @staticmethod
    def get_graph_data():
        dates = []
        count = []

        result = {"borrowed": None, "returned": None}

        for i in range(0, 7):
            dynamic_date = datetime.datetime.now() - datetime.timedelta(days=i)
            dynamic_date_start = dynamic_date.replace(hour=0, minute=0, second=0, microsecond=0)
            dynamic_date_end = dynamic_date.replace(hour=23, minute=59, second=59, microsecond=99)

            dates.append(dynamic_date_start.date().__str__())

            books_borrowed = db.session.query(BorrowRecord). \
                filter(BorrowRecord.status == MyEnum.borrowed). \
                filter(and_(BorrowRecord.issue_date >= dynamic_date_start,
                            BorrowRecord.issue_date <= dynamic_date_end)).count()

            count.append(books_borrowed)

        result["borrowed"] = {
            "dates": dates,
            "count": count
        }

        dates = []
        count = []

        for i in range(0, 7):
            dynamic_date = datetime.datetime.now() - datetime.timedelta(days=i)
            dynamic_date_start = dynamic_date.replace(hour=0, minute=0, second=0, microsecond=0)
            dynamic_date_end = dynamic_date.replace(hour=23, minute=59, second=59, microsecond=99)

            dates.append(dynamic_date_start.date().__str__())

            books_borrowed = db.session.query(BorrowRecord). \
                filter(BorrowRecord.status == MyEnum.returned). \
                filter(and_(BorrowRecord.issue_date >= dynamic_date_start,
                            BorrowRecord.issue_date <= dynamic_date_end)).count()

            count.append(books_borrowed)

        result["returned"] = {
            "dates": dates,
            "count": count
        }

        print(result)

        return result


class BookSchema(ma.Schema):
    def __init__(self, strict=True, **kwargs):
        super().__init__(strict=strict, **kwargs)

    class Meta:
        # Fields to expose.
        fields = ("id", "title", "isbn", "published_year", "author", "total_copies", "copies_available")


class BorrowRecordSchema(ma.Schema):
    def __init__(self, strict=True, **kwargs):
        super().__init__(strict=strict, **kwargs)

    class Meta:
        # Fields to expose.
        fields = ("id", "status", "issue_date", "return_date", "actual_return_date")
