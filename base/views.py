from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from django.contrib.auth import authenticate,login,logout
from . forms import RoomForm,UserForm,MyUserCreationForm


# Create your views here.
 
def loginPage(request):
    page='login'

    if request.user.is_authenticated:
        return redirect ('home')

    if request.method =="POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,"email does not exist.")

        user = authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"email OR Password Does Not Exit")

        

    context = {"page":page}
    return render(request,"base/login_register.html",context)


def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form =MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            # commit=False freeze the saving user process but user is created
            # and we can access the user now we can clean the user before saving
            # by converting the username in lowercase ,we do the same to login
            user.username = user.username.lower()
            form.save()
            login(request,user)
            return redirect ('home')
        else:
            messages.error(request,"An error has occurred during the registeration.")
    context={"form":form}
    return render(request,'base/login_register.html',context)


def home(request):
    # Here we are using inline condition
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms = Room.objects.filter(topic__name__icontains=q)

    # here we are searching by topic name but we want to search by room
    # name too and by description too, one way is that we can do is :
        # rooms = Room.objects.filter(topic__name__icontains=q,description__icontains=q)
    # but in this method our search much have both of them to give result 
    # so here we are gonna use lookups which help us to use "OR" "AND" in Filters
    # so lets import our lookup as "Q" and wrap search parameters with it 

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # now we can search by either of the above mentioned search parameters
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {"rooms":rooms,"topics":topics,"room_count":room_count,"room_messages":room_messages}
    return render(request,'base/home.html',context)


def room(request,pk):
    room = Room.objects.get(id=pk)
    # room_messages = room.message_set.all().order_by('-created')
    # we do this ordering in models.py
    room_messages = room.message_set.all()
    participants = room.participants.all()
    # for one-to-many we used modelname_set.all()
    # for many-to-many we used all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        # if the user message in room it will be added in the participants of that room
        return redirect('room',pk=room.id)
        # it will go to the room page even if we dont redirect it to room
        # page but b/c of POST it could cause issue,so we will redirect it 
        # and also give "pk=room.id" b/c in room page url there is pk argument
    context = {"room":room,"room_messages":room_messages,"participants":participants}
    return render(request,'base/room.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')

        # print(request.POST)
        # form = RoomForm(request.POST)
        # we cant use modelform here
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()

    context={'form':form,"topics":topics}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def updateRoom(request,pk):
    page = "update"
    room = Room.objects.get(id=pk)
    print(room.topic)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()


    if request.user != room.host:
        return HttpResponse("You are not authorized to view this page.")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context={'form':form,"topics":topics,"room":room,"page":page}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        HttpResponse("You are not authorized to view this page.")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context={'obj':room}
    return render(request,'base/delete_form.html',context)


@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        HttpResponse("You are not authorized to view this page.")
    
    if request.method == 'POST':
        message.delete()
        return redirect('room',pk=message.room.id)
    
    context={'obj':message}
    return render(request,'base/delete_form.html',context)


@login_required(login_url='login')
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={"user":user,"rooms":rooms,"room_messages":room_messages,"topics":topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    context = {"form":form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context={"topics":topics}
    return render(request,'base/topics.html',context)


def activityPage(request):
    room_messages=Message.objects.all()
    context={"room_messages":room_messages}
    return render(request,'base/activity.html',context)

