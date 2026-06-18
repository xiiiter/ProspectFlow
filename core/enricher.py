"""
Enriquece leads com CNPJ, telefone, emails, redes sociais, site e SEO.
"""
import re
import requests
import time
import logging

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

logger = logging.getLogger(__name__)

# CNPJ
def buscar_cnpj_por_nome(nome_empresa: str, cidade: str = "") -> dict:
    """Busca CNPJ pelo nome da empresa usando múltiplas fontes com fallback."""
    # Estratégia 1: Casa dos Dados
    try:
        payload = {
            "query": {"razao_social": nome_empresa},
            "range_query": {},
            "extras": {
                "somente_mei": False,
                "excluir_sem_contato": False,
                "com_email": False,
                "incluir_atividade_secundaria": False,
            },
            "page": 1,
        }
        if cidade:
            mun = re.sub(r"\s+", " ", cidade.split("-")[0].split(",")[0]).strip().upper()
            payload["query"]["municipio"] = [mun]
        r = requests.post(
            "https://api.casadosdados.com.br/v2/public/cnpj/pesquisa",
            json=payload, timeout=10,
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
        )
        if r.status_code == 200:
            items = r.json().get("data", {}).get("cnpj", [])
            if items:
                cnpj_num = re.sub(r"\D", "", items[0].get("cnpj", "") or "")
                if len(cnpj_num) == 14:
                    dados = enriquecer_cnpj(cnpj_num)
                    if dados.get("razao_social"):
                        return dados
    except Exception as e:
        logger.debug(f"Casa dos Dados erro: {e}")

    # Estratégia 2: cnpj.biz scraping
    try:
        nome_clean = re.sub(r"[^\w\s]", " ", nome_empresa).strip()
        q = requests.utils.quote(nome_clean)
        r = requests.get(
            f"https://www.cnpj.biz/pesquisa/{q}",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR,pt;q=0.9"},
        )
        if r.status_code == 200:
            cnpjs = re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", r.text)
            if cnpjs:
                cnpj_num = re.sub(r"\D", "", cnpjs[0])
                dados = enriquecer_cnpj(cnpj_num)
                if dados.get("razao_social"):
                    return dados
    except Exception as e:
        logger.debug(f"cnpj.biz erro: {e}")

    return {}


def buscar_dados_cnpj(cnpj: str) -> dict:
    """Busca dados completos de um CNPJ numérico."""
    return enriquecer_cnpj(cnpj)


def _fmt_cnpj(n: str) -> str:
    n = re.sub(r"\D", "", n)
    return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}" if len(n) == 14 else n


def _brasilapi(cnpj: str) -> dict:
    """Consulta BrasilAPI."""
    cnpj_num = re.sub(r'\D', '', cnpj)
    try:
        r = requests.get(
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_num}",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if r.status_code == 200:
            d = r.json()
            qsa = d.get('qsa', []) or []
            socios = [s.get('nome_socio', '') or s.get('nome', '') for s in qsa]
            socios = [s for s in socios if s]
            cap = d.get('capital_social', 0) or 0
            return {
                'cnpj': _fmt_cnpj(cnpj_num),
                'razao_social': d.get('razao_social', ''),
                'situacao': d.get('descricao_situacao_cadastral', ''),
                'situacao_cnpj': d.get('descricao_situacao_cadastral', ''),
                'atividade': d.get('cnae_fiscal_descricao', ''),
                'atividade_principal': d.get('cnae_fiscal_descricao', ''),
                'data_abertura': d.get('data_inicio_atividade', ''),
                'capital': f"R$ {cap:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'capital_social': f"R$ {cap:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'natureza': d.get('descricao_natureza_juridica', ''),
                'natureza_juridica': d.get('descricao_natureza_juridica', ''),
                'telefone': d.get('ddd_telefone_1', ''),
                'telefone_cnpj': d.get('ddd_telefone_1', ''),
                'socios': ' | '.join(socios[:5]),
                'nome_dono': socios[0] if socios else '',
            }
    except Exception as e:
        logger.warning(f"BrasilAPI erro: {e}")
    return {}


def _receitaws(cnpj: str) -> dict:
    """Consulta receitaws.com.br."""
    cnpj_num = re.sub(r'\D', '', cnpj)
    try:
        r = requests.get(
            f"https://receitaws.com.br/v1/cnpj/{cnpj_num}",
            timeout=12,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if r.status_code == 200:
            d = r.json()
            if d.get('status') == 'ERROR':
                return {}
            qsa = d.get('qsa', []) or []
            socios = [s.get('nome', '') for s in qsa if s.get('nome')]
            tel = re.sub(r"\D", "", d.get('telefone', '') or '')
            cap_raw = d.get('capital_social', '') or ''
            try:
                cap = float(re.sub(r"[^\d,]", "", cap_raw).replace(",", "."))
                cap_fmt = f"R$ {cap:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                cap_fmt = cap_raw
            return {
                'cnpj': _fmt_cnpj(cnpj_num),
                'razao_social': d.get('nome', ''),
                'situacao': d.get('situacao', ''),
                'situacao_cnpj': d.get('situacao', ''),
                'atividade': (d.get('atividade_principal') or [{}])[0].get('text', '') if d.get('atividade_principal') else '',
                'atividade_principal': (d.get('atividade_principal') or [{}])[0].get('text', '') if d.get('atividade_principal') else '',
                'data_abertura': d.get('abertura', ''),
                'capital': cap_fmt,
                'capital_social': cap_fmt,
                'natureza': d.get('natureza_juridica', ''),
                'natureza_juridica': d.get('natureza_juridica', ''),
                'telefone': tel,
                'telefone_cnpj': tel,
                'socios': ' | '.join(socios[:5]),
                'nome_dono': socios[0] if socios else '',
            }
    except Exception as e:
        logger.warning(f"ReceitaWS erro: {e}")
    return {}


def _cnpjws(cnpj: str) -> dict:
    """Consulta publica.cnpj.ws."""
    cnpj_num = re.sub(r'\D', '', cnpj)
    try:
        r = requests.get(
            f"https://publica.cnpj.ws/cnpj/{cnpj_num}",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if r.status_code == 200:
            d = r.json()
            qsa = d.get('qsa', []) or []
            socios = [
                s.get('nome_socio', '') or s.get('nome_responsavel', '')
                for s in qsa
            ]
            socios = [s for s in socios if s]
            tel_raw = d.get('ddd_telefone_1', '') or d.get('ddd_telefone_2', '') or ''
            tel = re.sub(r"\D", "", tel_raw)
            cap_raw = d.get('capital_social', '') or ''
            try:
                cap = float(str(cap_raw).replace(",", "."))
                cap_fmt = f"R$ {cap:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                cap_fmt = str(cap_raw)
            return {
                'cnpj': _fmt_cnpj(cnpj_num),
                'razao_social': d.get('razao_social', ''),
                'situacao': d.get('descricao_situacao_cadastral', '') or d.get('situacao_cadastral', ''),
                'situacao_cnpj': d.get('descricao_situacao_cadastral', '') or d.get('situacao_cadastral', ''),
                'atividade': d.get('cnae_fiscal_descricao', '') or d.get('descricao_cnae_principal', ''),
                'atividade_principal': d.get('cnae_fiscal_descricao', '') or d.get('descricao_cnae_principal', ''),
                'data_abertura': d.get('data_inicio_atividade', ''),
                'capital': cap_fmt,
                'capital_social': cap_fmt,
                'natureza': d.get('descricao_natureza_juridica', ''),
                'natureza_juridica': d.get('descricao_natureza_juridica', ''),
                'telefone': tel,
                'telefone_cnpj': tel,
                'socios': ' | '.join(socios[:5]),
                'nome_dono': socios[0] if socios else '',
            }
    except Exception as e:
        logger.warning(f"CNPJWS erro: {e}")
    return {}


def enriquecer_cnpj(cnpj: str) -> dict:
    """Tenta as 3 APIs em sequência e retorna o primeiro resultado."""
    for fn in [_brasilapi, _receitaws, _cnpjws]:
        dados = fn(cnpj)
        if dados.get('razao_social'):
            return dados
        time.sleep(0.5)
    return {}


# TELEFONE
_DDD_ESTADOS = {
    '11': 'SP', '12': 'SP', '13': 'SP', '14': 'SP', '15': 'SP', '16': 'SP',
    '17': 'SP', '18': 'SP', '19': 'SP',
    '21': 'RJ', '22': 'RJ', '24': 'RJ',
    '27': 'ES', '28': 'ES',
    '31': 'MG', '32': 'MG', '33': 'MG', '34': 'MG', '35': 'MG', '37': 'MG', '38': 'MG',
    '41': 'PR', '42': 'PR', '43': 'PR', '44': 'PR', '45': 'PR', '46': 'PR',
    '47': 'SC', '48': 'SC', '49': 'SC',
    '51': 'RS', '53': 'RS', '54': 'RS', '55': 'RS',
    '61': 'DF', '62': 'GO', '63': 'TO', '64': 'GO',
    '65': 'MT', '66': 'MT', '67': 'MS', '68': 'AC', '69': 'RO',
    '71': 'BA', '73': 'BA', '74': 'BA', '75': 'BA', '77': 'BA',
    '79': 'SE', '81': 'PE', '82': 'AL', '83': 'PB', '84': 'RN', '85': 'CE',
    '86': 'PI', '87': 'PE', '88': 'CE', '89': 'PI',
    '91': 'PA', '92': 'AM', '93': 'PA', '94': 'PA', '95': 'RR', '96': 'AP',
    '97': 'AM', '98': 'MA', '99': 'MA',
}


def classificar_telefone(numero: str) -> str:
    """Classifica número como celular, fixo ou desconhecido."""
    num = re.sub(r'\D', '', numero)
    if num.startswith('55'):
        num = num[2:]
    if len(num) == 11 and num[2] == '9':
        return 'celular'
    if len(num) == 10 and num[2] in '2345':
        return 'fixo'
    if len(num) == 11 and num[2] in '2345':
        return 'fixo'
    if len(num) in (10, 11):
        return 'celular'
    return 'desconhecido'


def buscar_dono_telefone(numero: str) -> dict:
    """
    Busca informações do dono do telefone via múltiplas fontes.
    Retorna: {'nome': '', 'operadora': '', 'regiao': '', 'tipo': ''}
    """
    num = re.sub(r'\D', '', numero)
    if num.startswith('55'):
        num = num[2:]

    resultado = {
        'nome': '',
        'operadora': '',
        'regiao': '',
        'tipo': classificar_telefone(numero),
        'fonte': '',
        'snippet_google': '',
    }

    if len(num) >= 2:
        ddd = num[:2]
        resultado['regiao'] = _DDD_ESTADOS.get(ddd, 'Desconhecido')
        resultado['ddd'] = ddd

    # Tenta busca no Google via requests
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        busca = f"quem tem o número {numero} empresa"
        r = requests.get(
            f"https://www.google.com/search?q={requests.utils.quote(busca)}",
            headers=headers, timeout=8
        )
        if r.status_code == 200 and BS4_OK:
            soup = BeautifulSoup(r.text, 'html.parser')
            snippets = soup.find_all('div', class_='BNeawe')
            for s in snippets[:3]:
                text = s.get_text()
                if len(text) > 10 and text.strip():
                    resultado['snippet_google'] = text[:200]
                    break
    except Exception as e:
        logger.debug(f"Erro busca dono telefone: {e}")

    return resultado


# EMAIL
def extrair_emails_do_site(url: str) -> list:
    """
    Acessa o site e extrai todos os emails encontrados:
    - Na página principal
    - Na página de contato (/contato, /contact, /fale-conosco)
    - No rodapé
    """
    if not url:
        return []
    if not url.startswith('http'):
        url = 'https://' + url

    emails_encontrados = set()
    EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
    RUIDO = {'sentry', 'example', 'test', 'schema', 'jquery', 'noreply', 'no-reply',
             'exemplo', '@seudominio', 'voce@', 'email@', '@2x'}

    paginas = [url]
    for sufixo in ['/contato', '/contact', '/fale-conosco', '/sobre', '/about']:
        paginas.append(url.rstrip('/') + sufixo)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for pagina in paginas[:4]:
        try:
            r = requests.get(pagina, headers=headers, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                # Busca em texto puro
                emails = EMAIL_RE.findall(r.text)
                for e in emails:
                    if not any(x in e.lower() for x in RUIDO) and 6 < len(e) < 80:
                        emails_encontrados.add(e.lower())
                # Busca em href="mailto:..."
                if BS4_OK:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('mailto:'):
                            email = href[7:].split('?')[0].strip()
                            if email and 6 < len(email) < 80:
                                emails_encontrados.add(email.lower())
        except Exception:
            pass
        time.sleep(0.3)

    return list(emails_encontrados)[:5]


# REDES SOCIAIS
def buscar_redes_sociais(nome_empresa: str, site: str = "", cidade: str = "") -> dict:
    """
    Busca perfis nas redes sociais da empresa:
    - Instagram, Facebook, LinkedIn, TikTok, YouTube
    """
    redes = {'instagram': '', 'facebook': '', 'linkedin': '', 'tiktok': '', 'youtube': ''}

    PADROES = {
        'instagram': re.compile(r'instagram\.com/([A-Za-z0-9_.]+)', re.I),
        'facebook': re.compile(r'facebook\.com/([A-Za-z0-9_.]+)', re.I),
        'linkedin': re.compile(r'linkedin\.com/(?:company|in)/([A-Za-z0-9_\-]+)', re.I),
        'tiktok': re.compile(r'tiktok\.com/@([A-Za-z0-9_.]+)', re.I),
        'youtube': re.compile(r'youtube\.com/(?:channel|@|c)/([A-Za-z0-9_\-]+)', re.I),
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # 1. Scrape do próprio site
    if site:
        url = site if site.startswith('http') else 'https://' + site
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                for rede, pattern in PADROES.items():
                    m = pattern.search(r.text)
                    if m:
                        usuario = m.group(1).rstrip('/')
                        if not any(x in usuario.lower() for x in ['sharer', 'share', 'plugins']):
                            if rede == 'tiktok':
                                redes[rede] = f"https://www.tiktok.com/@{usuario}"
                            elif rede == 'linkedin':
                                redes[rede] = f"https://www.linkedin.com/company/{usuario}"
                            else:
                                redes[rede] = f"https://www.{rede}.com/{usuario}"
        except Exception:
            pass

    return redes


# ANÁLISE DE WEBSITE
def analisar_website(url: str) -> dict:
    """
    Analisa o website da empresa e retorna diagnóstico completo.
    """
    if not url:
        return {'tem_site': False, 'funciona': False, 'problemas': ['Sem website']}

    if not url.startswith('http'):
        url = 'https://' + url

    resultado = {
        'url': url,
        'tem_site': True,
        'funciona': False,
        'ssl': url.startswith('https'),
        'mobile_friendly': False,
        'cms_detectado': 'Desconhecido',
        'velocidade': 'desconhecido',
        'tem_whatsapp_widget': False,
        'tem_chat': False,
        'titulo': '',
        'meta_descricao': '',
        'ano_copyright': '',
        'problemas': [],
        'oportunidades': [],
    }

    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36'}

    try:
        inicio = time.time()
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        tempo = time.time() - inicio

        resultado['funciona'] = r.status_code == 200
        resultado['codigo_status'] = r.status_code

        # Velocidade
        if tempo < 2:
            resultado['velocidade'] = 'rápido'
        elif tempo < 5:
            resultado['velocidade'] = 'médio'
        else:
            resultado['velocidade'] = 'lento'
            resultado['problemas'].append(f'Site lento ({tempo:.1f}s de carregamento)')

        if r.status_code == 200:
            html = r.text

            if BS4_OK:
                soup = BeautifulSoup(html, 'html.parser')

                # Título
                title_tag = soup.find('title')
                resultado['titulo'] = title_tag.get_text().strip()[:80] if title_tag else ''

                # Meta description
                meta = soup.find('meta', attrs={'name': re.compile('description', re.I)})
                resultado['meta_descricao'] = meta.get('content', '')[:160] if meta else ''

                # Viewport (mobile-friendly)
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                resultado['mobile_friendly'] = viewport is not None

            # CMS detection
            cms_patterns = {
                'WordPress': ['/wp-content/', 'wp-includes', 'wordpress'],
                'Wix': ['wix.com', '_wix_', 'wixsite'],
                'Shopify': ['cdn.shopify.com', 'shopify'],
                'Squarespace': ['squarespace.com', 'sqsp'],
                'Webflow': ['webflow.io', 'webflow'],
                'VTEX': ['vtex.net', 'vtexcommercestable'],
                'Loja Integrada': ['lojaintegrada.com.br'],
                'Nuvemshop': ['lojavirtual.vip', 'nuvemshop'],
                'Tray': ['traycorp.com.br'],
                'Joomla': ['joomla', '/components/com_'],
                'Drupal': ['drupal', 'drupal.org'],
            }
            for cms, pats in cms_patterns.items():
                if any(p in html.lower() for p in pats):
                    resultado['cms_detectado'] = cms
                    break

            # WhatsApp widget
            wa_patterns = ['wa.me/', 'api.whatsapp.com', 'whatsapp', 'wpp']
            resultado['tem_whatsapp_widget'] = any(p in html.lower() for p in wa_patterns)

            # Chat widget
            chat_patterns = ['tawk.to', 'intercom', 'zendesk', 'freshchat', 'crisp.chat', 'livechat', 'jivochat']
            resultado['tem_chat'] = any(p in html.lower() for p in chat_patterns)

            # Copyright year
            copy_m = re.search(r'©\s*(\d{4})', html)
            if copy_m:
                resultado['ano_copyright'] = copy_m.group(1)
                if int(copy_m.group(1)) < 2022:
                    resultado['problemas'].append(f'Site desatualizado (copyright {copy_m.group(1)})')

            # Problemas e oportunidades
            if not resultado['ssl']:
                resultado['problemas'].append('Sem HTTPS (SSL)')
                resultado['oportunidades'].append('Implementar certificado SSL')
            if not resultado['mobile_friendly']:
                resultado['problemas'].append('Sem viewport mobile')
                resultado['oportunidades'].append('Tornar site responsivo para mobile')
            if not resultado.get('meta_descricao'):
                resultado['problemas'].append('Sem meta description (SEO ruim)')
                resultado['oportunidades'].append('Adicionar meta descriptions para SEO')
            if not resultado.get('titulo'):
                resultado['problemas'].append('Sem título na página')
            if resultado['velocidade'] == 'lento':
                resultado['oportunidades'].append('Otimizar velocidade do site')
            if not resultado['tem_whatsapp_widget']:
                resultado['oportunidades'].append('Adicionar botão WhatsApp no site')

    except requests.exceptions.SSLError:
        resultado['problemas'].append('Erro SSL — certificado inválido ou expirado')
        resultado['ssl'] = False
    except requests.exceptions.ConnectionError:
        resultado['funciona'] = False
        resultado['problemas'].append('Site fora do ar ou domínio não encontrado')
    except Exception as e:
        resultado['funciona'] = False
        resultado['problemas'].append(f'Erro ao acessar site: {str(e)[:50]}')

    return resultado


# SEO BÁSICO
def analisar_seo(url: str, nome_empresa: str = "", nicho: str = "") -> dict:
    """
    Análise SEO básica com score de 0 a 100.
    """
    seo = {
        'score': 0,
        'tem_h1': False,
        'tem_h2': False,
        'h1_texto': '',
        'imagens_sem_alt': 0,
        'total_imagens': 0,
        'tem_schema': False,
        'tem_og_tags': False,
        'tem_sitemap': False,
        'tem_robots': False,
        'palavras_chave_titulo': False,
        'detalhes': [],
        'classificacao': 'Ruim',
    }

    if not url:
        return seo

    if not url.startswith('http'):
        url = 'https://' + url

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return seo

        score = 0

        if BS4_OK:
            soup = BeautifulSoup(r.text, 'html.parser')

            # H1
            h1 = soup.find('h1')
            if h1:
                seo['tem_h1'] = True
                seo['h1_texto'] = h1.get_text().strip()[:80]
                score += 15
            else:
                seo['detalhes'].append('Sem tag H1')

            # H2
            if soup.find('h2'):
                seo['tem_h2'] = True
                score += 5

            # Imagens sem alt
            imgs = soup.find_all('img')
            seo['total_imagens'] = len(imgs)
            seo['imagens_sem_alt'] = sum(1 for i in imgs if not i.get('alt'))
            if seo['imagens_sem_alt'] == 0 and len(imgs) > 0:
                score += 10
            elif seo['imagens_sem_alt'] > 0:
                seo['detalhes'].append(f'{seo["imagens_sem_alt"]} imagens sem alt text')

            # Schema.org
            if 'schema.org' in r.text or 'application/ld+json' in r.text:
                seo['tem_schema'] = True
                score += 15
            else:
                seo['detalhes'].append('Sem Schema.org markup')

            # Open Graph
            og = soup.find('meta', property='og:title')
            if og:
                seo['tem_og_tags'] = True
                score += 10

            # Meta title e description
            title = soup.find('title')
            meta_desc = soup.find('meta', attrs={'name': re.compile('description', re.I)})
            if title and title.get_text().strip():
                score += 10
            if meta_desc and meta_desc.get('content', '').strip():
                score += 10

            # Palavra-chave no título
            if title and nicho:
                if nicho.lower() in title.get_text().lower():
                    seo['palavras_chave_titulo'] = True
                    score += 10

        # Schema.org (backup sem BS4)
        else:
            if 'schema.org' in r.text or 'application/ld+json' in r.text:
                seo['tem_schema'] = True
                score += 15

        # Sitemap
        try:
            base = url.split('/')[0] + '//' + url.split('/')[2]
            rs = requests.get(base + '/sitemap.xml', timeout=5)
            if rs.status_code == 200:
                seo['tem_sitemap'] = True
                score += 10
        except Exception:
            pass

        # Robots.txt
        try:
            base = url.split('/')[0] + '//' + url.split('/')[2]
            rr = requests.get(base + '/robots.txt', timeout=5)
            if rr.status_code == 200:
                seo['tem_robots'] = True
                score += 5
        except Exception:
            pass

        seo['score'] = min(score, 100)

        # Classifica score
        if seo['score'] >= 70:
            seo['classificacao'] = 'Bom'
        elif seo['score'] >= 40:
            seo['classificacao'] = 'Regular'
        else:
            seo['classificacao'] = 'Ruim'
            seo['detalhes'].append('SEO muito fraco — grande oportunidade de melhoria')

    except Exception as e:
        logger.debug(f"Erro análise SEO: {e}")

    return seo


# SCORE DIGITAL
def calcular_score_oportunidade(lead: dict) -> dict:
    """
    Calcula pontuação de oportunidade de venda (0 a 100).
    Quanto MAIOR o score, MAIOR a oportunidade (lead mais quente).
    """
    score = 0
    motivos = []

    site = lead.get('website', '') or lead.get('site', '')

    if not site or str(site).strip() in ['', 'N/A', '-']:
        score += 35
        motivos.append('Sem website (+35)')
    else:
        analise = lead.get('_analise_site', {})
        if analise:
            if not analise.get('funciona', True):
                score += 25
                motivos.append('Site fora do ar (+25)')
            elif analise.get('velocidade') == 'lento':
                score += 10
                motivos.append('Site lento (+10)')
            if not analise.get('mobile_friendly', True):
                score += 10
                motivos.append('Nao e responsivo/mobile (+10)')
            if analise.get('ano_copyright'):
                try:
                    if int(analise.get('ano_copyright', '2024')) < 2021:
                        score += 10
                        motivos.append(f'Site desatualizado (+10)')
                except Exception:
                    pass

        seo = lead.get('_seo', {})
        if seo and seo.get('score', 100) < 40:
            score += 15
            motivos.append(f'SEO fraco ({seo.get("score", 0)}/100) (+15)')

    # Redes sociais
    redes = lead.get('_redes', {})
    redes_ativas = sum(1 for v in (redes or {}).values() if v)
    if redes_ativas == 0:
        score += 10
        motivos.append('Sem redes sociais (+10)')

    # Reviews
    try:
        reviews = int(str(lead.get('reviews', lead.get('num_reviews', lead.get('avaliacoes', '0')))).replace(',', '').split()[0])
        if reviews < 5:
            score += 10
            motivos.append(f'Poucos reviews ({reviews}) (+10)')
        elif reviews < 20:
            score += 5
    except Exception:
        pass

    # Rating
    try:
        rating_raw = str(lead.get('rating', lead.get('nota', '5'))).replace(',', '.')
        rating = float(rating_raw)
        if rating < 3.5:
            score += 5
            motivos.append(f'Rating baixo ({rating}) (+5)')
    except Exception:
        pass

    score = min(score, 100)

    if score >= 70:
        prioridade = 'ALTA'
    elif score >= 40:
        prioridade = 'MEDIA'
    else:
        prioridade = 'BAIXA'

    return {
        'score': score,
        'prioridade': prioridade,
        'motivos': motivos,
    }
