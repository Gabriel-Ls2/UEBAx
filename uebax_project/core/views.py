from django.shortcuts import render
# Em: core/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer, PasswordResetRequestSerializer
from .models import Usuario, ResetPasswordToken
from django.core.mail import send_mail
from django.conf import settings

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
    Recebe um e-mail e envia um token de 6 dígitos.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # O 'is_valid' vai rodar o 'validate_email'
        if serializer.is_valid():
            email = serializer.validated_data['email']
            usuario = Usuario.objects.get(email=email)
            
            # Cria ou obtém o token. O modelo cuida da geração dos 6 dígitos.
            # O 'defaults' garante que, se um token antigo existir,
            # ele seja atualizado com um novo código e 'created_at'.
            token, created = ResetPasswordToken.objects.update_or_create(
                usuario=usuario,
                defaults={'usuario': usuario}
            )

            # --- Lógica de Envio de E-mail ---
            subject = 'Seu código de redefinição de senha do UEBAX'
            message = f'Olá, {usuario.nome_completo}!\n\n' \
                      f'Seu token de redefinição de senha é: {token.token}\n\n' \
                      f'Este token expira em 5 minutos.\n' \
                      f'Se você não solicitou isso, ignore este e-mail.'
            
            from_email = settings.DEFAULT_FROM_EMAIL # Ou 'nao-responda@uebax.com'
            recipient_list = [usuario.email]
            
            # Envia o e-mail (que aparecerá no console)
            send_mail(subject, message, from_email, recipient_list)
            # ---------------------------------
            
            return Response(
                {"message": "Token enviado para o seu e-mail com sucesso!"},
                status=status.HTTP_200_OK
            )
        
        # Se não for válido, retorna o erro "E-mail Inválido"
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)