from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, Follow, SavedPost, Like, Comment
from .decorators import redirect_authenticated_user
from random import sample
import json

# Create your views here.

@login_required(login_url='login')
def index(request):
    # Fetch the user's profile
    user_profile = Profile.objects.get(user=request.user)
    
    # Fetch the posts of the user and the people they follow
    following_users = user_profile.user.following.all()  
    posts = Post.objects.filter(author__in=following_users.values('following')) | Post.objects.filter(author=request.user)
    posts = posts.order_by('-created_at')
    
    latest_posts = posts[:5]

    more_posts_exist = posts.count() > 5

    users_to_suggest = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)
    users_to_suggest = users_to_suggest.exclude(id__in=[user['following'] for user in following_users.values('following')])
    suggested_users = sample(list(users_to_suggest), min(4, users_to_suggest.count()))  # Pick random users, at most 4

    context = {
        'user_profile': user_profile,
        'posts': latest_posts, 
        'more_posts_exist': more_posts_exist,
        'suggested_users': suggested_users,
    }
    
    return render(request, 'index.html', context)

@login_required(login_url='login')
def fetch_posts(request):
    user = request.user
    
    # Get all posts from the logged-in user and the users they follow
    following_users = user.following.all() 
    following_users_posts = Post.objects.filter(author__in=following_users.values('following'))
    own_posts = Post.objects.filter(author=user)

    all_posts = (following_users_posts | own_posts).order_by('-created_at')

    # Set up pagination
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page', 1)  
    page_obj = paginator.get_page(page_number)

    # Prepare posts data
    posts_data = []
    for post in page_obj:
        post_data = {
            'id': post.id,
            'author': post.author.username,
            'caption': post.caption,
            'image_url': post.image.url,
            'likes_count': post.total_likes(),
            'comments_count': post.total_comments(),
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        posts_data.append(post_data)

    # Prepare the JSON response
    response_data = {
        'posts': posts_data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    }

    return JsonResponse(response_data)


@login_required(login_url='login')
def upload(request):

    if request.method == 'POST':
        user = request.user
        image = request.FILES.get('image')
        caption = request.POST['caption']

        new_post = Post.objects.create(author=user, image=image, caption=caption)
        new_post.save()
    # redirecting to home is fine as it will show new post
    return redirect('/')

@login_required(login_url='login')
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        return redirect('/') 
    except Profile.DoesNotExist:
        return redirect('/')  

    user_posts = Post.objects.filter(author=user)
    user_posts = user_posts.order_by('-created_at')
    number_of_posts = user_posts.count() 

    # Get the list of followers and following
    user_followers = user.followers.all()
    user_following = user.following.all()

    # Check if the logged-in user is following this user
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    # Set button text based on whether the user is already following or not
    if is_following:
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    # Create the context to pass to the template
    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'number_of_posts': number_of_posts,
        'button_text': button_text,
        'user_followers': user_followers.count(),
        'user_following': user_following.count(),
    }

    return render(request, 'profile.html', context)

@login_required(login_url='login')
def saved(request):
    user_profile = Profile.objects.get(user=request.user)
    saved_posts = SavedPost.objects.filter(user=request.user)

    return render(request, 'saved.html', {'user_profile': user_profile, 'saved_posts': saved_posts})

@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.avatar
        else:
            image = request.FILES.get('image')
        
        bio = request.POST['bio']

        user_profile.avatar = image
        user_profile.bio = bio
        user_profile.save()

        # would decide later if redirect to somewhere else
        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='login')
def search(request):
    user_profile = Profile.objects.get(user=request.user)

    search = ''
    searched_profiles = [] 

    if request.method == 'POST':
        search = request.POST['search']
        
        searched_users = User.objects.filter(username__icontains=search).exclude(id=request.user.id)
        
        searched_profiles = Profile.objects.filter(user__in=searched_users)

    return render(request, 'search.html', {'user_profile': user_profile, 'searched_profiles': searched_profiles, 'search': search})

@redirect_authenticated_user
def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm-password']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                if user_login is not None:
                    auth.login(request, user_login)
                else:
                    messages.error(request, 'Authentication failed.')
                    return redirect('signup')

                new_profile = Profile.objects.create(user=user)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')

@redirect_authenticated_user
def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user_login = auth.authenticate(username=username, password=password)

        if user_login is not None:
            auth.login(request, user_login)
            return redirect('/')
        else: 
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
    else:
        return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def single_post_view(request, post_id):
    post = Post.objects.get(id=post_id)
    author_profile = post.author.profile
    comments = post.comments.select_related('user').order_by('-created_at')
    likes_count = post.total_likes()
    comments_count = post.total_comments()

    is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
    is_liked = Like.objects.filter(user=request.user, post=post).exists()


    context = {
        'post': post,
        'author_profile': author_profile,
        'comments': comments,
        'likes_count': likes_count,
        'comments_count': comments_count,
        'is_saved': is_saved,
        'is_liked': is_liked,
    }

    return render(request, 'postmodal.html', context)

@login_required(login_url='login')
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    like_obj, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.total_likes(),
    })


@login_required(login_url='login')
def save(request, post_id):
    post = Post.objects.get(id=post_id)
    saved_obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)

    if not created:
        saved_obj.delete()
        saved = False
    else:
        saved = True

    return JsonResponse({
        'saved': saved,
    })

@login_required(login_url='login')
def comment(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment_text = data.get('comment')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(user=request.user, post=post, comment=comment_text)
        return JsonResponse({
            'username': comment.user.username,
            'comment':  comment.comment,
            'comments_count': post.total_comments()
        })
    return JsonResponse({
        'error': 'Only POST request is allowed'
    }, status=405)

@login_required(login_url='login')
def follow(request, username):
    following = User.objects.get(username=username)
    followed_obj, created = Follow.objects.get_or_create(follower=request.user, following=following)

    if not created:
        followed_obj.delete()

    return redirect('profile', username=username)

    