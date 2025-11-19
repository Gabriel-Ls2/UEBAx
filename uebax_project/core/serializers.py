from rest_framework import serializers
from .models import Usuario, ResetPasswordToken, Evento, Alerta
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import log_event

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Usuario
        fields = ['nome_completo', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Validação customizada para checar senhas e força.

        password = data.get('password')
        password2 = data.pop('password2')

        if password != password2:
            raise serializers.ValidationError("As senhas não coincidem")
        
        try:
            validate_password(password, user=None)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return data

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

class PasswordResetRequestSerializer(serializers.Serializer):
    
    # Serializador para a Tela 3 ("Esqueci a Senha").
    # Apenas valida se o email existe.
    
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            Usuario.objects.get(email=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("E-mail Inválido")
        return value

class PasswordResetVerifySerializer(serializers.Serializer):
    
    # Serializador para a "Tela de Verificação de Código" (Tela 4).
    # Valida o email e o token de 6 dígitos.
    
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data):
        email = data.get('email')
        token = data.get('token')

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Token Inválido") 

        try:
            reset_token = ResetPasswordToken.objects.get(usuario=usuario, token=token)
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Token Inválido")

        if reset_token.is_expired():
            raise serializers.ValidationError("Token Expirado")
        
        data['usuario'] = usuario
        return data

class PasswordResetConfirmSerializer(serializers.Serializer):
    
    # Serializador para a "Tela de Nova Senha" (Tela 5).
    # Recebe email, token, e a nova senha.
    
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True, 
        min_length=8
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True
    )

    def validate(self, data):
        # Validação das Senhas 
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "As senhas não coincidem"})

        # Valida a força da senha
        try:
            validate_password(password, user=None)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # Re-validação do Token 
        try:
            usuario = Usuario.objects.get(email=data.get('email'))
            reset_token = ResetPasswordToken.objects.get(
                usuario=usuario, 
                token=data.get('token')
            )
        except (Usuario.DoesNotExist, ResetPasswordToken.DoesNotExist):
            raise serializers.ValidationError({"token": "Token Inválido"})

        if reset_token.is_expired():
            raise serializers.ValidationError({"token": "Token Expirado"})
        
        # Anexa o usuário e o token aos dados validados
        data['usuario'] = usuario
        data['reset_token'] = reset_token
        return data

    def save(self):
       
        # Salva a nova senha do usuário e deleta o token.
        
        usuario = self.validated_data['usuario']
        reset_token = self.validated_data['reset_token']
        password = self.validated_data['password']

        usuario.set_password(password)
        usuario.save()

        reset_token.delete()

class LogoutSerializer(serializers.Serializer):
    
    # Serializador para o endpoint de Logout (Sair).
    # Recebe o refresh token para colocá-lo na blacklist.
    
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token inválido ou expirado')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
   
    # Serializer de Login (Versão E-mail).
    # Usa o padrão do Django (email/senha) e registra os eventos.
    
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except Exception as e:
            email_tentado = attrs.get('email')
            if email_tentado:
                try:
                    usuario = Usuario.objects.get(email=email_tentado)
                    log_event(
                        usuario=usuario,
                        tipo_evento=Evento.TipoEvento.FALHA_LOGIN,
                        descricao="Tentativa de login com senha incorreta."
                    )
                except Usuario.DoesNotExist:
                    pass
            raise e
        log_event(
            usuario=self.user,
            tipo_evento=Evento.TipoEvento.LOGIN
        )
        
        return data
    
class AlertaSerializer(serializers.ModelSerializer):
    
    # Serializador para a "Tabela de Alertas".
    
    usuario_email = serializers.ReadOnlyField(source='usuario.email')
    
    data = serializers.DateTimeField(source='timestamp', format='%d/%m/%Y')
    horario = serializers.DateTimeField(source='timestamp', format='%H:%M')
    descricao = serializers.CharField(source='get_tipo_alerta_display')

    class Meta:
        model = Alerta
        fields = ['descricao', 'usuario_email', 'data', 'horario']


class EventoSerializer(serializers.ModelSerializer):
    
    # Serializador para a "Tabela de Eventos".
    
    usuario_email = serializers.ReadOnlyField(source='usuario.email')
    
    evento_desc = serializers.CharField(source='get_tipo_evento_display')
    horario = serializers.DateTimeField(source='timestamp', format='%H:%M')

    class Meta:
        model = Evento
        fields = ['usuario_email', 'evento_desc', 'horario']