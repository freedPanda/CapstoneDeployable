from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import *
import io, base64, math
from base64 import b64encode
from mentions import *

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Visit(db.Model):
    __tablename__ = 'Visit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(db.Text, nullable=False)
    month = db.Column(db.Text, nullable=False)
    year = db.Column(db.Text, nullable=False)

class Mention(db.Model):
    __tablename__='Mention'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #format Jul 8 2020
    date = db.Column(db.Text, nullable=False)
    tweetid = db.Column(db.Text, nullable=False)
    #when entering hashtags, should enter all as one string, seperated by commas
    hashtags = db.Column(db.Text, nullable=True)
    screenname = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=True)

    @classmethod
    def avoid_duplication(cls,api_data):
        new_mentions = []
        for obj in api_data:
            m = ResponseMention(obj)
            mention = Mention(tweetid=m.tweet_id,date=m.date,hashtags=m.hashtags,screenname=m.screen_name, text=m.text)
            new_mentions.append(mention)
        #check to make sure no duplicates are entered into db
        mentions_in_db = db.session.query(Mention.tweetid).all()
        tweet_ids = []
        for mention in mentions_in_db:
            tweet_ids.append(mention[0])
        for mention in new_mentions:
            if mention.tweetid not in tweet_ids:
                db.session.add(mention)
                db.session.commit()
            

#admin table so products can be added or deleted
class Admin(db.Model):
    __tablename__ = 'Admin'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False, unique=False)

    @classmethod
    def register(cls, username, password):
        """Register an admin for admin web portal access

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        admin = Admin(
            username=username,
            password=hashed_pwd
        )

        db.session.add(admin)
        return admin

    @classmethod
    def authenticate(cls, username, password):
        """Find admin with `username` and `password`.

        This is a class method (call it on the class, not an individual admin.)
        It searches for a admin whose password hash matches this password
        and, if it finds such a admin, returns that admin object.

        If can't find matching admin (or if password is wrong), returns False.
        """

        admin = cls.query.filter_by(username=username).first()

        if admin:
            is_auth = bcrypt.check_password_hash(admin.password, password)
            if is_auth:
                return admin.username
            else:
                return False
        return False

#Products table for storing information about products
class Product(db.Model):
    __tablename__ = 'Product'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Integer, nullable=False, unique=False)
    image = db.Column(db.LargeBinary, nullable=False, unique=False)
    image1 = db.Column(db.LargeBinary, nullable=True, unique=False)
    image2 = db.Column(db.LargeBinary, nullable=True, unique=False)
    image3 = db.Column(db.LargeBinary, nullable=True, unique=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    available = db.Column(db.Boolean, nullable=False)
    #size = db.Column(db.Text, nullable=True, default=None)

    request = db.relationship('Request', backref='Product', lazy=True,
    passive_deletes=True)
    Sale = db.relationship('Sale', backref='Product', lazy=True,
    passive_deletes=True)

    def get_image_list(self):
        return [self.image, self.image1, self.image2, self.image3]

    def prepare_to_store(self):
        thing = io.BytesIO(self.image.read())
        self.image = thing.read()
        thing.close()  

        if self.image1:
            thing = io.BytesIO(self.image1.read())
            self.image1 = thing.read()
            thing.close()  
        if self.image2:
            thing = io.BytesIO(self.image2.read())
            self.image2 = thing.read()
            thing.close() 
        if self.image3:
            thing = io.BytesIO(self.image3.read())
            self.image3 = thing.read()
            thing.close() 

    #def convert_to_file(self):


    def prepare_to_show(self):
        f = b64encode(self.image).decode('utf-8')
        self.image = f
        if self.image1:
            f = b64encode(self.image1).decode('utf-8')
            self.image1 = f
        if self.image2:
            f = b64encode(self.image2).decode('utf-8')
            self.image2 = f
        if self.image3:
            f = b64encode(self.image3).decode('utf-8')
            self.image3 = f

    """This static method is used for taking in data from a product
    form and returning a product object for inserting into db"""
    @staticmethod
    def form_to_model(form):

        description = form.description.data
        category = form.category.data
        image = form.image.data
        image1 = form.image1.data
        image2 = form.image2.data
        image3 = form.image3.data
        price = form.price.data
        title = form.title.data
        available=form.available.data

        return Product(image=image, image1=image1,image2=image2,
        image3=image3,category=category,description=description,
        price=price, available=available, title=title)

    def update_product(self,form):

        changeimage = form.changeimage.data
        changeimage1 = form.changeimage1.data
        changeimage2 = form.changeimage2.data
        changeimage3 = form.changeimage3.data
        #check to see if images need to be updated
        if changeimage:
            image = form.image.data
            self.image = self.image_to_bytes(image)
        if changeimage1:
            image1 = form.image1.data
            self.image1 = self.image_to_bytes(image1)
        if changeimage2:
            image2 = form.image2.data
            self.image2 = self.image_to_bytes(image2)
        if changeimage3:
            image3 = form.image3.database
            self.image3 = self.image_to_bytes(image3)

        description = form.description.data
        category = form.category.data
        price = form.price.data
        title = form.title.data
        available=form.available.data

        self.category = category
        self.description = description
        self.price = price
        self.title = title
        self.available = available

    def image_to_bytes(self,image):
        thing = io.BytesIO(image.read())
        image = thing.read()
        thing.close()
        return image

#customer can request to purchase a product via email
class Request(db.Model):
    __tablename__ = 'Request'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    product = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), nullable=False)
    
    @staticmethod
    def form_to_model(form):
        email = form.email.data
        message = form.message.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        product_id = form.product_id.data

        return Request(email=form.email.data, message=message, firstname=firstname, 
        lastname=lastname, product=product_id)


#requests can be converted into sales
class Sale(db.Model):
    __tablename__ = 'Sale'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    product = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), nullable=False)
