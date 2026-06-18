"""
Gerador de proposta comercial em HTML.
"""
import os
from datetime import datetime

PRECOS_PADRAO = {
    'site_institucional': {'de': 2500, 'por': 1800, 'descricao': 'Site institucional profissional com até 5 páginas'},
    'landing_page': {'de': 1500, 'por': 997, 'descricao': 'Landing page de alta conversão'},
    'loja_virtual': {'de': 5000, 'por': 3500, 'descricao': 'Loja virtual completa com carrinho e pagamento'},
    'redesign': {'de': 2000, 'por': 1400, 'descricao': 'Redesign completo do site atual'},
    'manutencao': {'de': 400, 'por': 290, 'descricao': 'Manutenção mensal (suporte + atualizações)'},
    'seo': {'de': 1200, 'por': 890, 'descricao': 'Pacote SEO mensal (3 meses mínimo)'},
    'google_ads': {'de': 800, 'por': 600, 'descricao': 'Gestão Google Ads mensal'},
}


def gerar_proposta_html(lead: dict, autor: dict, servicos_selecionados: list = None) -> str:
    """
    Gera proposta comercial em HTML pronto para enviar/imprimir.
    """
    nome_empresa = lead.get('nome', 'Empresa')
    nicho = lead.get('nicho', '')
    cidade = lead.get('cidade', '')

    if not servicos_selecionados:
        # Auto-seleciona baseado no score
        site = lead.get('website', '')
        if not site:
            servicos_selecionados = ['site_institucional', 'seo']
        else:
            servicos_selecionados = ['redesign', 'seo']

    servicos_html = ''
    total_de = 0
    total_por = 0
    for key in servicos_selecionados:
        if key in PRECOS_PADRAO:
            s = PRECOS_PADRAO[key]
            total_de += s['de']
            total_por += s['por']
            servicos_html += f"""
            <tr>
                <td style="padding:12px;border-bottom:1px solid #eee">{s['descricao']}</td>
                <td style="padding:12px;border-bottom:1px solid #eee;text-align:right;color:#999;text-decoration:line-through">R$ {s['de']:,.0f}</td>
                <td style="padding:12px;border-bottom:1px solid #eee;text-align:right;font-weight:bold;color:#2d6a4f">R$ {s['por']:,.0f}</td>
            </tr>"""

    data_hoje = datetime.now().strftime('%d/%m/%Y')

    problemas = lead.get('_analise_site', {}).get('problemas', []) or ['Presença digital fraca ou inexistente']
    oportunidades = lead.get('_analise_site', {}).get('oportunidades', []) or [
        'Criar presença digital profissional',
        'Atrair mais clientes pelo Google',
    ]

    problemas_html = ''.join(f'<li>{p}</li>' for p in problemas)
    opps_html = ''.join(f'<li>{o}</li>' for o in oportunidades)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proposta Comercial — {nome_empresa}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #f9f9f9; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; padding: 40px; border-radius: 16px; margin-bottom: 30px; }}
  .header h1 {{ margin: 0 0 8px; font-size: 28px; }}
  .header p {{ margin: 0; opacity: 0.8; }}
  .card {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .price-box {{ background: linear-gradient(135deg, #2d6a4f, #40916c); color: white; border-radius: 12px; padding: 24px; text-align: center; }}
  .price-box .de {{ font-size: 18px; opacity: 0.7; text-decoration: line-through; }}
  .price-box .por {{ font-size: 42px; font-weight: bold; }}
  .footer {{ text-align: center; color: #999; font-size: 13px; margin-top: 30px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  .problem-list li {{ margin-bottom: 8px; color: #c0392b; }}
  .opp-list li {{ margin-bottom: 8px; color: #27ae60; }}
  .cta {{ background: #1a1a2e; color: white; padding: 20px 30px; border-radius: 12px; text-align: center; }}
  .cta a {{ color: #4fc3f7; text-decoration: none; font-weight: bold; font-size: 18px; }}
</style>
</head>
<body>

<div class="header">
  <div style="font-size:13px;opacity:0.6;margin-bottom:8px">PROPOSTA COMERCIAL EXCLUSIVA</div>
  <h1>Transformação Digital para<br><span style="color:#4fc3f7">{nome_empresa}</span></h1>
  <p>{nicho.title()} · {cidade} · Emitida em {data_hoje}</p>
</div>

<div class="card">
  <h2 style="margin-top:0">Diagnóstico Digital</h2>
  <p>Após analisar a presença digital de <strong>{nome_empresa}</strong>, identificamos as seguintes oportunidades:</p>

  <h3 style="color:#c0392b">Problemas encontrados:</h3>
  <ul class="problem-list">
    {problemas_html}
  </ul>

  <h3 style="color:#27ae60">O que podemos melhorar:</h3>
  <ul class="opp-list">
    {opps_html}
  </ul>
</div>

<div class="card">
  <h2 style="margin-top:0">Serviços Propostos</h2>
  <table>
    <thead>
      <tr style="background:#f5f5f5">
        <th style="padding:12px;text-align:left">Serviço</th>
        <th style="padding:12px;text-align:right">De</th>
        <th style="padding:12px;text-align:right">Por</th>
      </tr>
    </thead>
    <tbody>
      {servicos_html}
    </tbody>
  </table>
</div>

<div class="price-box">
  <div class="de">De R$ {total_de:,.0f}</div>
  <div class="por">R$ {total_por:,.0f}</div>
  <div style="margin-top:8px;opacity:0.9">Investimento total (oferta especial)</div>
  <div style="margin-top:16px;font-size:13px;opacity:0.7">Proposta válida por 7 dias · Parcelamento disponível</div>
</div>

<div class="card" style="margin-top:20px">
  <h2 style="margin-top:0">O que está incluído</h2>
  <ul>
    <li>Design profissional e moderno</li>
    <li>Totalmente responsivo (celular, tablet, desktop)</li>
    <li>Integração com WhatsApp e Google Maps</li>
    <li>Domínio e hospedagem no 1º ano</li>
    <li>30 dias de suporte pós-entrega</li>
    <li>Treinamento para editar conteúdo</li>
  </ul>
</div>

<div class="cta">
  <p style="margin:0 0 8px;font-size:15px">Pronto para transformar a presença digital de {nome_empresa}?</p>
  <a href="https://wa.me/{autor.get('whatsapp', '')}">{autor.get('nome', 'Desenvolvedor Web')} — Fale comigo no WhatsApp</a>
  <p style="margin:8px 0 0;font-size:13px;opacity:0.6">{autor.get('email', '')} · {autor.get('site', '')}</p>
</div>

<div class="footer">
  <p>Proposta elaborada exclusivamente para {nome_empresa} · {data_hoje}</p>
</div>

</body>
</html>"""

    return html
