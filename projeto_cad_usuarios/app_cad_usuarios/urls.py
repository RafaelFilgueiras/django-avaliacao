from django.urls import path
from app_cad_usuarios import views

urlpatterns = [
    path('', views.home, name='home'),
    path('usuarios/', views.usuarios, name='listagem_usuarios'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Rota para o dashboard
    path('empresas/criar/', views.criar_empresa, name='criar_empresa'),
    path('empresas/', views.listar_empresas, name='listagem_empresas'),
    path('empresas/<int:empresa_id>/projeto/criar/', views.criar_projeto, name='criar_projeto'),
    path('empresas/<int:empresa_id>/excluir/', views.excluir_empresa, name='excluir_empresa'),
    path('projeto/<int:projeto_id>/excluir/', views.excluir_projeto, name='excluir_projeto'),  # Rota para excluir projeto
    path('projeto/<int:projeto_id>/', views.ver_projeto, name='ver_projeto'),  # Rota para ver detalhes do projeto
    path('projeto/<int:projeto_id>/usuario/adicionar/', views.adicionar_usuario_projeto, name='adicionar_usuario_projeto'),
    path('projeto/<int:projeto_id>/usuario/remover/<int:usuario_id>/', views.remover_usuario_projeto, name='remover_usuario_projeto'),
    path('empresa/<int:empresa_id>/usuario/adicionar/', views.adicionar_usuario_empresa, name='adicionar_usuario_empresa'),
    path('empresa/<int:empresa_id>/usuario/remover/<int:usuario_id>/', views.remover_usuario_empresa, name='remover_usuario_empresa'),
]
