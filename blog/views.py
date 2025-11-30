from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    # Only show published posts
    posts = Post.objects.filter(is_published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    # Allow viewing unpublished drafts if you are staff
    if request.user.is_staff:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post, slug=slug, is_published=True)

    return render(request, 'blog/post_detail.html', {'post': post})