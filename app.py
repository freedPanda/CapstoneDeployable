from flask import Flask, request, make_response, g, send_file, render_template, session, redirect, abort, jsonify, flash
from flask_mail import Mail, Message
#from image import Image
from PIL import Image
from secret import get_route
from forms import AdminForm, ProductForm, PurchaseForm, EditForm, ApiAuth
from models import *
from mentions import ResponseMention
from flask_debugtoolbar import DebugToolbarExtension
import io, base64, math
from base64 import b64encode
import os, os.path
import smtplib
from helpers import Helper
from FormsHandle import FormsHandle
from datetime import date, timedelta
from requests_oauthlib import OAuth1Session
from sqlalchemy.exc import IntegrityError

"""PRODUCTION VS DEVELOPMENT VARIABLES"""

#in production environment this needs to be commented out
#from reallysecret import TW_API_KEY, TW_SECRET_API_KEY

#os.environ.pop('DATABASE_URL')

#uncomment these in development mode. comment out when in production
#consumer_key =  os.environ.get('TW_API_KEY', TW_API_KEY)# Add your API key here
#consumer_secret =  os.environ.get('TW_SECRET_API_KEY', TW_SECRET_API_KEY) # Add your API secret key here

#uncomment these in production mode. comment out when in development
consumer_key =  os.environ['TW_API_KEY']
consumer_secret =  os.environ['TW_SECRET_API_KEY']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///capstone1')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_BINDS'] = {
    #created a bind to update this table
    'Mention': os.environ.get('DATABASE_URL','postgresql:///capstone1')
}

#to recieve emails from customers you must have a gmail account and allow
#3rd party apps to have access to it. Best to create a completely different
#gmail account for this website.
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config['WTF_CSRF_ENABLED'] = True

CURR_USER_KEY = 'username'

app.config.update(mail_settings)
mail = Mail(app)
mail.connect()

connect_db(app)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = Admin.query.filter_by(username=session[CURR_USER_KEY])
        #the following code will make sure the admin is automatically logged out after
        #15min
        app.permanent_session_lifetime = timedelta(minutes=15)

    else:
        g.user = None


def do_login(admin):
    """Log in admin."""

    session[CURR_USER_KEY] = admin


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def home_page_1():
    return render_template('index.html')
@app.route('/index')
def home_page():
    """This route will need to return the home page for now"""
    return render_template("index.html") 

@app.route('/products') 
def return_products_page():
    products = Product.query.filter_by(available=True).all()
        
    for product in products:
        product.prepare_to_show()
    for product in products:
        product.available = 'Available'

    organized_products = Helper.organize_products(products)
    return render_template('products2.html',rows=organized_products)

@app.route('/gallery')
def show_gallery():
    products = Product.query.filter_by(available=False).all()
    for product in products:
        product.prepare_to_show()
    organized_products = Helper.organize_products(products)
    return render_template('gallery.html',rows=organized_products)

@app.route('/gallery/<product_id>')
def show_gallery_product(product_id):
    product = Product.query.get(product_id)
    product.prepare_to_show()

    return render_template('gallery-product.html', product=product) 

@app.route('/products/<product_id>', methods=['GET', 'POST'])
def return_product_details(product_id):
    """This isnt actually purchasing a product. This is just notifying
    the website owner that a customer wants to purchase a product or has
    questions about a product."""
    form=PurchaseForm()
    if form.validate_on_submit():
        request = Request.form_to_model(form)
        email = []
        email.append(request.email)
        result = ''
        try:
            send_email(request.message)
        except:
            print('GOOGLE ACCOUNT SETTINGS FOR LESS SECURE APP SHOULD BE ENABLED')
            print('GOOGLE ACCOUNT SETTINGS THE DEVICE SHOULD VERIFIED FOR USE')
        
        result = send_confirmation(email)
        
        print(result)
        
        if result == 535:
            print('GOOGLE ACCOUNT SETTINGS FOR LESS SECURE APP SHOULD BE ENABLED')
            print('GOOGLE ACCOUNT SETTINGS THE DEVICE SHOULD VERIFIED FOR USE')
        elif result == False:  
            flash('Error. Invalid email address.','danger')
            return redirect(f'/products/{product_id}')
        #request = Request(email=form.email.data, message=message, firstname=firstname, lastname=lastname, product=product_id)
        db.session.add(request)
        db.session.commit()
        return redirect(f'/request/{product_id}')
    product = Product.query.get(product_id)

    #need to convert an image for html to display
    product.prepare_to_show()
          
    product.available = 'Available'

    form.product_id.data = product.id

    return render_template('product.html', product=product, form=form)


@app.route('/request/<product_id>')
def confirm_request(product_id):
    product = Product.query.get(product_id)
    #prepare image to be displayed in web browser
    product.prepare_to_show()
    return render_template('confirm.html', product=product)

@app.route('/events')
def return_events_page():
    return render_template('events.html')

@app.route('/contact')
def contact_page():

    return render_template('contact.html')

#---------------------------ADMIN  ROUTES-------------------------------------------------------
#-------ADMIN LOGIN
@app.route(f'/{get_route()}', methods=['POST','GET'])
def admin():
    
    form = AdminForm()
    if form.validate_on_submit():
                
        username = form.username.data
        password = form.password.data
        #authenticate returns the username
        admin = Admin.authenticate(username,
                                    password)

        if admin:
            do_login(admin)
            return redirect(f'/{get_route()}/admin-home')
        else:
            return render_template('admin-login.html', form=form)

     #if admin not logged in then show the login form       
    if not g.user:
        return render_template('admin-login.html', form=form)
    #if admin logged in the show admin home
    else:
        return redirect(f'{get_route()}/admin-home')
    

@app.route(f'/{get_route()}/admin-home')
def admin_home():
    if not g.user:
        return redirect('/')

    tweet_stats = get_tweet_stats()
    mention_info = Mention.query.all()
    return render_template('admin.html', route=get_route(), data = tweet_stats, mention_info = mention_info)

@app.route(f'/{get_route()}/admin-logout')
def admin_logout():

    if not g.user:
        return redirect('/')

    do_logout()
    return redirect('/')
#-------ADMIN VIEW ALL PRODUCTS AND ADD
@app.route(f'/{get_route()}/view-products', methods=['POST', 'GET'])
def admin_products():
    if not g.user:
        return redirect('/')
    
    else:
        products = Product.query.all()
        form = ProductForm()
        #add product to db
        if form.validate_on_submit():
            product = Product.form_to_model(form)
            #converting images into bytes like object
            #prepare images to be stored
            product.prepare_to_store()
            db.session.add(product)
            db.session.commit()

            flash('Product added to database','success')
            return redirect(f'/{get_route()}/view-products')

        else:
            
            for product in products:
                if product.available:
                    product.availabile = 'Available'
                else:
                    product.availabile = 'Sold'
            for product in products:
                product.prepare_to_show()
            organized_products = Helper.organize_products(products)
            return render_template('view-products.html', form=form, rows=organized_products, route=get_route())
   
#---------ADMIN EDIT PRODUCT
@app.route(f"/{get_route()}/<int:product_id>", methods=['GET','POST'])
def edit_product(product_id):
    #view and edit a product
    if not g.user:
        return redirect('/')

    else:
        method = request.method
        product = Product.query.get(product_id)
        
        form = EditForm(obj=product)
        if form.validate_on_submit():
            product.update_product(form)
            
            db.session.add(product)
            db.session.commit()
            return redirect(f'/{get_route()}/{product.id}')
            
        else:
            #prepare an image for display
            product.prepare_to_show()
            availability = 'Sold'
            if product.available:
                availability = 'Available'
            
            return render_template('admin-products-edit.html', product = product, form=form, route=get_route(), availability=availability)
    

@app.route(f"/{get_route()}/delete/<int:product_id>")
def delete_product(product_id):
    if not g.user:
        return redirect('/')
    
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(f'/{get_route()}/view-products')

#--------Request routes
@app.route(f'/{get_route()}/view-requests')
def admin_requests():
    if not g.user:
        return redirect('/')
    
    requests = db.session.query(Product,Request).join(Request, Product.id == Request.product).all()
    #issue here is that the image has already been decoded
    for request in requests:
        print(request[0],request[1])
        if isinstance(request[0].image,str) == False:
            request[0].image = prepare_animage(request[0].image)
    return render_template('admin-requests.html', requests=requests, route=get_route())

@app.route(f'/{get_route()}/delete/request/<request_id>')
def delete_request(request_id):
    if not g.user:
        return redirect('/')
    else:
        request = Request.query.get(request_id)
        db.session.delete(request)
        db.session.commit()
        return redirect(f'/{get_route()}/view-requests')

@app.route(f'/{get_route()}/sold/<request_id>')
def sold_product(request_id):
    if not g.user:
        return redirect('/')
    else:
        request = Request.query.get(request_id)
        product = Product.query.get(request.product)
        if product.available == True:
            sale = Sale(firstname=request.firstname, lastname=request.lastname,
            email=request.email,product=product.id)
            product.available = False
            db.session.add(product)
            db.session.add(sale)
            db.session.delete(request)
            db.session.commit()
            return redirect(f'/{get_route()}/view-requests')
        else:
            flash('Product has already been sold. Delete this request and notify buyer.','danger')
            return redirect(f'/{get_route()}/view-requests')
#----------Sales routes
@app.route(f'/{get_route()}/sales')
def view_sales():
    if not g.user:
        return redirect('/')
    sales = db.session.query(Product,Sale).join(Sale, Product.id == Sale.product).all()
    for sale in sales:
        sale[0].image = prepare_animage(sale[0].image)
    return render_template('admin-sales.html', sales=sales, route=get_route())
   

#---------admin event route-------
@app.route(f'/{get_route()}/view-events')
def admin_events():
    if not g.user:
        return redirect('/')
        
    return render_template('admin-events.html')
    

#-------------------------------IMAGE URLS--------------------------------------------------
@app.route(f'/images/<product_id>')
def retrieve_image(product_id):
    """Use this route to determine what image is shown in a tweet or
    facebook post."""
    with app.open_resource(f'{os.getcwd()}/static/images/desk.jpg') as f:
        contents = f.read()
        response = make_response(contents)
        response.headers.set('Content-Type', 'image/jpg')
        response.headers.set(
        'Content-Disposition', 'attachment', filename=f'fb_post.jpg')
        return response

#------------------------------TWITTER API------------------------------------

@app.route(f'/{get_route()}/mentions', methods =['GET','POST'])
def get_mention_data():
    if not g.user:
        return redirect('/')
    else:    
        form = ApiAuth()
        if form.validate_on_submit():
            verifier = str(form.code.data)
            resource_owner_secret=session['ros']
            resource_owner_key = session['rok']
            access_token_url = 'https://api.twitter.com/oauth/access_token'
            oauth = OAuth1Session(consumer_key,
                            client_secret=consumer_secret,
                            resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret,
                            verifier=verifier)
            oauth_tokens = oauth.fetch_access_token(access_token_url)

            access_token = oauth_tokens['oauth_token']
            access_token_secret = oauth_tokens['oauth_token_secret']

            # Make the request
            oauth = OAuth1Session(consumer_key,
                            client_secret=consumer_secret,
                            resource_owner_key=access_token,
                            resource_owner_secret=access_token_secret)
            #get list of 20 most recent mentions
            response = oauth.get("https://api.twitter.com/1.1/statuses/mentions_timeline.json")
            jsondata = response.json()
            Mention.avoid_duplication(jsondata)

            return redirect(f'/{get_route()}/admin-home')

        else:
            # Get request token
            request_token_url = "https://api.twitter.com/oauth/request_token"
            oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
            fetch_response = oauth.fetch_request_token(request_token_url)
            resource_owner_key = fetch_response.get('oauth_token')
            resource_owner_secret = fetch_response.get('oauth_token_secret')

            # # Get authorization
            base_authorization_url = 'https://api.twitter.com/oauth/authorize'
            authorization_url = oauth.authorization_url(base_authorization_url)
            #print('Please go here and authorize: %s' % authorization_url)
            #verifier = input('Paste the PIN here: ')
            session['rok']=resource_owner_key
            session['ros']=resource_owner_secret
            return render_template('apiauth.html', url=authorization_url, form=form)
    

#---------------------------DATA ROUTE--------------------------
@app.route('/datevst', methods=['POST'])
def shared_site():
    """This route is for the script called externalApis.js. The
    script uses axios requests to log each time some tweets this 
    website using the tweet button."""
    v_date = request.json['solut']
    if isinstance(v_date, str):
        sep = v_date.split()
        todaydate = date.today()
        todaydate = todaydate.strftime("%b-%d-%Y")
        todaydate = todaydate.replace('-',' ')
        sep2 = todaydate.split()
        allgood = False
        if sep[0] == sep2[0]:
            if sep[1] == sep2[1]:
                if sep[2] == sep2[2]:
                    visit = Visit(day = sep[1], month=sep[0], year=sep[2])
                    db.session.add(visit)
                    db.session.commit()
                    return jsonify('success', 201)
        return jsonify('nothing', 201)
    else:
        return jsonify('nothing', 201)

def get_tweet_stats():
    #instead get year month day in a tuple, then make an array of years,
    #then make an array of months
    stat_package = {}
    months_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    visits = db.session.query(Visit.year, Visit.month)
    for visit in visits:
        if (visit.year) not in stat_package.keys():
            #stat_package.append({visit.year:[]})
            stat_package[visit.year] = {}
            for month in months_list:
                year = stat_package[visit.year][month] = 0
                #if visit.month == stat_package[vi]
            stat_package[visit.year][visit.month] += 1
        else:
            stat_package[visit.year][visit.month] += 1
    """
    distinct_years = Visit.query.distinct(Visit.year)
    package = []
    for dyears in distinct_years:
        package.append({dyears.year:[]})
    months_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Nov','Dec']
    foears.items():
            for month in monthr years in package:
        for (year,months) in ys_list:
                months.append({month:Visit.query.filter_by(year=year,month=month).count()})
    """
    return stat_package            

"""Helper functions"""

#used when an image is being taken out of the database
def prepare_animage(image):
    f = b64encode(image).decode('utf-8')
    image = f
    return image

#a function that is in development
def bytes_to_image(image,id):
    save_path = f'{os.getcwd()}/storage'
    if image:
        #str = base64.b64encode(imageFile.read())
        #folder_location = 'storage'
        #/Users/christopherhjorth/Desktop/ClearStone/EvaHjortSite/storage
        #print(os.getcwd())
        current = f'current{id}.png'
        complete_path = os.path.join(save_path, current)
        f = open(os.path.join(save_path, current),'wb')
        #somef = b64encode(image).decode('utf-8')
        newf = f.write(image)
        
        f.close()
        return newf
    else:
        return None    

#------this method notifies owner of a potential product purchase
def send_email(body):
    with app.app_context():
        msg = Message(subject="Product Request",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[app.config.get("MAIL_USERNAME")], # replace with your email for testing
                      body=body)
        mail.send(msg)
            

#------this method confirms requestor that the request has been sent
def send_confirmation(recipients):
    with app.app_context():
        try:
            msg = Message(subject="Thank you for inqiury!",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=recipients, # replace with your email for testing
                      body='Thank you for sending a request to purchase a piece of art! This message is to confirm that your request has been sent and we will response as soon as possible! Thank you and have a wonderful day!')
            mail.send(msg)
            return True
        except smtplib.SMTPAuthenticationError as err:
            print(err)
            return 535
        except Exception as err1:
            print(err1)
            return False
