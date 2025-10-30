# Em: core/serializers.py
from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializador para o registro de novos usuários.
    """
    
    # Adicionamos um campo 'password2' que não existe no modelo,
    # ele servirá apenas para a validação da "Confirmação de Senha".
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Usuario
        # Campos que esperamos receber do frontend
        fields = ['nome_completo', 'cpf', 'email', 'password', 'password2']
        extra_kwargs = {
            # 'password' será apenas para escrita (não será retornado na resposta)
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Validação customizada para checar se as senhas coincidem.
        """
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            # Exatamente a mensagem de erro que você especificou!
            raise serializers.ValidationError("As senhas não coincidem")

        # Valida a força da senha (mínimo 8 dígitos, etc.)
        # Você pode configurar as regras no settings.py do Django
        try:
            validate_password(password, user=Usuario(**data))
        except serializers.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Remove o campo 'password2' pois ele não faz parte do modelo Usuario
        data.pop('password2')
        return data

    def create(self, validated_data):
        """
        Cria e retorna um novo usuário com uma senha HASHED (criptografada).
        """
        # Usamos create_user() em vez de create() para garantir
        # que a senha seja salva corretamente (com hash).
        usuario = Usuario.objects.create_user(
            email=validated_data['email'],
            nome_completo=validated_data['nome_completo'],
            cpf=validated_data['cpf'],
            password=validated_data['password']
            # Note que 'username' não é necessário se você configurou
            # USERNAME_FIELD = 'email' no seu models.py
        )
        return usuario