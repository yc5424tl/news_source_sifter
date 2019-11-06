
from sifter import db


categories = db.Table('source_categories',
                      db.Column('source_id', db.Integer, db.ForeignKey('source.id'), primary_key=True),
                      db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True))


class Source(db.Model):

    __tablename__ = 'source'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    country = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(255), nullable=False)
    categories = db.relationship('Category', secondary=categories, lazy='subquery', backref=db.backref('sources', lazy=True))

    # def __init__(self, name: str, country: str, language: str):
    #     self._name = name
    #     self._country = country
    #     self._language = language
    #     self._categories = categories
    # def __str__(self):
    #     return f'{self.name}, {self.country}, {self.language}'

    @property
    def json(self):
        return {
            'name': self.name,
            'country': self.country,
            'language': self.language,
            'categories': [category.name for category in self.categories]
        }




class Category(db.Model):

    __tablename__ = 'category'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    # def __init__(self, name: str):
    #     self._name = name

    # def __repr__(self):
    #     return f'{self._name}'