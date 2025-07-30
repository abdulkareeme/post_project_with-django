from django_filters import rest_framework as filters
from .models import Post


class PostFilter(filters.FilterSet) :
    title = filters.CharFilter(lookup_expr='icontains')
    content= filters.CharFilter(lookup_expr='icontains')
    author__name = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateFilter(field_name='created_at',lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at',lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['title' , 'content' , 'author__name']