import os
import re
import json
import random
import urllib.parse
import pandas as pd

def main():
    cleaned_descriptions = {}
    with open(r'E:\Project\testing_ViT\cleaned.txt', 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    entries = text.split('====================================================================================================')
    for e in entries:
        title_match = re.search(r'TITLE:\s*(.+)', e)
        handle_match = re.search(r'HANDLE:\s*(.+)', e)
        body_match = re.search(r'BODY_HTML:\s*\'?([\s\S]+?)\'?$', e)
        if title_match:
            t = title_match.group(1).strip()
            h = handle_match.group(1).strip() if handle_match else ''
            b = body_match.group(1).strip() if body_match else ''
            b = b.replace('\\n', '\n').replace('\\xa0', ' ').replace('\\r', '').strip()
            cleaned_descriptions[h] = {'title': t, 'body': b}

    print('Cleaned descriptions parsed:', len(cleaned_descriptions))

    df = pd.read_csv(r'E:\Project\testing_ViT\around_always_full_catalog.csv')

    dataset_path = r'E:\Project\testing_ViT\dataset'
    existing_folders = set(os.listdir(dataset_path))

    CATEGORIES = {
        'wedges': {'id': 'c1000000-0000-0000-0000-000000000001', 'name': 'Wedges & Platforms', 'slug': 'wedges'},
        'mules': {'id': 'c1000000-0000-0000-0000-000000000005', 'name': 'Mules & Slides', 'slug': 'mules-and-slides'},
        'sandals': {'id': 'c1000000-0000-0000-0000-000000000003', 'name': 'Sandals & Block Heels', 'slug': 'sandals'},
        'flats': {'id': 'c1000000-0000-0000-0000-000000000004', 'name': 'Flats & Slip-Ons', 'slug': 'flats'},
        'sneakers': {'id': 'c1000000-0000-0000-0000-000000000002', 'name': 'Sneakers & High Tops', 'slug': 'sneakers'},
    }

    def determine_category(name_lower):
        if 'wedge' in name_lower:
            return CATEGORIES['wedges']
        elif 'mule' in name_lower:
            return CATEGORIES['mules']
        elif 'sandal' in name_lower or 'heel' in name_lower:
            return CATEGORIES['sandals']
        elif 'sneaker' in name_lower:
            return CATEGORIES['sneakers']
        elif any(k in name_lower for k in ['flat', 'slider', 'slipon', 'slip-on', 'chappal', 'mojri', 'kolhapuri']):
            return CATEGORIES['flats']
        return CATEGORIES['wedges']

    footwear_keywords = [
        'sandals', 'sandal', 'sneakers', 'sneaker', 'shoes', 'shoe',
        'flats', 'flat', 'wedges', 'wedge', 'mules', 'mule',
        'heels', 'heel', 'footwear', 'chappals', 'chappal',
        'sliders', 'slider', 'slipons', 'slipon', 'slip-ons', 'slip-on',
        'mojri', 'kolhapuri', 'stilettos', 'stiletto'
    ]

    products = []
    random.seed(42)

    for i, r in df.iterrows():
        folder_raw = str(r['Image Folder'])
        folder_name = os.path.basename(folder_raw)
        if folder_name not in existing_folders:
            continue
        
        title = str(r['Title']).strip()
        title_clean = title.split('|')[0].strip()
        title_lower = title.lower()
        
        # Ensure it is footwear
        if not any(kw in title_lower or kw in folder_name.lower() for kw in footwear_keywords):
            continue
        
        folder_full_path = os.path.join(dataset_path, folder_name)
        all_imgs = sorted([img for img in os.listdir(folder_full_path) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        if len(all_imgs) == 0:
            continue
            
        handle = str(r['Product Handle']).strip() if pd.notna(r['Product Handle']) else ''
        
        desc = ''
        if handle in cleaned_descriptions and cleaned_descriptions[handle]['body']:
            desc = cleaned_descriptions[handle]['body']
        elif pd.notna(r['Description']):
            desc = str(r['Description']).strip()
        else:
            desc = 'A striking blend of designer craftsmanship and ease, made to stand out at every celebration with cushioned footbed.'

        try:
            price = float(r['Price'])
            if price <= 0 or pd.isna(price):
                price = 4990.0
        except:
            price = 4990.0
            
        category = determine_category(title_lower)
        item_id = str(r['ID'])
        prod_id = f'prod-cat-{item_id}'
        slug = handle if handle else re.sub(r'[^a-z0-9]+', '-', title_clean.lower()).strip('-')

        # Images
        images = []
        for idx, img_file in enumerate(all_imgs):
            encoded_folder = urllib.parse.quote(folder_name)
            encoded_file = urllib.parse.quote(img_file)
            img_url = f'/media/dataset/{encoded_folder}/{encoded_file}'
            images.append({
                'id': f'img-{prod_id}-{idx+1}',
                'url': img_url,
                'alt_text': f'{title_clean} view {idx+1}',
                'sort_order': idx,
                'is_primary': idx == 0
            })

        # Available sizes with inventory between 5 and 10
        sizes = [36, 37, 38, 39, 40, 41]
        variants = []
        for sz in sizes:
            stock = random.randint(5, 10)
            variants.append({
                'id': f'v-{prod_id}-{sz}',
                'sku': f'IBR-{slug[:6].upper()}-{sz}',
                'size': sz,
                'color': 'Artisan Handcrafted',
                'color_hex': '#C5A880',
                'price': price,
                'stock': stock,
                'is_active': True
            })

        # Heel modifications: 1", 2", 3"
        customizations = [
            {
                'id': f'cust-{prod_id}-1',
                'type': 'HEEL_SIZE',
                'value': '1"',
                'display_name': '1" Kitten Lift (Comfort)',
                'additional_price': 0,
                'is_available': True
            },
            {
                'id': f'cust-{prod_id}-2',
                'type': 'HEEL_SIZE',
                'value': '2"',
                'display_name': '2" Mid Ceremony Heel',
                'additional_price': 0,
                'is_available': True
            },
            {
                'id': f'cust-{prod_id}-3',
                'type': 'HEEL_SIZE',
                'value': '3"',
                'display_name': '3" Signature Elevation',
                'additional_price': 0,
                'is_available': True
            }
        ]

        product_obj = {
            'id': prod_id,
            'name': title_clean,
            'slug': slug,
            'description': desc,
            'base_price': price,
            'category': category,
            'collection': {
                'id': 'col-atelier-couture',
                'name': 'Atelier Couture Edit',
                'slug': 'atelier-couture',
                'is_active': True
            },
            'material': 'Handcrafted Brocade, Zardozi & Cushioned Footbed',
            'occasion': 'Festive & Bridal Celebrations',
            'style': category['name'],
            'is_active': True,
            'is_featured': len(products) < 12,
            'is_new_arrival': len(products) < 20,
            'images': images,
            'variants': variants,
            'customizations': customizations,
            'average_rating': round(random.uniform(4.7, 5.0), 1),
            'review_count': random.randint(6, 32),
            'created_at': '2026-10-29T10:00:00Z',
            'updated_at': '2026-10-29T10:00:00Z'
        }
        products.append(product_obj)

    print(f'Successfully built {len(products)} products!')
    out_path = r'E:\Project\Ibrat\frontend\data\catalog_100_products.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f'Saved {len(products)} products to {out_path}')

if __name__ == '__main__':
    main()
