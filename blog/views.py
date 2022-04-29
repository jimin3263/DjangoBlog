# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView

from blog.forms import CommentForm
from blog.models import Post, Category, Tag


class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm

        return context

# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/index.html',
#         {
#             'posts': posts,
#         }
#     )
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/single_post_page.html',
#         {
#             'post': post,
#         }
#     )

def show_category_post(request, slug):

    if slug == 'no-category':
        category = "미분류"
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    context = {
        'categories' : Category.objects.all(),
        'category_less_post_count' : Post.objects.filter(category=None).count(),
        'category': category,
        'post_list': post_list
    }

    return render(request, 'blog/post_list.html', context)

def show_tag_post(request, slug):

    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    context = {
        'categories' : Category.objects.all(),
        'category_less_post_count' : Post.objects.filter(category=None).count(),
        'tag': tag,
        'post_list': post_list
    }

    return render(request, 'blog/post_list.html', context)

class PostCreate(LoginRequiredMixin, CreateView, UserPassesTestMixin):
    model = Post
    fields = ['title', 'hook', "content", "head_image", "attached_file", "category"] #입력받을 요소들

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user

        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author= current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook', "content", "head_image", "attached_file", "category"]

    template_name = 'blog/post_form_update.html'

    def dispatch(self, request, *args, **kwargs):
        if(request.user.is_authenticated and request.user == self.get_object().author):
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form =CommentForm(request.POST)
            if comment_form.is_valid():
                comment= comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        return PermissionDenied