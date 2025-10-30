from django.shortcuts import render
# Em: core/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, PasswordResetRequestSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer, LogoutSerializer, CustomTokenObtainPairSerializer
from .models import Usuario, ResetPasswordToken
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView

class UserRegistrationView(generics.CreateAPIView):
    """
    View para a "Tela de Cadastro".
    Aceita requisições POST para criar um novo usuário.
    """
    queryset = Usuario.objects.all()
    serializer_class = UserRegistrationSerializer
    
    # Define que qualquer pessoa (mesmo não logada) pode acessar este endpoint.
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método 'create' para retornar a sua 
        mensagem de sucesso customizada.
        """
        serializer = self.get_serializer(data=request.data)
        
        # O 'is_valid' vai rodar o nosso 'validate()' do serializador
        if serializer.is_valid():
            self.perform_create(serializer)
            
            # Sua mensagem de sucesso!
            return Response(
                {"message": "Cadastro realizado com sucesso!"}, 
                status=status.HTTP_201_CREATED
            )
        
        # Se não for válido, o DRF automaticamente retorna os erros
        # (Ex: "As senhas não coincidem", "Este e-mail já existe", etc.)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    """
    View para a "Tela de Redefinição de Senha" (Tela 3).
    (VERSÃO CORRIGIDA)
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            usuario = Usuario.objects.get(email=email)
            
            # --- LÓGICA CORRIGIDA AQUI ---
            
            # 1. Usamos get_or_create. Ele retorna o token (antigo)
            #    ou cria um novo (com um token inicial).
            token, created = ResetPasswordToken.objects.get_or_create(usuario=usuario)
            
            # 2. AGORA, nós manualmente chamamos .save().
            #    Isso vai FORÇAR a execução do nosso método save() no models.py.
            #    O método vai gerar um NOVO token e reiniciar o timer.
            token.save()
            
            # 3. Agora, a variável 'token' na nossa mão (em 'token.token')
            #    tem o MESMO valor que foi salvo no banco, pois o
            #    .save() atualizou o objeto 'self.token'.
            
            # --- Fim da Lógica Corrigida ---

            # Lógica de Envio de E-mail (agora com o token correto)
            subject = 'Seu código de redefinição de senha do UEBAX'
            message = f'Olá, {usuario.nome_completo}!\n\n' \
                      f'Seu token de redefinição de senha é: {token.token}\n\n' \
                      f'Este token expira em 5 minutos.\n' \
                      f'Se você não solicitou isso, ignore este e-mail.'
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [usuario.email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            return Response(
                {"message": "Token enviado para o seu e-mail com sucesso!"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyView(generics.GenericAPIView):
    """
    View para a "Tela de Verificação de Código" (Tela 4).
    Verifica se o token é válido e não expirou.
    """
    serializer_class = PasswordResetVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # 'is_valid' vai rodar toda a lógica do 'validate'
        if serializer.is_valid():
            # Sua mensagem de sucesso da especificação
            return Response(
                {"message": "Token Confirmado"},
                status=status.HTTP_200_OK
            )
        
        # Se não for válido, retorna o erro (Ex: "Token Inválido", "Token Expirado")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    View para a "Tela de Nova Senha" (Tela 5).
    Finalmente, atualiza a senha do usuário.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Chama o nosso método .save() customizado no serializer
            serializer.save() 
            
            # Sua mensagem de sucesso da especificação
            return Response(
                {"message": "Sua senha foi redefinida com sucesso!"},
                status=status.HTTP_200_OK
            )
        
        # Retorna erros (Ex: "Token Inválido", "As senhas não coincidem", etc.)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(generics.GenericAPIView):
    """
    View para a "Tela de Sair" (Botão Sair).
    Exige que o usuário esteja autenticado.
    """
    serializer_class = LogoutSerializer

    # Pela primeira vez, definimos que esta view SÓ
    # pode ser acessada por usuários logados (autenticados).
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Valida os dados (basicamente, checa se 'refresh' foi enviado)
        serializer.is_valid(raise_exception=True)

        # Chama o método .save() do nosso serializer (que faz o blacklist)
        serializer.save()

        # Sua mensagem de sucesso da especificação!
        return Response(
            {"message": "Logout com Sucesso!"}, 
            status=status.HTTP_200_OK
        )
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View de Login customizada.
    A única mudança é dizer ao simple-jwt para usar nosso
    serializer customizado (que registra o log).
    """
    serializer_class = CustomTokenObtainPairSerializer