from django.urls import path
from .views import neptune_visualization_view,gremlin_search,add_system_view,add_dependency_view,edit_system_view, delete_system_view
from . import views

urlpatterns = [
    path('neptune-data/', neptune_visualization_view, name='neptune_data'),   
    path('gremlin-search/', gremlin_search, name='gremlin_search'),
    path('add-system/', add_system_view, name='add_system'),
    path('add-dependency/', add_dependency_view, name='add_dependency'),
    path('edit-system/', edit_system_view, name='edit_system'),
    path('delete-system/', delete_system_view, name='delete_system'),
    # Add other URL patterns as needed
]