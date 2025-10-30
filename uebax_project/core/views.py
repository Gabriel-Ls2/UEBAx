from django.shortcuts import render
# Em: core/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny # Permite acesso a qualquer um (para cadastro)
from .serializers import UserRegistrationSerializer
from .models import Usuario

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