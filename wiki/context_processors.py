# wiki/context_processors.py
from .models import Node

def sidebar_nodes(request):
    return {'nodes': Node.objects.all().order_by('order')}