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

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializador para a Tela 3 ("Esqueci a Senha").
    Apenas valida se o email existe.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        # Verifica se existe um usuário com este e-mail
        try:
            Usuario.objects.get(email=value)
        except Usuario.DoesNotExist:
            # Exatamente a mensagem de erro que você especificou
            raise serializers.ValidationError("E-mail Inválido")
        return value

class PasswordResetVerifySerializer(serializers.Serializer):
    """
    Serializador para a "Tela de Verificação de Código" (Tela 4).
    Valida o email e o token de 6 dígitos.
    """
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data):
        email = data.get('email')
        token = data.get('token')

        try:
            # 1. Tenta encontrar o usuário pelo e-mail
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Token Inválido") # Ou "Usuário não encontrado"

        try:
            # 2. Tenta encontrar o token associado a esse usuário
            reset_token = ResetPasswordToken.objects.get(usuario=usuario, token=token)
        except ResetPasswordToken.DoesNotExist:
            # Sua mensagem de erro da especificação
            raise serializers.ValidationError("Token Inválido")

        # 3. Verifica se o token expirou (usando o método do models.py)
        if reset_token.is_expired():
            # Sua mensagem de erro da especificação
            raise serializers.ValidationError("Token Expirado")
        
        # Se passou por tudo, anexa o usuário aos dados validados
        # Isso será útil no próximo passo (Tela 5)
        data['usuario'] = usuario
        return data

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializador para a "Tela de Nova Senha" (Tela 5).
    Recebe email, token, e a nova senha.
    """
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
        # --- 1. Validação das Senhas ---
        # (Lógica da sua especificação e do serializer de registro)
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "As senhas não coincidem"})

        # Valida a força da senha
        try:
            validate_password(password, user=None)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # --- 2. Re-validação do Token ---
        # (Lógica do serializer anterior)
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
        """
        Salva a nova senha do usuário e deleta o token.
        """
        usuario = self.validated_data['usuario']
        reset_token = self.validated_data['reset_token']
        password = self.validated_data['password']

        # 1. Define a nova senha (o 'set_password' cuida da criptografia)
        usuario.set_password(password)
        usuario.save()

        # 2. Deleta o token para que não possa ser reutilizado
        reset_token.delete()

class LogoutSerializer(serializers.Serializer):
    """
    Serializador para o endpoint de Logout (Sair).
    Recebe o refresh token para colocá-lo na blacklist.
    """
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token inválido ou expirado')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        # O 'save' aqui é onde a mágica acontece.
        # Nós pegamos o token e o adicionamos à blacklist.
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            # Se o token já for inválido, expirado ou adulterado,
            # o .blacklist() dará um erro. Nós o "ignoramos",
            # pois o usuário já está efetivamente deslogado.
            self.fail('bad_token')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer de Login (Versão E-mail).
    Usa o padrão do Django (email/senha) e registra os eventos.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        # Tenta autenticar usando o padrão (Email e Senha)
        try:
            data = super().validate(attrs)
        except Exception as e:
            # --- LOG DE FALHA ---
            # Se o login falhar, tentamos achar o usuário pelo email para registrar a falha
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
                    # Se o e-mail nem existe, não logamos evento de usuário
                    pass
            # Re-lançamos o erro para o frontend receber o "Não autorizado"
            raise e

        # --- LOG DE SUCESSO ---
        # Se chegou aqui, a senha está correta e self.user está preenchido
        log_event(
            usuario=self.user,
            tipo_evento=Evento.TipoEvento.LOGIN
        )
        
        return data
    
class AlertaSerializer(serializers.ModelSerializer):
    """
    Serializador para a "Tabela de Alertas".
    """
    # Em vez de mostrar o ID do usuário, vamos mostrar seu email
    usuario_email = serializers.ReadOnlyField(source='usuario.email')
    
    # Formata o timestamp para ficar mais legível (Data e Hora)
    data = serializers.DateTimeField(source='timestamp', format='%d/%m/%Y')
    horario = serializers.DateTimeField(source='timestamp', format='%H:%M')
    # Pega o nome "legível" do tipo de alerta (ex: "Acesso fora do horário")
    descricao = serializers.CharField(source='get_tipo_alerta_display')

    class Meta:
        model = Alerta
        # Campos exatos que você especificou na "Tela de Alertas"
        fields = ['descricao', 'usuario_email', 'data', 'horario']


class EventoSerializer(serializers.ModelSerializer):
    """
    Serializador para a "Tabela de Eventos".
    """
    # Em vez de mostrar o ID do usuário, vamos mostrar seu email
    usuario_email = serializers.ReadOnlyField(source='usuario.email')
    
    # Pega o nome "legível" do tipo de evento (ex: "Login")
    evento_desc = serializers.CharField(source='get_tipo_evento_display')
    horario = serializers.DateTimeField(source='timestamp', format='%H:%M')

    class Meta:
        model = Evento
        # Campos exatos da sua "Tela de Eventos"
        fields = ['usuario_email', 'evento_desc', 'horario']