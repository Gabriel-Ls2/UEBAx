from .models import Usuario, Evento, Alerta
from django.utils import timezone

def _analisar_evento(evento: Evento):
    """
    Motor de Regras Interno.
    Esta função é chamada pelo log_event para analisar
    um evento recém-criado e decidir se gera um alerta.
    """
    
    # --- REGRA 1: Acesso fora do horário comercial ---
    # Como você especificou, vamos checar se o login foi feito
    # em um horário "incomum" (ex: antes das 8h ou depois das 18h)
    if evento.tipo_evento == Evento.TipoEvento.LOGIN:
        hora_do_evento = evento.timestamp.hour
        
        # Vamos definir "horário comercial" como 8h às 18h
        if hora_do_evento < 8 or hora_do_evento > 18:
            
            # REGRA VIOLADA! Crie um Alerta.
            Alerta.objects.create(
                usuario=evento.usuario,
                tipo_alerta=Alerta.TipoAlerta.FORA_DO_HORARIO,
                descricao_detalhada=f"Usuário fez login fora do horário comercial (às {hora_do_evento}h)."
            )
    
    # --- REGRA 2: Múltiplas Falhas de Login ---
    # (Exemplo de como você adicionaria sua próxima regra)
    if evento.tipo_evento == Evento.TipoEvento.FALHA_LOGIN:
        # 1. Conte quantas falhas este usuário teve nos últimos 10 minutos
        dez_minutos_atras = timezone.now() - timezone.timedelta(minutes=10)
        falhas_recentes = Evento.objects.filter(
            usuario=evento.usuario,
            tipo_evento=Evento.TipoEvento.FALHA_LOGIN,
            timestamp__gte=dez_minutos_atras
        ).count()
        
        # 2. Defina um limite (ex: 5 falhas)
        if falhas_recentes >= 5:
            # REGRA VIOLADA!
            # (Evita criar 10 alertas, só cria um)
            Alerta.objects.get_or_create(
                usuario=evento.usuario,
                tipo_alerta=Alerta.TipoAlerta.FALHA_LOGIN_MULTIPLA,
                defaults={'descricao_detalhada': f"Detectadas {falhas_recentes} falhas de login em 10 minutos."}
            )

    # --- FUTURAS REGRAS ---
    # if evento.tipo_evento == Evento.TipoEvento.ACESSO_ARQUIVO:
    #    if 'confidencial' in evento.descricao:
    #        Alerta.objects.create(...)
    #


def log_event(usuario: Usuario, tipo_evento: Evento.TipoEvento, descricao: str = None):
    """
    MOTOR DE EVENTOS (UEBAX)
    Esta é a função central para registrar qualquer atividade no sistema.
    """
    
    # 1. Cria o evento no banco de dados
    evento = Evento.objects.create(
        usuario=usuario,
        tipo_evento=tipo_evento,
        descricao=descricao
    )
    
    # 2. Imediatamente, envia o evento para análise do motor de regras
    _analisar_evento(evento)
    
    return evento