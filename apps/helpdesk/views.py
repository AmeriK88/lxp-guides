from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, render
from .models import HelpCategory, HelpArticle


def helpdesk_view(request):
    q = (request.GET.get("q") or "").strip()

    # Base: solo categorías activas
    categories_qs = HelpCategory.objects.filter(is_active=True)

    # Base: solo artículos publicados
    articles_qs = HelpArticle.objects.filter(is_published=True)

    # Si hay búsqueda, filtra artículos por title/content
    if q:
        articles_qs = articles_qs.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        )

        # Opcional pero recomendado: solo categorías que tengan resultados
        categories_qs = categories_qs.filter(articles__in=articles_qs).distinct()

    # Prefetch SOLO los artículos filtrados y los guarda en "filtered_articles"
    categories = categories_qs.prefetch_related(
        Prefetch("articles", queryset=articles_qs.order_by("-is_featured", "title"), to_attr="filtered_articles")
    ).order_by("order", "name")

    search_cfg = {
        "title": "¿En qué podemos ayudarte?",
        "subtitle": "Busca por palabras clave: cancelación, cambios, pagos, reservas…",
        "badge": "🔍 Ayuda",
        "action_url": request.path,
        "query_label": "¿Qué necesitas?",
        "query_placeholder": "cancelación, cambio de fecha, reembolso...",
        "button_text": "Buscar en el centro de ayuda",
        "show_price": False,
        "show_duration": False,
        "helper_text": None,
    }

    return render(request, "helpdesk/helpdesk.html", {
        "categories": categories,
        "q": q,
        "search_cfg": search_cfg,
    })


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
