from forms import *
from models import *
class FormsHandle:

    @staticmethod
    def form_to_model(form):
        if isinstance(form,ProductForm) == True:
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

        #elif isinstance(form, EditForm) == True:
