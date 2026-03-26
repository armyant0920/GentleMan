import re, json, sys

with open('messages.html', 'r', encoding='utf-8') as f:
    content = f.read()

entries = []
pattern = re.compile(r'<img class="photo" src="(photos/[^"]+_thumb\.jpg)"[^>]*/>\s*</a>\s*</div>\s*<div class="text">\s*(\U0001F525.*?)\s*</div>', re.DOTALL)

matches = list(pattern.finditer(content))

FIRE = '\U0001F525'
PERSON = '\U0001F464'
LOCATION = '\U0001F4CD'
BUILDING = '\U0001F3E2'
MONEY = '\U0001F4B0'
CHECK = '\u2705'
STAR = '\u2B50'

for m in matches:
    photo = m.group(1)
    raw = m.group(2)

    # Replace <br> with newline, remove other HTML tags
    raw = re.sub(r'<br>', '\n', raw)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = raw.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

    # Parse name/nationality from first line: "🔥 Name（Nationality）"
    name_match = re.match(FIRE + r'\s*(.+?)\uff08(.+?)\uff09', raw)
    if name_match:
        name = name_match.group(1).strip()
        nationality = name_match.group(2).strip()
    else:
        name_match2 = re.match(FIRE + r'\s*(\S+)', raw)
        name = name_match2.group(1).strip() if name_match2 else ''
        nationality = ''

    # Parse height/weight/cup
    body_match = re.search(r'(\d+\.?\d*)cm\s*/\s*(\d+\.?\d*)kg\s*/\s*([A-Z+]+)', raw)
    if body_match:
        height = body_match.group(1)
        weight = body_match.group(2)
        cup = body_match.group(3)
    else:
        body_match2 = re.search(r'(\d+\.?\d*)cm\s*/\s*([A-Z+]+)', raw)
        if body_match2:
            height = body_match2.group(1)
            weight = ''
            cup = body_match2.group(2)
        else:
            height = weight = cup = ''

    # Parse district: after "地區：", get hashtags
    dist_section = re.search(r'\u5730\u5340\uff1a(.+?)(?:\n\n|\n' + BUILDING + r')', raw, re.DOTALL)
    if dist_section:
        hashtags = re.findall(r'#(\S+)', dist_section.group(1))
        district = hashtags[1] if len(hashtags) >= 2 else (hashtags[0] if hashtags else '')
    else:
        district = ''

    # Parse svctype
    svc_match = re.search(r'\u670d\u52d9\u65b9\u5f0f\uff1a#(\S+)', raw)
    svctype = svc_match.group(1) if svc_match else ''

    # Parse short price (短鐘)
    short_match = re.search(r'\u77ed\u9418\uff1a\$([\d.]+)', raw)
    shortPrice = float(short_match.group(1)) if short_match else None

    # Parse long price (長鐘)
    long_match = re.search(r'\u9577\u9418\uff1a\$([\d.]+)', raw)
    longPrice = float(long_match.group(1)) if long_match else None

    # Parse basic services (基本服務)
    svc_basic = re.search(CHECK + r'\s*\u57fa\u672c\u670d\u52d9\uff1a\n(.+?)(?=\n\n|\n' + STAR + r')', raw, re.DOTALL)
    if svc_basic:
        services_raw = svc_basic.group(1).strip()
        services = [s.strip() for s in services_raw.split(',') if s.strip()]
    else:
        services = []

    # Parse extra services (加值服務) - \u503c is the correct char for 值
    extra_match = re.search(STAR + r'\s*\u52a0\u503c\u670d\u52d9\uff1a\n(.+?)$', raw, re.DOTALL)
    extraServices = extra_match.group(1).strip() if extra_match else ''

    entry = {
        'name': name,
        'nationality': nationality,
        'height': height,
        'weight': weight,
        'cup': cup,
        'district': district,
        'svctype': svctype,
        'shortPrice': shortPrice,
        'longPrice': longPrice,
        'services': services,
        'extraServices': extraServices,
        'photo': photo
    }
    entries.append(entry)

with open('output_entries.json', 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

sys.stdout.reconfigure(encoding='utf-8')
print(f'Total entries: {len(entries)}')
# Check extraServices
with_extra = [e for e in entries if e['extraServices']]
print(f'Entries with extraServices: {len(with_extra)}')
if with_extra:
    print(f'Sample extraServices: {with_extra[0]["extraServices"][:80]}')
