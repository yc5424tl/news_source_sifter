from sifter import db


source_categories = db.Table('source_categories', db.Column('source_id', db.Integer, db.ForeignKey('source.id'), primary_key=True), db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)    )


class Source(db.Model):

    __tablename__ = 'source'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    country = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    categories = db.relationship('Category', secondary=source_categories, lazy='subquery', backref=db.backref('sources', lazy=True))

    @property
    def json(self):
        return {
            'name': self.name,
            'country': self.country,
            'language': self.language,
            'url': self.url,
            'categories': [category.json for category in self.categories]
        }


# class CategoryChoice(Enum):
#     BIZ = 'business'
#     ENT = 'entertainment'
#     HLT = 'health'
#     GEN = 'general'
#     SCI = 'science'
#     SPO = 'sports'
#     TEC = 'technology'


class Category(db.Model):

    __tablename__ = 'category'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, blank=False, unique=False)


    @property
    def json(self):
        return {'name': self.name}
