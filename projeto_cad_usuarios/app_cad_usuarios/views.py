from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Empresa, Projeto, Usuario, PessoasProjeto, PessoasEmpresa

# View da página inicial
def home(request):
    # Criação automática de usuários na primeira execução
    # if not Usuario.objects.filter(user='user1').exists():
    #     Usuario.objects.create(user='user1', senha='senha_caso1')
    # if not Usuario.objects.filter(user='user2').exists():
    #     Usuario.objects.create(user='user2', senha='senha_caso2')
    # if not Usuario.objects.filter(user='user3').exists():
    #     Usuario.objects.create(user='user3', senha='senha_caso3')
    # if not Usuario.objects.filter(user='user4').exists():
    #     Usuario.objects.create(user='user4', senha='senha_caso4')

    return render(request, 'usuarios/home.html')

# View para cadastrar ou autenticar usuário
def usuarios(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        senha = request.POST.get('senha')

        # Tenta encontrar um usuário existente com as credenciais fornecidas
        usuario = Usuario.objects.filter(user=user, senha=senha).first()

        if usuario:
            # Usuário encontrado, armazena na sessão
            request.session['user'] = usuario.id_usuario
            # Redireciona para o dashboard
            return redirect('dashboard')
        else:
            # Caso não exista, retorna erro ou renderiza a página de cadastro novamente
            return HttpResponse("Usuário ou senha incorretos. Tente novamente.")

    # Renderiza a página inicial de cadastro caso o método não seja POST
    return render(request, 'usuarios/home.html')

# View para mostrar o dashboard do usuário
from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from .models import Empresa, Projeto, Usuario, PessoasProjeto

from django.db.models import Q

def dashboard(request):
    usuario = Usuario.objects.get(id_usuario=request.session['user'])

    # Projetos que o usuário criou
    projetos_criados = Projeto.objects.filter(criador=usuario)

    # Projetos nos quais o usuário foi adicionado como participante
    projetos_participando_ids = PessoasProjeto.objects.filter(usuario=usuario).values_list('projeto', flat=True)
    projetos_participando = Projeto.objects.filter(Q(id__in=projetos_participando_ids) | Q(criador=usuario))

    # Empresas criadas pelo usuário
    minhas_empresas = Empresa.objects.filter(criador=usuario)
    
    # Empresas onde o usuário participa
    empresas_participando = Empresa.objects.filter(Q(criador=usuario) | Q(pessoas_empresas__usuario=usuario)).distinct()

    return render(request, 'usuarios/dashboard.html', {
        'usuario': usuario,
        'minhas_empresas': minhas_empresas,
        'empresas_participando': empresas_participando,
        'projetos_criados': projetos_criados,
        'projetos_participando': projetos_participando,
    })


# View para listar empresas
def listar_empresas(request):
    # Verifica se o usuário está autenticado na sessão
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para visualizar as empresas.")

    # Busca o usuário associado na sessão
    usuario = Usuario.objects.get(id_usuario=request.session['user'])
    
    # Filtra as empresas vinculadas ao usuário autenticado
    empresas = Empresa.objects.filter(criador=usuario)
    
    if not empresas.exists():
        return HttpResponse("Nenhuma empresa associada a este usuário.")
    
    return render(request, 'empresas/listar_empresas.html', {'empresas': empresas})

# View para criar uma nova empresa
def criar_empresa(request):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para criar uma empresa.")

    usuario = Usuario.objects.get(id_usuario=request.session['user'])
    
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome')
        nova_empresa = Empresa(nome=nome_empresa, criador=usuario)
        nova_empresa.save()
        return redirect('dashboard')
    return render(request, 'empresas/criar_empresa.html')

# View para criar um novo projeto
from django.shortcuts import get_object_or_404

def criar_projeto(request, empresa_id):
    usuario = Usuario.objects.get(id_usuario=request.session['user'])
    empresa = get_object_or_404(Empresa, id=empresa_id)

    # Verifique se o usuário é o criador da empresa ou está na lista de membros da empresa
    is_member = empresa.criador == usuario or empresa.pessoas_empresas.filter(usuario=usuario).exists()

    if not is_member:
        return HttpResponse("Você não tem permissão para criar projetos nesta empresa.")

    if request.method == 'POST':
        nome = request.POST['nome']
        descricao = request.POST['descricao']
        Projeto.objects.create(nome=nome, descricao=descricao, empresa=empresa, criador=usuario)
        return redirect('dashboard')

    return render(request, 'projetos/criar_projeto.html', {'empresa': empresa})

# View para excluir empresa (somente criador da empresa pode excluir)
def excluir_empresa(request, empresa_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para excluir uma empresa.")

    empresa = Empresa.objects.get(id=empresa_id)
    
    # Verifica se o usuário autenticado é o criador da empresa
    if request.session['user'] == empresa.criador.id_usuario:
        empresa.delete()
        return redirect('dashboard')
    
    return HttpResponse("Apenas o criador da empresa pode excluí-la.")

def excluir_projeto(request, projeto_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para excluir um projeto.")

    projeto = Projeto.objects.get(id=projeto_id)
    
    # Verifica se o usuário autenticado é o criador do projeto
    if request.session['user'] == projeto.criador.id_usuario:
        projeto.delete()
        return redirect('dashboard')
    
    return HttpResponse("Apenas o criador do projeto pode excluí-lo.")

def ver_projeto(request, projeto_id):
    # Verifica se o usuário está autenticado
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para ver o projeto.")

    # Busca o projeto pelo ID
    projeto = Projeto.objects.get(id=projeto_id)

    # Renderiza a página com os detalhes do projeto
    return render(request, 'projetos/ver_projeto.html', {'projeto': projeto})

def adicionar_usuario_projeto(request, projeto_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para adicionar usuários a projetos.")

    projeto = Projeto.objects.get(id=projeto_id)
    empresa = projeto.empresa

    # Apenas o criador do projeto pode adicionar usuários
    if request.session['user'] != projeto.criador.id_usuario:
        return HttpResponse("Apenas o criador do projeto pode adicionar usuários.")

    if request.method == 'POST':
        usuario_nome = request.POST.get('usuario_nome')
        try:
            usuario = Usuario.objects.get(user=usuario_nome)  # Busca pelo nome do usuário
        except Usuario.DoesNotExist:
            return HttpResponse("Usuário não encontrado.")

        # Adiciona usuário ao projeto usando o modelo PessoasProjeto
        PessoasProjeto.objects.create(empresa=empresa, usuario=usuario, projeto=projeto)
        return redirect('dashboard')

    usuarios = Usuario.objects.all()
    return render(request, 'projetos/adicionar_usuario.html', {'projeto': projeto, 'usuarios': usuarios})

def remover_usuario_projeto(request, projeto_id, usuario_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para remover usuários de projetos.")

    projeto = Projeto.objects.get(id=projeto_id)

    # Apenas o criador do projeto pode remover usuários
    if request.session['user'] != projeto.criador.id_usuario:
        return HttpResponse("Apenas o criador do projeto pode remover usuários.")

    usuario = Usuario.objects.get(id_usuario=usuario_id)
    relacao = PessoasProjeto.objects.filter(empresa=projeto.empresa, projeto=projeto, usuario=usuario)

    # Remove o relacionamento se existir
    if relacao.exists():
        relacao.delete()

    return redirect('dashboard')

def adicionar_usuario_empresa(request, empresa_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para adicionar usuários a empresas.")

    empresa = Empresa.objects.get(id=empresa_id)

    # Apenas o criador da empresa pode adicionar usuários
    if request.session['user'] != empresa.criador.id_usuario:
        return HttpResponse("Apenas o criador da empresa pode adicionar usuários.")

    if request.method == 'POST':
        usuario_nome = request.POST.get('usuario_nome')
        try:
            usuario = Usuario.objects.get(user=usuario_nome)
            # Adiciona usuário à empresa usando o modelo PessoasEmpresa
            PessoasEmpresa.objects.create(empresa=empresa, usuario=usuario)
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            return HttpResponse("Usuário não encontrado.")

    usuarios = Usuario.objects.all()
    return render(request, 'empresas/adicionar_usuario.html', {'empresa': empresa, 'usuarios': usuarios})

def remover_usuario_empresa(request, empresa_id, usuario_id):
    if 'user' not in request.session:
        return HttpResponse("Você precisa estar autenticado para remover usuários da empresa.")
    
    empresa = Empresa.objects.get(id=empresa_id)
    
    # Apenas o criador da empresa pode remover usuários
    if request.session['user'] != empresa.criador.id_usuario:
        return HttpResponse("Apenas o criador da empresa pode remover usuários.")
    
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    
    # Remover usuário da empresa
    relacao_empresa = PessoasEmpresa.objects.filter(empresa=empresa, usuario=usuario)
    if relacao_empresa.exists():
        relacao_empresa.delete()
    
    # Remover usuário de todos os projetos da empresa
    relacoes_projetos = PessoasProjeto.objects.filter(empresa=empresa, usuario=usuario)
    if relacoes_projetos.exists():
        relacoes_projetos.delete()
    
    return redirect('dashboard')


