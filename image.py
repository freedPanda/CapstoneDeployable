import io, base64
from base64 import b64encode

class Images():
    def __init__(self, image, description, title, id):
        self.image = image
        self.description = description
        self.title = title
        self.id = id
        self.images

    #this is used to prepare image file to store into database
    #typically this is used so the db can store the image data
    def prepare_to_store(self):
        for image in self.images:
            #converting to bytes like object
            thing = io.BytesIO(image.read())
            image = thing.read()
            thing.close()  

    def get_image(self, index):
        if index < len(self.images) - 1:
            return self.images[index]

    #this is used to covert bytes like object to an image file to be used in a web browser
    #typically this is used when an image will be displayed
    def prepare_to_show(self):
        for image in self.images:
            f = b64encode(image).decode('utf-8')
            image = f

    #this is used when a product object is provided
    @staticmethod
    def product_imaging(product):
        product.image = prepare_animage(product.image)
        if product.image1:
            product.image1 = prepare_animage(product.image1)
        if product.image2:
            product.image2 = prepare_animage(product.image2)
        if product.image3:
            product.image3 = prepare_animage(product.image3)
    @staticmethod
    def prepare_animage(image):
        f = b64encode(image).decode('utf-8')
        image = f
        return image