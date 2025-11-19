from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, PasswordResetRequestSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer, LogoutSerializer, CustomTokenObtainPairSerializer, AlertaSerializer, EventoSerializer
from .models import Usuario, ResetPasswordToken, Evento, Alerta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import ExtractHour
from .utils import log_event

class UserRegistrationView(generics.CreateAPIView):
    
    # View para a "Tela de Cadastro".
    # Aceita requisições POST para criar um novo usuário.
    
    queryset = Usuario.objects.all()
    serializer_class = UserRegistrationSerializer

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)

            return Response(
                {"message": "Cadastro realizado com sucesso!"}, 
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    
    # View para a "Tela de Redefinição de Senha" (Tela 3).
    # (VERSÃO CORRIGIDA)
    
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            usuario = Usuario.objects.get(email=email)
            
            token, created = ResetPasswordToken.objects.get_or_create(usuario=usuario)
            
            token.save()

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
    
    # View para a "Tela de Verificação de Código" (Tela 4).
    # Verifica se o token é válido e não expirou.
    
    serializer_class = PasswordResetVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            return Response(
                {"message": "Token Confirmado"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    
    # View para a "Tela de Nova Senha" (Tela 5).
    # Finalmente, atualiza a senha do usuário.
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save() 
            
            return Response(
                {"message": "Sua senha foi redefinida com sucesso!"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(generics.GenericAPIView):
    
    # View para a "Tela de Sair" (Botão Sair).
    # Exige que o usuário esteja autenticado.
    
    serializer_class = LogoutSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        log_event(
            usuario=request.user, 
            tipo_evento=Evento.TipoEvento.LOGOUT
        )

        serializer.save()

        return Response(
            {"message": "Logout com Sucesso!"}, 
            status=status.HTTP_200_OK
        )
    
class CustomTokenObtainPairView(TokenObtainPairView):
    
    # View de Login customizada.
    # A única mudança é dizer ao simple-jwt para usar nosso
    # serializer customizado (que registra o log).
    
    serializer_class = CustomTokenObtainPairSerializer

class EventoListView(generics.ListAPIView):
    
    # Endpoint para a "Tabela de Eventos" (Tela 6).
    # Retorna uma lista de todos os eventos.
    
    queryset = Evento.objects.all() 
    serializer_class = EventoSerializer

    permission_classes = [IsAuthenticated]


class AlertaListView(generics.ListAPIView):
    
    # Endpoint para a "Tabela de Alertas" (Tela 6).
    # Retorna uma lista de todos os alertas.
    
    queryset = Alerta.objects.all() 
    serializer_class = AlertaSerializer
    permission_classes = [IsAuthenticated]

class DashboardStatsView(APIView):
    
    # Endpoint mestre para a tela principal do Dashboard.
    # (VERSÃO CORRIGIDA PARA FUSO HORÁRIO)
    
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        agora = timezone.localtime(timezone.now())
        hoje = agora.date()
        
        # Cálculo dos 4 Cards 

        eventos_hoje = Evento.objects.filter(timestamp__date=hoje)
        alertas_hoje = Alerta.objects.filter(timestamp__date=hoje)

        logins_hoje = eventos_hoje.filter(tipo_evento=Evento.TipoEvento.LOGIN).count()
        
        alertas_ativos = alertas_hoje.count()

        dispositivos_hoje = eventos_hoje.filter(
            tipo_evento=Evento.TipoEvento.LOGIN
        ).values('usuario').distinct().count()

        ultimo_evento_obj = eventos_hoje.order_by('-timestamp').first()
        ultimo_evento_str = "Nenhum evento hoje"
        
        if ultimo_evento_obj:
            hora_local = timezone.localtime(ultimo_evento_obj.timestamp)
            ultimo_evento_str = f"{ultimo_evento_obj.get_tipo_evento_display()} às {hora_local.strftime('%H:%M')}"

        # Dados do "Gráfico em Linha" (Logins por Hora) 

        logins_obj = eventos_hoje.filter(tipo_evento=Evento.TipoEvento.LOGIN)
        logins_por_hora_dados = [0] * 24
        
        for evento in logins_obj:
            hora = timezone.localtime(evento.timestamp).hour
            logins_por_hora_dados[hora] += 1

        # Tabela de "Status de Conexão" 
        
        usuarios_ativos_ids = eventos_hoje.filter(
            tipo_evento=Evento.TipoEvento.LOGIN
        ).values_list('usuario__id', flat=True).distinct()
        
        status_conexao = []
        todos_usuarios = Usuario.objects.all()
        
        for usuario in todos_usuarios:
            user_status = "Ativo" if usuario.id in usuarios_ativos_ids else "Inativo"
            status_conexao.append({
                "nome_usuario": usuario.nome_completo,
                "status": user_status
            })

        # Monta a Resposta Final 
        
        data = {
            "cards": {
                "logins_hoje": logins_hoje,
                "alertas_ativos": alertas_ativos,
                "dispositivos_conectados": dispositivos_hoje,
                "ultimo_evento": ultimo_evento_str
            },
            "grafico_logins_por_hora": {
                "labels": list(range(24)),
                "data": logins_por_hora_dados
            },
            "tabela_status_conexao": status_conexao
        }
        
        return Response(data, status=status.HTTP_200_OK)