from configuration import db, ma
from sqlalchemy import ForeignKey, Enum, or_


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

    @staticmethod
    def get_stats():
        result = Book.query.filter(Book.id.status("borrowed")).all()

        # session.query(MyTable.col1).count()

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
    status = db.Column(Enum('borrowed', 'returned'))
    issue_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    actual_return_date = db.Column(db.DateTime)


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
        fields = ("id", "status", "issue_date", "return_date", "actual return date")
