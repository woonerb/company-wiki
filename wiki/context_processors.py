# wiki/context_processors.py
from .models import KnowledgeNode

def sidebar_nodes(request):
    return {'nodes': KnowledgeNode.objects.all().order_by('order')}