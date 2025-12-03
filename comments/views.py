from django.shortcuts import redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CommentForm


@login_required
@require_POST
def add_comment(request, content_type_id, object_id):
    content_type = get_object_or_404(ContentType, id=content_type_id)
    # We verify the object exists
    obj = get_object_or_404(content_type.model_class(), id=object_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.content_object = obj
        comment.save()

    # Bounce user back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', '/'))