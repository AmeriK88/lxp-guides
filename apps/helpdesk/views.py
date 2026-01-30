from django.shortcuts import get_object_or_404, render
from .models import HelpCategory, HelpArticle


def helpdesk_view(request):
    categories = HelpCategory.objects.filter(is_active=True).prefetch_related("articles")
    return render(request, "helpdesk/helpdesk.html", {"categories": categories})


def article_detail(request, slug):
    article = get_object_or_404(
        HelpArticle.objects.select_related("category"),
        slug=slug,
        is_published=True,
        category__is_active=True,
    )

    related = (
        HelpArticle.objects.filter(category=article.category, is_published=True)
        .exclude(pk=article.pk)
        .order_by("-is_featured", "title")[:6]
    )

    return render(
        request,
        "helpdesk/article_detail.html",
        {"article": article, "related": related},
    )
