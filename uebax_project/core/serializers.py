# Em: core/serializers.py
from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Usuario
        # Os campos são os mesmos
        fields = ['nome_completo', 'cpf', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Validação customizada para checar senhas e força.
        """
        password = data.get('password')
        # Pega o 'password2' e já o remove do 'data'
        password2 = data.pop('password2')

        if password != password2:
            raise serializers.ValidationError("As senhas não coincidem")
        
        try:
            # Valida a senha (força, comprimento, etc.) sem
            # precisar de um objeto de usuário.
            validate_password(password, user=None)
        except serializers.ValidationError as e:
            # O 'list(e.messages)' é ótimo para retornar um JSON de erros
            raise serializers.ValidationError(list(e.messages))
        
        # Retorna 'data' limpo (sem password2)
        return data

    def create(self, validated_data):
        """
        Chama o nosso CustomUserManager.create_user()
        """
        # Como 'validated_data' já está limpo (sem password2),
        # podemos passá-lo diretamente para nosso novo create_user.
        return Usuario.objects.create_user(**validated_data)