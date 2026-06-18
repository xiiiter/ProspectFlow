"""
Gera emails personalizados com Claude ou template local.
"""
import os
import json
import time
import random
from pathlib import Path

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# Constantes
SEU_NOME  = os.getenv("SEU_NOME",  "Your Name")
SEU_EMAIL = os.getenv("SEU_EMAIL", "you@email.com")
SEU_LINK  = os.getenv("SEU_LINK",  "https://yourportfolio.com")

# Carrega config.json se disponível
_BASE_DIR = Path(__file__).parent.parent
_CONFIG_PATH = _BASE_DIR / "config.json"
_CONFIG: dict = {}
try:
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, encoding="utf-8") as _f:
            _CONFIG = json.load(_f)
except Exception:
    pass

MOEDA_SIMBOLO = "R$" if _CONFIG.get("moeda", "BRL") == "BRL" else "US$"

PRECOS_DEFAULT = {
    # Brasil (BRL)
    "dentista": 2500, "clínica odontológica": 3000, "ortodontista": 2800,
    "fisioterapeuta": 1800, "psicólogo": 2000, "nutricionista": 1800,
    "médico": 3000, "clínica médica": 3000, "dermatologista": 2800,
    "oftalmologista": 2500, "pediatra": 2800, "veterinário": 2200,
    "clínica veterinária": 2500, "pet shop": 1500,
    "barbearia": 1200, "salão de beleza": 1500, "cabeleireiro": 1400,
    "manicure": 900, "spa": 2000, "estética": 1800,
    "academia": 2000, "crossfit": 2000, "pilates": 1800, "yoga": 1500,
    "restaurante": 1800, "lanchonete": 1200, "pizzaria": 1500,
    "padaria": 1300, "cafeteria": 1200, "hamburgueria": 1300,
    "advogado": 3500, "contador": 2800, "imobiliária": 3000,
    "arquiteto": 3000, "escola": 2500, "cursinho": 2000,
    "construtora": 3000, "eletricista": 1500, "mecânica": 1800,
    # Gringa (USD)
    "dentist": 800, "barbershop": 500, "restaurant": 600,
    "gym": 600, "salon": 500, "vet": 700,
    "law": 1200, "accountant": 800, "photographer": 600,
    "default": 700,
}

PRECOS = {**PRECOS_DEFAULT, **_CONFIG.get("precos", {})}


def obter_preco(nicho: str) -> int:
    """Retorna o preço configurado para o nicho."""
    if nicho in PRECOS:
        return int(PRECOS[nicho])
    nicho_lower = nicho.lower()
    for key, val in PRECOS.items():
        if key in nicho_lower or nicho_lower in key:
            return int(val)
    return int(PRECOS.get("default", 700))


def formatar_preco(valor: int) -> str:
    """Formata preço com símbolo da moeda configurada."""
    if MOEDA_SIMBOLO == "R$":
        return f"R$ {valor:,.0f}".replace(",", ".")
    return f"${valor}"


def gerar_email_com_claude(lead: dict, modo_fallback: bool = False) -> dict:
    """
    Gera subject + body do email via Claude API.
    Se modo_fallback=True ou sem API key, usa template local.
    """
    if modo_fallback or not REQUESTS_OK:
        return gerar_email_template(lead)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return gerar_email_template(lead)

    preco     = obter_preco(lead.get("nicho", "default"))
    preco_fmt = formatar_preco(preco)
    site_tipo = lead.get("site_tipo", "sem_site")
    eh_brasil = MOEDA_SIMBOLO == "R$"
    idioma    = "português brasileiro" if eh_brasil else "English"

    if site_tipo == "sem_site":
        contexto = (
            f"O negócio NÃO tem site, apenas aparece no Google Maps "
            f"com {lead.get('num_reviews', 'algumas')} avaliações."
            if eh_brasil else
            f"The business has NO website. Found on Google Maps with {lead.get('num_reviews', 'some')} reviews."
        )
    elif site_tipo == "apenas_social":
        contexto = (
            f"O negócio usa apenas Instagram/Facebook como presença online, sem site próprio."
            if eh_brasil else
            f"The business only has Facebook/Instagram, no real website."
        )
    else:
        contexto = (
            f"O negócio tem site mas ele está desatualizado ou não é responsivo."
            if eh_brasil else
            f"The business has an outdated or non-mobile-friendly website."
        )

    prompt = f"""Você é um copywriter especialista em cold email para desenvolvedor web freelancer.
Escreva um cold email para o dono de um negócio local oferecendo um site novo.
Escreva em {idioma}.

Informações do negócio:
- Nome: {lead.get('nome', '')}
- Tipo: {lead.get('nicho', '')}
- Cidade: {lead.get('cidade', '')}
- Avaliação: {lead.get('rating', 'N/A')} estrelas ({lead.get('num_reviews', 'várias')} avaliações)
- Situação: {contexto}
- WhatsApp disponível: {'sim' if lead.get('whatsapp') else 'não'}

Remetente: {SEU_NOME} | {SEU_LINK}
Preço: {preco_fmt}
Prazo: 5 dias úteis
Preview expira: 7 dias

Regras:
- Assunto: máx 8 palavras, desperta curiosidade, específico ao negócio
- Corpo: máx 80 palavras, ultra-personalizado, sem enrolação
- Mencione UM ponto de dor específico baseado na situação
- UM CTA claro: ver o demo
- Termina só com o nome do remetente
- Substitua [LINK_DEMO] literalmente (será preenchido depois)
- {'Escreva em português brasileiro natural e direto' if eh_brasil else 'Write in natural English'}

Responda SOMENTE com JSON (sem markdown, sem explicação):
{{"subject": "...", "body": "..."}}"""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )

        if resp.status_code == 401:
            return gerar_email_template(lead)

        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        return {
            "subject": parsed["subject"],
            "body":    parsed["body"],
            "preco":   preco,
            "via":     "claude_api",
        }

    except Exception:
        return gerar_email_template(lead)


def gerar_email_template(lead: dict) -> dict:
    """Template local de fallback (não requer API). Suporta BRL e USD."""
    preco     = obter_preco(lead.get("nicho", "default"))
    preco_fmt = formatar_preco(preco)
    nome      = lead.get("nome", "")
    cidade    = lead.get("cidade", "")
    tipo      = lead.get("site_tipo", "sem_site")
    eh_brasil = MOEDA_SIMBOLO == "R$"
    nicho     = lead.get("nicho", "seu segmento")

    if eh_brasil:
        if tipo == "sem_site":
            subject = f"Criei um site para {nome} — dá uma olhada"
            body = (
                f"Olá,\n\n"
                f"Encontrei {nome} no Google Maps — ótimas avaliações!\n"
                f"Um site profissional ajudaria mais pessoas em {cidade} a encontrar vocês.\n\n"
                f"Já criei um conceito para vocês: [LINK_DEMO]\n\n"
                f"Responsivo, com seus serviços + localização + botão de contato. "
                f"Pronto em 5 dias úteis por {preco_fmt}. Preview disponível por 7 dias.\n\n"
                f"{SEU_NOME}"
            )
        elif tipo == "apenas_social":
            subject = f"Seu Instagram está custando clientes para {nome}"
            body = (
                f"Olá,\n\n"
                f"Vi {nome} no Google Maps e percebi que vocês dependem só do Instagram.\n"
                f"Clientes pesquisando {nicho} em {cidade} não conseguem te encontrar no Google.\n\n"
                f"Criei um site completo para vocês: [LINK_DEMO]\n\n"
                f"Rápido, mobile-first, pronto em 5 dias por {preco_fmt}.\n\n"
                f"{SEU_NOME}"
            )
        else:
            subject = f"Conceito de site moderno para {nome}"
            body = (
                f"Olá,\n\n"
                f"Encontrei {nome} ao pesquisar {nicho} em {cidade} "
                f"e vi que o site poderia ter uma atualização.\n\n"
                f"Criei um conceito moderno para vocês: [LINK_DEMO]\n\n"
                f"Responsivo, rápido e otimizado para converter visitantes em clientes. "
                f"Versão final em 5 dias por {preco_fmt}.\n\n"
                f"{SEU_NOME}"
            )
    else:
        if tipo == "sem_site":
            subject = f"I built a website for {nome} — take a look"
            body = (
                f"Hi,\n\nFound {nome} on Google Maps — great reviews! "
                f"A professional website would help more people in {cidade} find you.\n\n"
                f"I already built a concept: [LINK_DEMO]\n\n"
                f"Mobile-friendly, your services + location + booking. "
                f"Ready in 5 days for {preco_fmt}. Preview up for 7 days.\n\n{SEU_NOME}"
            )
        elif tipo == "apenas_social":
            subject = f"Your Facebook page is costing {nome} customers"
            body = (
                f"Hi,\nFound {nome} on Google Maps — running on Facebook only. "
                f"Customers searching for {nicho} in {cidade} can't find you properly.\n\n"
                f"Built a real site concept: [LINK_DEMO]\n\nFast, mobile-first — "
                f"ready in 5 days for {preco_fmt}.\n\n{SEU_NOME}"
            )
        else:
            subject = f"Modern website concept for {nome}"
            body = (
                f"Hi,\nSaw {nome} while looking for {nicho} in {cidade} "
                f"— noticed the site could use a refresh.\n\n"
                f"Created a concept: [LINK_DEMO]\n\nResponsive, fast, converts visitors. "
                f"Final version in 5 days for {preco_fmt}.\n\n{SEU_NOME}"
            )

    return {"subject": subject, "body": body, "preco": preco, "via": "template"}
