from models import *
from app import app, check_image

db.create_all(bind=None)

def delete_all_records():
    Request.query.delete()
    Product.query.delete()
    Mention.query.delete()
    Visit.query.delete()

def delete_Requests():
    Request.query.delete()
    db.session.commit()

def fill_db():
    add_fake_mentions()
    add_fake_products()
    add_fake_visits()
    add_fake_requests()

def add_fake_visits():
    months_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Nov','Dec']
    visits = []
    for num in range(11):
        visit = Visit(day=str(num),month=months_list[num], year = str(2018))
        db.session.add(visit)
        db.session.commit()
    for num in range(4):
        visit = Visit(day=str(num),month=months_list[num], year = str(2019))
        db.session.add(visit)
        db.session.commit()
    for num in range(8):
        visit = Visit(day=str(num),month=months_list[num], year = str(2020))
        db.session.add(visit)
        db.session.commit()

def add_fake_products():

    image1 = open('testimage1.jpg','rb')
    image1 = check_image(image1)
    image2 = open('testimage2.jpg','rb')
    image2 = check_image(image2)
    for num in range(5):
        product = Product(image=image1, category='box', price=num*2,
        description=f'description gallery {str(num)}', available=False, title=f'title gallery {str(num)}')
        db.session.add(product)
        db.session.commit()
    for num in range(5):
        product = Product(image=image2, image1=image1, price=num*2,
        category='box', description=f'description gallery {str(num)}', available=False, 
        title=f'title gallery {str(num)}')
        db.session.add(product)
        db.session.commit()
    for num in range(5):
        product = Product(image=image1, category='box', price=num*2,
        description=f'description {str(num)}', available=True, title=f'title {str(num)}')
        db.session.add(product)
        db.session.commit()
    for num in range(5):
        product = Product(image=image2, image1=image1, price=num*2,
        category='box', description=f'description  {str(num)}', available=True, 
        title=f'title  {str(num)}')
        db.session.add(product)
        db.session.commit()
    
def add_fake_mentions():
    for num in range(5):
        mention = Mention(date=f'Jun {str(num)} 2020', tweetid=f'{str(num)}', 
        hashtags=f'hash {str(num)}',screenname=f'@someone{str(num)}' , text=f'example text {num}')
        db.session.add(mention)
        db.session.commit()

def add_fake_requests():
    for num in range(5):
        request = Request(email=f'fake{str(num)}@fake.com', firstname=f'name {str(num)}',
        lastname = f'lastname {str(num)}', message=f'fake message {str(num)}', product=num)

