"""
Listas de nichos e cidades usadas na prospeccao.
"""

import json
from itertools import product

# NICHOS — organizados por categoria
NICHOS_GRINGA = {
    "Saúde": [
        "dentist", "dental clinic", "orthodontist", "chiropractor",
        "physical therapist", "optometrist", "dermatologist",
        "pediatrician", "psychologist", "nutritionist",
        "veterinarian", "animal clinic",
    ],
    "Beleza & Bem-estar": [
        "barbershop", "hair salon", "nail salon", "spa",
        "massage therapy", "tattoo studio", "eyebrow threading",
        "beauty clinic", "aesthetic clinic",
    ],
    "Fitness": [
        "gym", "fitness studio", "personal trainer",
        "yoga studio", "pilates studio", "crossfit box",
        "martial arts", "dance studio", "swimming pool",
    ],
    "Alimentação": [
        "restaurant", "cafe", "bakery", "food truck",
        "catering service", "meal prep", "juice bar",
        "pizzeria", "sushi restaurant", "steakhouse",
    ],
    "Serviços Profissionais": [
        "law firm", "attorney", "accountant", "tax consultant",
        "financial advisor", "insurance agency", "real estate agent",
        "mortgage broker", "notary public",
    ],
    "Educação": [
        "tutoring center", "language school", "music school",
        "art school", "driving school", "coding bootcamp",
        "daycare", "preschool", "private school",
    ],
    "Construção & Casa": [
        "contractor", "plumber", "electrician", "landscaping",
        "roofing company", "interior designer", "cleaning service",
        "moving company", "pest control", "HVAC",
    ],
    "Varejo & Moda": [
        "boutique", "clothing store", "shoe store",
        "jewelry store", "gift shop", "florist",
        "furniture store", "home decor",
    ],
    "Automotivo": [
        "auto repair", "car dealership", "car wash",
        "auto detailing", "tire shop", "towing service",
    ],
    "Eventos & Entretenimento": [
        "event venue", "wedding photographer", "photographer",
        "videographer", "DJ service", "catering",
        "escape room", "party supply",
    ],
    "Imóveis": [
        "real estate agency", "property management",
        "real estate developer", "home staging",
    ],
    "Tecnologia": [
        "IT support", "computer repair", "phone repair",
        "web design agency", "digital marketing agency",
    ],
}

NICHOS_BRASIL = {
    "Saúde": [
        "dentista", "clínica odontológica", "ortodontista",
        "fisioterapeuta", "psicólogo", "nutricionista",
        "médico", "clínica médica", "dermatologista",
        "oftalmologista", "pediatra", "veterinário",
        "clínica veterinária", "pet shop",
    ],
    "Beleza & Bem-estar": [
        "barbearia", "salão de beleza", "cabeleireiro",
        "manicure", "spa", "estética", "clínica de estética",
        "tatuagem", "micropigmentação", "sobrancelha",
    ],
    "Fitness": [
        "academia", "personal trainer", "crossfit",
        "yoga", "pilates", "artes marciais",
        "escola de dança", "natação",
    ],
    "Alimentação": [
        "restaurante", "lanchonete", "padaria", "cafeteria",
        "pizzaria", "churrascaria", "hamburgueria",
        "sorveteria", "doceria", "marmitaria",
        "buffet", "sushi", "delivery",
    ],
    "Serviços Profissionais": [
        "advocacia", "advogado", "contabilidade", "contador",
        "consultoria financeira", "corretora de seguros",
        "despachante", "cartório", "imobiliária",
    ],
    "Educação": [
        "escola de idiomas", "curso de inglês",
        "escola de música", "escola de artes",
        "autoescola", "reforço escolar", "creche",
        "escola particular", "curso técnico",
    ],
    "Construção & Casa": [
        "construtora", "empreiteiro", "encanador",
        "eletricista", "jardinagem", "dedetização",
        "reforma", "pintor", "marceneiro",
        "decoração", "limpeza", "mudança",
    ],
    "Varejo": [
        "boutique", "loja de roupas", "calçados",
        "joalheria", "floricultura", "ótica",
        "loja de móveis", "pet shop",
    ],
    "Automotivo": [
        "oficina mecânica", "concessionária", "lava-rápido",
        "borracharia", "funilaria", "despachante veicular",
    ],
    "Imóveis": [
        "imobiliária", "corretor de imóveis",
        "construtora", "incorporadora",
    ],
    "Eventos": [
        "buffet", "fotógrafo", "videógrafo",
        "decoração de festas", "DJ", "cerimonialista",
        "salão de festas", "espaço para eventos",
    ],
}

# CIDADES POR ESTADO (Brasil)
CIDADES_BRASIL = {
    "PR": [
        "Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel",
        "São José dos Pinhais", "Foz do Iguaçu", "Colombo", "Guarapuava",
        "Paranaguá", "Araucária", "Toledo", "Apucarana", "Pinhais",
        "Campo Largo", "Almirante Tamandaré", "Umuarama", "Cambé",
        "Paranavaí", "Francisco Beltrão",
    ],
    "SP": [
        "São Paulo", "Campinas", "Guarulhos", "Santo André", "São Bernardo do Campo",
        "Osasco", "Ribeirão Preto", "Sorocaba", "Mauá", "São José dos Campos",
        "Santos", "Mogi das Cruzes", "Jundiaí", "Piracicaba", "Carapicuíba",
        "Bauru", "Itaquaquecetuba", "São Vicente", "Franca", "Guarujá",
        "Taubaté", "Limeira", "Suzano", "Praia Grande", "Barueri",
        "Americana", "Diadema", "Marília", "Araraquara", "Cotia",
    ],
    "RJ": [
        "Rio de Janeiro", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu",
        "Niterói", "Belford Roxo", "Campos dos Goytacazes", "São João de Meriti",
        "Petrópolis", "Volta Redonda", "Macaé", "Magé", "Itaboraí",
        "Mesquita", "Nova Friburgo", "Barra Mansa", "Angra dos Reis",
        "Nilópolis", "Cabo Frio", "Teresópolis",
    ],
    "MG": [
        "Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora",
        "Betim", "Montes Claros", "Ribeirão das Neves", "Uberaba",
        "Governador Valadares", "Ipatinga", "Sete Lagoas", "Divinópolis",
        "Santa Luzia", "Ibirité", "Poços de Caldas", "Patos de Minas",
        "Pouso Alegre", "Teófilo Otoni", "Barbacena", "Sabará",
    ],
    "RS": [
        "Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria",
        "Gravataí", "Viamão", "Novo Hamburgo", "São Leopoldo", "Rio Grande",
        "Alvorada", "Passo Fundo", "Sapucaia do Sul", "Uruguaiana", "Santa Cruz do Sul",
        "Cachoeirinha", "Bagé", "Lajeado", "Erechim", "Sapiranga",
    ],
    "BA": [
        "Salvador", "Feira de Santana", "Vitória da Conquista", "Camaçari",
        "Itabuna", "Juazeiro", "Lauro de Freitas", "Ilhéus", "Jequié",
        "Teixeira de Freitas", "Alagoinhas", "Barreiras", "Porto Seguro",
        "Simões Filho", "Paulo Afonso", "Eunápolis", "Santo Antônio de Jesus",
    ],
    "SC": [
        "Joinville", "Florianópolis", "Blumenau", "São José", "Criciúma",
        "Chapecó", "Itajaí", "Jaraguá do Sul", "Lages", "Palhoça",
        "Balneário Camboriú", "Brusque", "Tubarão", "São Bento do Sul",
        "Caçador", "Concórdia", "Camboriú", "Navegantes", "Indaial",
    ],
    "GO": [
        "Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde",
        "Luziânia", "Águas Lindas de Goiás", "Valparaíso de Goiás",
        "Trindade", "Formosa", "Novo Gama", "Itumbiara", "Senador Canedo",
        "Jataí", "Catalão", "Planaltina",
    ],
    "CE": [
        "Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú",
        "Sobral", "Crato", "Itapipoca", "Maranguape", "Iguatu",
        "Quixadá", "Pacatuba", "Canindé", "Aquiraz",
    ],
    "PE": [
        "Recife", "Caruaru", "Olinda", "Petrolina", "Paulista",
        "Camaçari", "Vitória de Santo Antão", "Garanhuns",
        "Jaboatão dos Guararapes", "Cabo de Santo Agostinho",
    ],
    "AM": [
        "Manaus", "Parintins", "Itacoatiara", "Manacapuru",
        "Coari", "Tefé", "Maués", "Tabatinga",
    ],
    "PA": [
        "Belém", "Ananindeua", "Santarém", "Marabá",
        "Castanhal", "Abaetetuba", "Cametá", "Bragança",
    ],
    "MT": [
        "Cuiabá", "Várzea Grande", "Rondonópolis", "Sinop",
        "Tangará da Serra", "Cáceres", "Sorriso", "Lucas do Rio Verde",
    ],
    "MS": [
        "Campo Grande", "Dourados", "Três Lagoas", "Corumbá",
        "Ponta Porã", "Naviraí", "Nova Andradina",
    ],
    "DF": ["Brasília", "Taguatinga", "Ceilândia", "Samambaia", "Planaltina"],
    "ES": [
        "Vitória", "Vila Velha", "Serra", "Cariacica",
        "Linhares", "Cachoeiro de Itapemirim", "Colatina",
    ],
    "AL": [
        "Maceió", "Arapiraca", "Rio Largo", "Palmeira dos Índios",
        "União dos Palmares",
    ],
    "RN": [
        "Natal", "Mossoró", "Parnamirim", "São Gonçalo do Amarante",
        "Caicó", "Assu",
    ],
    "PB": [
        "João Pessoa", "Campina Grande", "Santa Rita", "Patos",
        "Bayeux", "Sousa",
    ],
    "PI": [
        "Teresina", "Parnaíba", "Picos", "Piripiri", "Floriano",
    ],
    "MA": [
        "São Luís", "Imperatriz", "Caxias", "Timon",
        "Codó", "Açailândia", "Bacabal",
    ],
    "TO": [
        "Palmas", "Araguaína", "Gurupi", "Porto Nacional",
    ],
    "RO": [
        "Porto Velho", "Ji-Paraná", "Ariquemes", "Cacoal",
    ],
    "AC": ["Rio Branco", "Cruzeiro do Sul", "Sena Madureira"],
    "RR": ["Boa Vista", "Rorainópolis"],
    "AP": ["Macapá", "Santana"],
}

# CIDADES POR ESTADO (EUA — Gringa)
CIDADES_USA = {
    "TX": [
        "Austin", "Dallas", "Houston", "San Antonio", "Fort Worth",
        "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo",
        "Lubbock", "Garland", "Irving", "Amarillo", "Grand Prairie",
        "McKinney", "Frisco", "Pasadena", "Mesquite", "Killeen",
        "Waco", "Carrollton", "Denton", "Midland", "Odessa",
    ],
    "FL": [
        "Miami", "Orlando", "Tampa", "Jacksonville", "St. Petersburg",
        "Hialeah", "Tallahassee", "Fort Lauderdale", "Cape Coral",
        "Pembroke Pines", "Hollywood", "Gainesville", "Miramar",
        "Coral Springs", "Clearwater", "Palm Bay", "Lakeland",
        "Pompano Beach", "West Palm Beach", "Davie",
    ],
    "CA": [
        "Los Angeles", "San Diego", "San Jose", "San Francisco",
        "Fresno", "Sacramento", "Long Beach", "Oakland", "Bakersfield",
        "Anaheim", "Santa Ana", "Stockton", "Riverside", "Irvine",
        "Chula Vista", "Fremont", "San Bernardino", "Modesto",
        "Fontana", "Moreno Valley",
    ],
    "NY": [
        "New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse",
        "Albany", "New Rochelle", "Mount Vernon", "Schenectady", "Utica",
        "White Plains", "Hempstead", "Troy", "Niagara Falls", "Binghamton",
    ],
    "GA": [
        "Atlanta", "Augusta", "Columbus", "Savannah", "Athens",
        "Sandy Springs", "Roswell", "Macon", "Johns Creek", "Albany",
        "Warner Robins", "Alpharetta", "Marietta", "Valdosta", "Smyrna",
    ],
    "NC": [
        "Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem",
        "Fayetteville", "Cary", "Wilmington", "High Point", "Concord",
        "Gastonia", "Greenville", "Asheville", "Jacksonville", "Chapel Hill",
    ],
    "OH": [
        "Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron",
        "Dayton", "Parma", "Canton", "Youngstown", "Lorain",
        "Hamilton", "Springfield", "Kettering", "Elyria", "Lakewood",
    ],
    "PA": [
        "Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading",
        "Scranton", "Bethlehem", "Lancaster", "Harrisburg", "Altoona",
    ],
    "AZ": [
        "Phoenix", "Tucson", "Mesa", "Chandler", "Glendale",
        "Scottsdale", "Gilbert", "Tempe", "Peoria", "Surprise",
        "Yuma", "Avondale", "Flagstaff", "Goodyear", "Buckeye",
    ],
    "CO": [
        "Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood",
        "Thornton", "Arvada", "Westminster", "Pueblo", "Centennial",
        "Boulder", "Highlands Ranch", "Greeley", "Longmont", "Loveland",
    ],
    "WA": [
        "Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue",
        "Kent", "Everett", "Renton", "Kirkland", "Redmond",
        "Bellingham", "Federal Way", "Kennewick", "Yakima",
    ],
    "TN": [
        "Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville",
        "Murfreesboro", "Franklin", "Jackson", "Johnson City", "Bartlett",
    ],
    "IN": [
        "Indianapolis", "Fort Wayne", "Evansville", "South Bend",
        "Carmel", "Fishers", "Bloomington", "Hammond", "Lafayette",
    ],
    "MO": [
        "Kansas City", "St. Louis", "Springfield", "Columbia",
        "Independence", "Lee's Summit", "O'Fallon", "St. Joseph",
    ],
    "NV": [
        "Las Vegas", "Henderson", "Reno", "North Las Vegas",
        "Sparks", "Carson City", "Fernley",
    ],
    "MI": [
        "Detroit", "Grand Rapids", "Warren", "Sterling Heights",
        "Ann Arbor", "Lansing", "Flint", "Dearborn", "Livonia",
    ],
    "IL": [
        "Chicago", "Aurora", "Naperville", "Joliet", "Rockford",
        "Springfield", "Elgin", "Peoria", "Champaign", "Waukegan",
    ],
    "MA": [
        "Boston", "Worcester", "Springfield", "Lowell", "Cambridge",
        "New Bedford", "Brockton", "Quincy", "Lynn", "Fall River",
    ],
    "VA": [
        "Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News",
        "Alexandria", "Hampton", "Roanoke", "Portsmouth", "Suffolk",
    ],
    "OR": [
        "Portland", "Salem", "Eugene", "Gresham", "Hillsboro",
        "Beaverton", "Bend", "Medford", "Springfield", "Corvallis",
    ],
}


# Funções utilitárias
def listar_estados(modo: str = "brasil"):
    db = CIDADES_BRASIL if modo == "brasil" else CIDADES_USA
    print(f"\nEstados disponíveis ({modo.upper()}):\n")
    for estado, cidades in sorted(db.items()):
        print(f"  {estado:5} -> {len(cidades)} cidades")
    print()


def obter_nichos(modo: str, categorias: list = None) -> dict:
    db = NICHOS_BRASIL if modo == "brasil" else NICHOS_GRINGA
    if not categorias:
        return db
    return {k: v for k, v in db.items() if k in categorias}


def obter_cidades(estado: str, modo: str) -> list:
    db = CIDADES_BRASIL if modo == "brasil" else CIDADES_USA
    estado_upper = estado.upper()
    if estado_upper not in db:
        raise ValueError(
            f"Estado '{estado}' não encontrado. "
            f"Use listar_estados() para ver os disponíveis."
        )
    return db[estado_upper]


def gerar_combinacoes(
    estado: str,
    modo: str = "brasil",
    categorias: list = None,
    max_nichos_por_categoria: int = 5,
    max_cidades: int = None,
) -> list:
    """
    Retorna lista de {'nicho': ..., 'cidade': ..., 'categoria': ...}
    priorizando nichos com maior potencial (primeiros da lista).
    """
    nichos_db = obter_nichos(modo, categorias)
    cidades   = obter_cidades(estado, modo)

    if max_cidades:
        cidades = cidades[:max_cidades]

    combinacoes = []
    for categoria, nichos in nichos_db.items():
        nichos_selecionados = nichos[:max_nichos_por_categoria]
        for nicho, cidade in product(nichos_selecionados, cidades):
            combinacoes.append({
                "nicho":     nicho,
                "cidade":    cidade,
                "estado":    estado.upper(),
                "categoria": categoria,
                "modo":      modo,
            })

    return combinacoes


def resumo_combinacoes(combinacoes: list):
    total      = len(combinacoes)
    categorias = {}
    cidades    = set()
    nichos     = set()
    for c in combinacoes:
        categorias[c["categoria"]] = categorias.get(c["categoria"], 0) + 1
        cidades.add(c["cidade"])
        nichos.add(c["nicho"])

    print(f"\nRESUMO DAS COMBINACOES")
    print("-" * 40)
    print(f"  Total de buscas: {total:,}")
    print(f"  Cidades:         {len(cidades)}")
    print(f"  Nichos únicos:   {len(nichos)}")
    print(f"\n  Por categoria:")
    for cat, qtd in sorted(categorias.items(), key=lambda x: -x[1]):
        print(f"    {cat:<30} {qtd:>5}")
    print()


def exportar_json(combinacoes: list, caminho: str = "combinacoes.json"):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(combinacoes, f, ensure_ascii=False, indent=2)
    print(f"Exportado: {caminho} ({len(combinacoes)} combinações)")
