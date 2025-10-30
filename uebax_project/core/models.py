import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# --- Modelos de Autenticação e Usuário ---

class Usuario(AbstractUser):
    """
    Modelo de usuário customizado.
    Estendemos o AbstractUser do Django para já ter senha, email, etc.
    Trocamos o login de 'username' para 'email'.
    """
    # Removemos o username, já que usaremos o email
    username = None 
    
    # Campos da sua especificação
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True) # Idealmente, adicione um validador para CPF
    email = models.EmailField(unique=True, blank=False)

    # Dizemos ao Django que o campo 'email' será usado para login
    USERNAME_FIELD = 'email'
    
    # Campos obrigatórios ao criar um superusuário
    REQUIRED_FIELDS = ['nome_completo', 'cpf']

    def __str__(self):
        return self.email

class ResetPasswordToken(models.Model):
    """
    Modelo para guardar o token de 6 dígitos da redefinição de senha.
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Gera um token de 6 dígitos antes de salvar
        if not self.token:
            self.token = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def is_expired(self):
        # Verifica se o token tem mais de 5 minutos
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"Token para {self.usuario.email}"

# --- Modelos do Sistema UEBAX ---

class Evento(models.Model):
    """
    Registra cada atividade ("Evento") que o usuário realiza.
    """
    # Define "tipos" de eventos para padronizar
    class TipoEvento(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        ACESSO_ARQUIVO = 'ACESSO_ARQUIVO', 'Acesso a Arquivo'
        FALHA_LOGIN = 'FALHA_LOGIN', 'Falha de Login'
        # Adicione outros tipos conforme necessário

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos')
    tipo_evento = models.CharField(max_length=20, choices=TipoEvento.choices)
    timestamp = models.DateTimeField(auto_now_add=True) # "Data" e "Horário" juntos
    descricao = models.TextField(blank=True, null=True) # Detalhes extras, se houver

    class Meta:
        ordering = ['-timestamp'] # Sempre mostra os mais recentes primeiro

    def __str__(self):
        return f"[{self.timestamp}] {self.usuario.email} - {self.tipo_evento}"

class Alerta(models.Model):
    """
    Registra um "Alerta" quando um Evento viola uma regra.
    """
    class TipoAlerta(models.TextChoices):
        ACESSO_NEGADO = 'ACESSO_NEGADO', 'Acesso Negado'
        FORA_DO_HORARIO = 'FORA_DO_HORARIO', 'Acesso fora do horário'
        FALHA_LOGIN_MULTIPLA = 'FALHA_LOGIN_MULTIPLA', 'Múltiplas falhas de login'
        # Adicione outros tipos conforme necessário

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='alertas')
    tipo_alerta = models.CharField(max_length=50, choices=TipoAlerta.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    descricao_detalhada = models.TextField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"ALERTA: {self.usuario.email} - {self.tipo_alerta}"
