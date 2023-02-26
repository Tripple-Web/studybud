from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")
    # default image is important, let say user have the image 
    # but then they delete it now we dont have any image which
    # will give error even tho we have null=True  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

     

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):

    # when u use "models.SET_NULL" then u have to use "null=True"
    # class Topic is parent of room class that y it is on top of room
    # if topic class were below room class then we have to write like this
    # topic = models.ForeignKey('Topic',on_delete=models.SET_NULL, null=True)
    # in above line u have to put Topic in string if topic class in below room class
    
    host = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    participants = models.ManyToManyField(User, related_name='Participants',blank=True)
    # In the host field we have already created the relation with User model so
    # if we have to make relation with User model again the we  must specify
    # "related_name" ,we can give related-name generally to all ,i think to save ourself 
    # for confusing database but here it is necessary. Use to blank to avoid form submition problems.

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # auto_now take screenshot every time field value changes
    # auto_now_add take screenshot when field was first created

    
    class Meta:
        ordering = ['-updated','-created']

 
        #   not working i dont know y, 
        # it was working fine in tutorial
        # ordering = ['topic']
    
    def __str__(self):
        return self.name

    


class Message(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
    body = models.TextField()

    # auto_now take screenshot evertime a thing get change 
    # auto_now_add take screenshot just at when it is created 

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):

        # we are slicing body to 50 words

        return self.body[0:50]