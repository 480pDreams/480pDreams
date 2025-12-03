from django import template
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from comments.forms import CommentForm

register = template.Library()


@register.inclusion_tag('comments/partials/comment_section.html', takes_context=True)
def render_comments(context, obj):
    # Get ContentType ID for the object (Game, Hardware, etc)
    content_type = ContentType.objects.get_for_model(obj)

    # Get existing comments
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        active=True
    )

    return {
        'object': obj,
        'comments': comments,
        'content_type': content_type,
        'user': context['user'],
        'comment_form': CommentForm(),
    }