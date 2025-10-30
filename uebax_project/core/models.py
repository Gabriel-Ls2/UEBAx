import random
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

# --- Modelos de Autenticação e Usuário ---
class CustomUserManager(BaseUserManager):
    """
    Gerenciador de usuário customizado onde o email é o identificador único
    em vez do username.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Cria e salva um Usuário com o email e senha fornecidos.
        """
        if not email:
            raise ValueError('O Email é obrigatório')
        
        email = self.normalize_email(email)
        
        # Pega os campos do seu modelo (nome_completo, cpf)
        # dos extra_fields para criar o usuário
        usuario = self.model(email=email, **extra_fields)
        
        usuario.set_password(password) # Criptografa a senha
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e salva um Superusuário com o email e senha fornecidos.
        """
        # Define os padrões para um superusuário
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')
        
        # Chama o create_user normal
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado usando AbstractBaseUser.
    """
    # Campos da sua especificação
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True, blank=False)

    # Campos que o AbstractUser fornecia e que agora precisamos
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # --- Configuração Principal ---
    
    # Diz ao Django que o campo 'email' será usado para login
    USERNAME_FIELD = 'email'
    
    # Campos obrigatórios ao criar um superusuário (além de email e senha)
    REQUIRED_FIELDS = ['nome_completo', 'cpf']

    # Diz ao Django para usar nosso gerenciador customizado
    objects = CustomUserManager() 

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
