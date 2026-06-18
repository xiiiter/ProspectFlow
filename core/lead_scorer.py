"""
Pontuação e análise de leads para prospecção.
"""
from core.enricher import (
    analisar_website,
    analisar_seo,
    buscar_redes_sociais,
    extrair_emails_do_site,
    calcular_score_oportunidade,
)


def analisar_lead_completo(lead: dict, analisar_site: bool = True) -> dict:
    """
    Faz análise completa de um lead e retorna dados enriquecidos.
    """
    site = lead.get('website', '') or lead.get('site', '')
    nome = lead.get('nome', '')
    nicho = lead.get('nicho', '')

    resultado = dict(lead)

    if analisar_site and site:
        resultado['_analise_site'] = analisar_website(site)
        resultado['_seo'] = analisar_seo(site, nome, nicho)
        resultado['_redes'] = buscar_redes_sociais(nome, site)

        if not lead.get('email'):
            emails = extrair_emails_do_site(site)
            if emails:
                resultado['email'] = emails[0]
                resultado['emails_extras'] = emails[1:]

    score_info = calcular_score_oportunidade(resultado)
    resultado['score_oportunidade'] = score_info['score']
    resultado['prioridade_score'] = score_info['prioridade']
    resultado['motivos_score'] = '\n'.join(score_info['motivos'])

    return resultado
