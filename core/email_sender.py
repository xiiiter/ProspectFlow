"""
Envia emails pela API do Gmail usando OAuth2.
"""
import os
import base64
import time
import random
from pathlib import Path
from email.mime.text import MIMEText

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False

# Caminhos relativos à raiz do projeto
_BASE_DIR = Path(__file__).parent.parent

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

SEU_NOME  = os.getenv("SEU_NOME",  "Your Name")
SEU_EMAIL = os.getenv("SEU_EMAIL", "")

LIMITE_DIARIO_PADRAO = 20

FOLLOWUP_1 = {
    "subject": "Re: Website concept for {nome}",
    "body": (
        "Hi,\n\n"
        "Just following up on my previous email. "
        "The preview I built for {nome} is still active: [DEMO_LINK]\n\n"
        "Would you have 5 minutes to take a look? Happy to answer any questions.\n\n"
        "Best,\n{seu_nome}"
    ),
}

FOLLOWUP_2 = {
    "subject": "Re: Website — last chance to preview",
    "body": (
        "Hi,\n\n"
        "Taking the preview down soon. Here's the link one more time: [DEMO_LINK]\n\n"
        "No pressure — just wanted to make sure you had a chance to see it.\n\n"
        "Best,\n{seu_nome}"
    ),
}


def autenticar_gmail():
    """Autentica via OAuth2 e retorna (serviço Gmail, email_remetente)."""
    if not GOOGLE_OK:
        raise ImportError("Instale: pip install google-auth google-auth-oauthlib google-api-python-client")

    creds = None
    token_path = _BASE_DIR / "token.json"
    creds_path = _BASE_DIR / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError("credentials.json não encontrado")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(str(token_path), "w") as f:
            f.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    email_remetente = profile.get("emailAddress", "")

    return service, email_remetente


def criar_mensagem(para: str, assunto: str, corpo: str, remetente: str) -> dict:
    """Cria mensagem MIME codificada em base64."""
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["to"]      = para
    msg["from"]    = remetente
    msg["subject"] = assunto
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def enviar_email(service, para: str, assunto: str, corpo: str, remetente: str, dry_run: bool = False) -> bool:
    """Envia email via Gmail API."""
    if dry_run:
        return True
    if not GOOGLE_OK:
        return False
    try:
        msg = criar_mensagem(para, assunto, corpo, remetente)
        service.users().messages().send(userId="me", body=msg).execute()
        return True
    except Exception:
        return False
