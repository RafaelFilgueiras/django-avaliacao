from django.db import models

# Modelo de Usuário
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255, unique=True)
    senha = models.CharField(max_length=255)

    def __str__(self):
        return self.user

# Modelo de Empresa
class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='empresas')

    def __str__(self):
        return self.nome

# Modelo de Projeto
class Projeto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='projetos')
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='projetos')

    def __str__(self):
        return self.nome
    
# Modelo para associar pessoas a projetos
class PessoasProjeto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pessoas_projetos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pessoas_projetos')
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='pessoas_projetos')

    def __str__(self):
        return f"{self.usuario.user} em {self.projeto.nome} da {self.empresa.nome}"

class PessoasEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pessoas_empresas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='empresas_participadas')

    def __str__(self):
        return f"{self.usuario.user} na empresa {self.empresa.nome}"