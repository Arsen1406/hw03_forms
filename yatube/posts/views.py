from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from .models import Post, Group, User
from .forms import PostForm

COUNT_PAGE = 10

def paginator_func(request, post_list, count_page):
    pag = Paginator(post_list, count_page)
    page_number = request.GET.get('page')
    paginator = pag.get_page(page_number)
    return paginator

def index(request):
    main = "Последние обновления на сайте"
    post_list = Post.objects.order_by('-pub_date')
    page_obj = paginator_func(request, post_list, COUNT_PAGE)
    context = {
        'page_obj': page_obj,
        'main': main
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = paginator_func(request, posts, COUNT_PAGE)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')
    count = Post.objects.filter(author=author).aggregate(Count('pk'))
    posts_other = Post.objects.exclude(author=author)
    page_obj = paginator_func(request, posts, COUNT_PAGE)
    context = {
        'page_obj': page_obj,
        'posts_other': posts_other,
        'count': count,
        'author': author,
        'posts': posts
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    count = Post.objects.filter(author_id=post.author_id).aggregate(
        Count('pk')
    )
    context = {
        'count': count,
        'post': post,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    group = Group.objects.all()
    user = request.user
    main = 'Создать пост от имени'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.pub_date = timezone.now()
        post.save()
        return HttpResponseRedirect(f'/profile/{user.username}/')

    context = {
        'main': main,
        'user': user,
        'is_edit': False,
        'group': group,
        'form': form
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    group = Group.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    main = 'Редактировать пост'
    group_set = post.group
    if request.user.id == post.author_id:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = timezone.now()
            post.save()
            return HttpResponseRedirect(f'/posts/{post_id}')
        else:
            form = PostForm(instance=post)
    else:
        return HttpResponseRedirect(f'/posts/{post_id}')
    context = {
        'group_set': group_set,
        'group': group,
        'main': main,
        'post': post,
        'form': form,
        'is_edit': True,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)
