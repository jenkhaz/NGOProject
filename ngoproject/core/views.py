from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random

# Create your views here.

@login_required(login_url='signin') #this is just so the user can't access if they're not logged in
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    #used object of currently logged in user to get profile to use attributes of it
    
    user_following_list = [] #list of all users the user is following
    feed = [] #to include only posts of people the user is following
    
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    
    for users in user_following:
        user_following_list.append(users.user)
        
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    
    feed_list = list(chain(*feed))
    
    #user suggestions:
    all_users = User.objects.all()
    user_following_all = []
    
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username = request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list) #so they can be random
    
    username_profile = []
    username_profile_list = []
    
    for users in final_suggestions_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_list = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_list)
        
    suggestions_username_profile_list = list(chain(*username_profile_list))
        
    #posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def upload(request):
    
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url="signin")
def search(request):
    
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username) #a list of all objects that contain the username
        
        username_profile = []
        username_profile_list = []
        
        for users in username_object:
            username_profile.append(users.id)    

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
        
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    
    post = Post.objects.get(id=post_id)
    
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    #this makes sure the object exists
    
    if like_filter == None: #like the post
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
    
    else: #unlike the post
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
    
    return redirect('/')
    
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts) #to get the nb of posts
    
    follower = request.user.username
    user = pk
    
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = "Follow"
        
    user_followers = len(FollowersCount.objects.filter(user=pk)) #pk is the user who's profile is being looked at
    user_following = len(FollowersCount.objects.filter(follower=pk))
        
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    
    return render(request, 'profile.html', context)
    
@login_required(login_url = 'signin')
def follow(request):
    
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        
        #to unfollow
        if FollowersCount.objects.filter(follower = follower, user = user).first(): 
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        
        #to follow
        else: 
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            
        return redirect('/profile/'+user) #redirect to user's page
            
    else:
        return redirect('/')

@login_required(login_url='signin') #can't access settings if not logged in
def settings(request):
    
    try:
        user_profile = Profile.objects.get(user=request.user) #getting profile object of that specific user
    #     return render(request, 'setting.html',{'user_profile': user_profile})
    except Profile.DoesNotExist:
        print("Profile does not exist")
        user_profile = Profile.objects.create(user=request.user)
   
   # user_profile = Profile.objects.get(user=request.user) #getting profile object of that specific user
    if request.method == 'POST':
        bio = request.POST['bio']
        location = request.POST['location']
           
        user_profile.bio = bio
        user_profile.location = location
           
        if request.FILES.get('image') == None:
           image = user_profile.profileimg    
           
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
           
        user_profile.profileimg = image
        user_profile.save()
            
        return redirect('settings')
    
    return render(request, 'setting.html',{'user_profile': user_profile}) #the last one passes it into our html

def signup(request):
    if request.method == 'POST':
        username = request.POST['username'] #gonna get value of that data using name of the input
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if (password == password2):
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken!')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                #log user in and redirect to settings page
                    #automatically log user in
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings') #redirect to settings page (to finalize their profile info)
                
        else:
            messages.info(request, 'Passwords are not a match!')
            return redirect('signup')
                
    else:
        return render(request, 'signup.html')

def signin(request):
    
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None: 
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials invalid!')
            return redirect('signin')
        
    else:
        return render(request, 'signin.html')
    
@login_required(login_url='signin') #have to be logged in to log out
def logout(request):
    auth.logout(request)
    return redirect('signin')