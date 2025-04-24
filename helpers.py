import re

# Константы
BASE_URL = 'https://moto.av.by'
SITE = '.de' in BASE_URL  # Проверяем, содержит ли URL '.de'
FILTER_URL = BASE_URL if SITE else f"{BASE_URL}/filter?category_type=1&brands[0][brand]="
CHUNK_MODEL = 'vhc:motorbike,srt:year,sro:desc,mke:' if SITE else '&brands[0][model]='
CHUNK_YEAR = '&brands[0][year][min]='
CHUNK_PRICE = '&price_usd[max]='

# Маппинг брендов
BRAND = {
    'APRILIA': 'aprilia',
    'HONDA': 'honda',
    'YAMAHA': 'yamaha',
    'BMW': 'bmw',
    'HD': 'hd',
}

# Маппинг моделей
MODEL = {
    'APRILIA_TUAREG': 'tuareg',
    'APRILIA_RS': 'rs',
    'HONDA_CB': 'cb',
    'HONDA_TRANSALP': 'transalp',
    'YAMAHA_XSR': 'xsr',
    'YAMAHA_XV': 'xv',
    'HD_SG': 'sg',
    'HD_CVO': 'cvo',
    'HD_SOFT': 'soft',
    'HD_RG': 'rg',
    'HD_FB': 'fb',
    'HD_RK': 'rk',
    'HD_FTB': 'ftb',
    'BMW_R': 'r',
    'BMW_S': 's',
    'BMW_K': 'k',
    'BMW_F': 'f',
    'BMW_G': 'g',
}

# Маппинг ID для av.by
AVBY = {
    'APRILIA': '2731',
    'HONDA': '383',
    'YAMAHA': '2875',
}

# Маппинг ID для mobile.de
MOBILEDE = {
    'APRILIA_RS': '1500,mld:rs',
    'TUAREG': '1500,mld:tuareg',
    'HONDA_CB': '11000,mld:cb',
    'TRANSALP': '11000,mld:transalp',
    'YAMAHA_XSR': '26000,mld:xsr',
}

# Структура моделей для поиска
MODELS_SEARCH = [
    {'brand': 'aprilia', 'model': ['rs', 'tuareg']},
    {'brand': 'honda', 'model': ['cb', 'transalp']},
    {'brand': 'yamaha', 'model': ['xsr', 'xv']},
    {'brand': 'bmw', 'model': ['r', 's', 'k', 'g', 'f']},
    {'brand': 'hd', 'model': ['sg', 'cvo', 'soft', 'rg', 'fb', 'rk', 'ftb']},
]

NON_CLICKABLE_BRANDS = ['honda', 'yamaha', 'bmw', 'hd']

# Структура клавиатуры моделей
MODEL_KEYBOARD = [
    {'model': [{'rs': 'rs'}, {'tuareg': 'tuareg'}]},
    {'model': [{'cb': 'cb'}, {'transalp': 'transalp'}]},
    {'model': [{'xsr': 'xsr'}, {'xv': 'xv'}]},
    {'model': [{'r': 'r'}, {'s': 's'}, {'k': 'k'}, {'g': 'g'}, {'f': 'f'}]},
    {'model': [
        {'sg': 'street glide'}, {'cvo': 'cvo'},
        {'soft': 'softail'}, {'rg': 'road glide'},
        {'fb': 'fat boy'}, {'rk': 'road king'},
        {'ftb': 'fat bob'}
    ]}
]

# Вспомогательные функции
def is_number(s):
    """Проверяет, является ли строка числом."""
    return bool(re.match(r'^\d+$', s))

def find_model(model):
    """Находит отображаемое имя модели."""
    k = model.lower()
    found_model = '-'
    for group in MODEL_KEYBOARD:
        for m in group['model']:
            if k in m:
                found_model = m[k]
                break
        if found_model != '-':
            break
    return found_model

def find_model_by_brand(model):
    """Находит бренд по модели."""
    m = model.lower()
    if not m or is_number(m):
        return False
    if m in NON_CLICKABLE_BRANDS:
        return m
    for item in MODELS_SEARCH:
        if m in item.get('model', []):
            return item['brand']
    return False

# Основная функция для формирования URL
def create_link(model, year, price, sort=False):
    """Формирует URL для поиска на основе модели, года, цены и сортировки."""
    url = ''
    model_lower = model.lower()

    # Определяем бренд
    brand = find_model_by_brand(model_lower)

    if brand == BRAND['APRILIA']:
        if model_lower == MODEL['APRILIA_TUAREG']:
            url += f"{model_lower}/{CHUNK_MODEL}{MOBILEDE['TUAREG']}" if SITE else ''
        elif model_lower == MODEL['APRILIA_RS']:
            url += f"{model_lower}/{CHUNK_MODEL}{MOBILEDE['APRILIA_RS']}" if SITE else f"{AVBY['APRILIA']}{CHUNK_MODEL}3118"

    elif brand == BRAND['HONDA']:
        if model_lower == MODEL['HONDA_CB']:
            url += f"{model_lower}/{CHUNK_MODEL}{MOBILEDE['HONDA_CB']}" if SITE else f"{AVBY['HONDA']}{CHUNK_MODEL}2914"
        elif model_lower == MODEL['HONDA_TRANSALP']:
            url += f"{model_lower}/{CHUNK_MODEL}{MOBILEDE['TRANSALP']}" if SITE else f"{AVBY['HONDA']}{CHUNK_MODEL}5647"

    elif brand == BRAND['YAMAHA']:
        url += MOBILEDE.get('YAMAHA', '') if SITE else AVBY['YAMAHA']
        if model_lower == MODEL['YAMAHA_XSR']:
            url += f"{model_lower}" if SITE else f"{CHUNK_MODEL}5704"
        elif model_lower == MODEL['YAMAHA_XV']:
            url += f"{CHUNK_MODEL}4622"

    elif brand == BRAND['HD']:
        url += '2774'
        if model_lower == MODEL['HD_SG']:
            url += f"{CHUNK_MODEL}5880"
        elif model_lower == MODEL['HD_CVO']:
            url += f"{CHUNK_MODEL}3522"
        elif model_lower == MODEL['HD_SOFT']:
            url += f"{CHUNK_MODEL}3524"
        elif model_lower == MODEL['HD_RG']:
            url += f"{CHUNK_MODEL}5652"
        elif model_lower == MODEL['HD_FB']:
            url += f"{CHUNK_MODEL}10025"
        elif model_lower == MODEL['HD_RK']:
            url += f"{CHUNK_MODEL}5640"
        elif model_lower == MODEL['HD_FTB']:
            url += f"{CHUNK_MODEL}10037"

    elif brand == BRAND['BMW']:
        url += '8'
        if model_lower == MODEL['BMW_R']:
            url += f"{CHUNK_MODEL}2910"
        elif model_lower == MODEL['BMW_S']:
            url += f"{CHUNK_MODEL}2912"
        elif model_lower == MODEL['BMW_K']:
            url += f"{CHUNK_MODEL}2909"
        elif model_lower == MODEL['BMW_F']:
            url += f"{CHUNK_MODEL}2905"
        elif model_lower == MODEL['BMW_G']:
            url += f"{CHUNK_MODEL}2906"

    # Добавляем год и цену
    if is_number(model):
        url += f"{CHUNK_YEAR}{model}"
        if year:
            url += f"{CHUNK_PRICE}{year}"
    else:
        if year:
            url += f",frn:{year}" if SITE else f"{CHUNK_YEAR}{year}"
        if price:
            url += f",prn:1000,prx:{price}" if SITE else f"{CHUNK_PRICE}{price}"

    # Добавляем сортировку
    if sort:
        url += "&sort=4"

    return FILTER_URL + url