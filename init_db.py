"""
init_db.py — crea BD, admin GlazAdmin y productos demo (ES/GN, PYG).
Ejecutar: python init_db.py
"""
from app import app, db, User, Product, ProductImage, ProductSpec

ADMIN_USERNAME = 'GlazAdmin'
ADMIN_EMAIL = 'admin@mvideoshop.py'
ADMIN_PASSWORD = 'GlazAdmin123!'  # ⚠️ cámbiala en producción

# Catálogo Paraguay — precios en guaraníes (PYG)
DEMO = [
    # ========== CELULARES ==========
    {
        'sku': 'MV-001',
        'name': 'Celular Apple iPhone 15 128GB',
        'name_gn': 'Pumbyry Apple iPhone 15 128GB',
        'category': 'Celulares',
        'price': 4445570, 'old_price': 5100000,
        'description': 'Apple iPhone 15 con pantalla OLED Super Retina XDR de 6.1", chip A16 Bionic, cámara principal de 48 MP y USB-C.',
        'description_gn': 'Apple iPhone 15 tesa OLED Super Retina XDR 6.1", chip A16 Bionic, ta\'angaryru 48 MP ha USB-C.',
        'specs': [
            ('Marca', 'Apple'), ('Modelo', 'iPhone 15'),
            ('Pantalla', '6.1" OLED'), ('Memoria', '128 GB'),
            ('SO', 'iOS 17'), ('Color', 'Negro'),
        ],
        'images': [
            'https://loremflickr.com/800/800/iphone?lock=101',
            'https://loremflickr.com/800/800/iphone,screen?lock=102',
        ],
    },
    {
        'sku': 'MV-002',
        'name': 'Celular Samsung Galaxy S25 Ultra 256GB',
        'name_gn': 'Pumbyry Samsung Galaxy S25 Ultra 256GB',
        'category': 'Celulares',
        'price': 8395000,
        'description': 'Flagship Samsung Galaxy S25 Ultra con S Pen, cámara de 200 MP y pantalla Dynamic AMOLED 2X de 6.8" 120 Hz.',
        'description_gn': 'Samsung Galaxy S25 Ultra S Pen reheve, ta\'angaryru 200 MP ha tesa 6.8" 120 Hz.',
        'specs': [
            ('Marca', 'Samsung'), ('Modelo', 'Galaxy S25 Ultra'),
            ('Memoria', '256 GB'), ('Cámara', '200 MP'),
            ('Pantalla', '6.8" AMOLED 120Hz'),
        ],
        'images': [
            'https://loremflickr.com/800/800/samsung,galaxy?lock=201',
            'https://loremflickr.com/800/800/samsung,ultra?lock=202',
        ],
    },
    {
        'sku': 'MV-003',
        'name': 'Celular Honor X7d 256GB 4G 6.77"',
        'name_gn': 'Pumbyry Honor X7d 256GB 4G 6.77"',
        'category': 'Celulares',
        'price': 1292100,
        'description': 'Honor X7d con batería de 6500 mAh, cámara 108 MP y pantalla de 6.77".',
        'description_gn': 'Honor X7d batería 6500 mAh, ta\'angaryru 108 MP ha tesa 6.77".',
        'specs': [
            ('Marca', 'Honor'), ('Modelo', 'X7d'),
            ('Memoria', '256 GB'), ('Cámara', '108 MP'),
            ('Batería', '6500 mAh'),
        ],
        'images': ['https://loremflickr.com/800/800/honor,phone?lock=301'],
    },
    {
        'sku': 'MV-004',
        'name': 'Celular Xiaomi Poco X7 Pro 512GB 5G',
        'name_gn': 'Pumbyry Xiaomi Poco X7 Pro 512GB 5G',
        'category': 'Celulares',
        'price': 2518500, 'old_price': 2850000,
        'description': 'Xiaomi Poco X7 Pro con 512 GB, chip dual, versión global y soporte 5G.',
        'description_gn': 'Xiaomi Poco X7 Pro 512 GB, dual chip, versión global ha 5G.',
        'specs': [
            ('Marca', 'Xiaomi'), ('Modelo', 'Poco X7 Pro'),
            ('Memoria', '512 GB'), ('Red', '5G'),
        ],
        'images': ['https://loremflickr.com/800/800/xiaomi,phone?lock=401'],
    },

    # ========== INFORMÁTICA ==========
    {
        'sku': 'MV-005',
        'name': 'Notebook Apple MacBook Air 13" M3 8/256GB',
        'name_gn': 'Kuatiañe\'ẽrenda Apple MacBook Air 13" M3',
        'category': 'Informática',
        'price': 8760000,
        'description': 'Apple MacBook Air 13" con chip M3, 8 GB de memoria unificada, 256 GB SSD y hasta 18 horas de autonomía.',
        'description_gn': 'Apple MacBook Air 13" chip M3 reheve, 8 GB memoria, 256 GB SSD ha 18 aravo peve.',
        'specs': [
            ('Marca', 'Apple'), ('Procesador', 'Apple M3'),
            ('RAM', '8 GB'), ('SSD', '256 GB'),
            ('Pantalla', '13" Retina'), ('SO', 'macOS'),
        ],
        'images': [
            'https://loremflickr.com/800/800/macbook?lock=501',
            'https://loremflickr.com/800/800/apple,laptop?lock=502',
        ],
    },
    {
        'sku': 'MV-006',
        'name': 'Notebook Lenovo IdeaPad 5 15" i5 16GB 512GB',
        'name_gn': 'Kuatiañe\'ẽrenda Lenovo IdeaPad 5',
        'category': 'Informática',
        'price': 4380000, 'old_price': 5100000,
        'description': 'Lenovo IdeaPad 5 con Intel Core i5, 16 GB RAM, 512 GB SSD y Windows 11.',
        'description_gn': 'Lenovo IdeaPad 5 Intel Core i5, 16 GB RAM, 512 GB SSD ha Windows 11.',
        'specs': [
            ('Marca', 'Lenovo'), ('Procesador', 'Intel Core i5'),
            ('RAM', '16 GB'), ('SSD', '512 GB'),
            ('Pantalla', '15.6" FHD IPS'),
        ],
        'images': ['https://loremflickr.com/800/800/laptop,notebook?lock=601'],
    },
    {
        'sku': 'MV-007',
        'name': 'Procesador Intel Core i5-12400F 2.5GHz',
        'name_gn': 'Procesador Intel Core i5-12400F',
        'category': 'Informática',
        'price': 1006700,
        'description': 'Intel Core i5-12400F, socket LGA 1700, 18 MB de caché, 6 núcleos / 12 hilos.',
        'description_gn': 'Intel Core i5-12400F LGA 1700, 18 MB caché, 6 núcleo.',
        'specs': [
            ('Marca', 'Intel'), ('Modelo', 'i5-12400F'),
            ('Frecuencia', '2.5 GHz'), ('Socket', 'LGA 1700'),
            ('Núcleos', '6'),
        ],
        'images': ['https://loremflickr.com/800/800/processor,intel?lock=701'],
    },

    # ========== TV / AUDIO ==========
    {
        'sku': 'MV-008',
        'name': 'Smart TV LG OLED C3 55" 4K',
        'name_gn': 'Ta\'angambyry LG OLED C3 55" 4K',
        'category': 'TV y Audio',
        'price': 10220000,
        'description': 'LG OLED evo 55" 4K UHD con procesador α9 Gen6, webOS 23, Dolby Vision y Dolby Atmos.',
        'description_gn': 'LG OLED 55" 4K UHD chip α9 Gen6, webOS 23, Dolby Vision ha Dolby Atmos.',
        'specs': [
            ('Marca', 'LG'), ('Pantalla', '55"'),
            ('Resolución', '4K UHD'), ('Tipo', 'OLED evo'),
            ('Smart TV', 'webOS 23'),
        ],
        'images': ['https://loremflickr.com/800/800/tv,oled?lock=801'],
    },
    {
        'sku': 'MV-009',
        'name': 'Smart TV Samsung 55" QLED 4K',
        'name_gn': 'Ta\'angambyry Samsung 55" QLED',
        'category': 'TV y Audio',
        'price': 6570000, 'old_price': 7500000,
        'description': 'Samsung 55" QLED 4K Smart TV con Neo Quantum Processor 4K y panel de 120 Hz.',
        'description_gn': 'Samsung 55" QLED 4K panel 120 Hz reheve.',
        'specs': [
            ('Marca', 'Samsung'), ('Pantalla', '55"'),
            ('Tipo', 'QLED'), ('Frecuencia', '120 Hz'),
        ],
        'images': ['https://loremflickr.com/800/800/samsung,tv?lock=901'],
    },
    {
        'sku': 'MV-010',
        'name': 'Auriculares Apple AirPods Pro 2 USB-C',
        'name_gn': 'Apysakaha Apple AirPods Pro 2',
        'category': 'TV y Audio',
        'price': 1606000,
        'description': 'AirPods Pro 2 con cancelación activa de ruido, audio espacial y estuche MagSafe USB-C.',
        'description_gn': 'AirPods Pro 2 cancelación activa, audio espacial ha estuche USB-C.',
        'specs': [
            ('Marca', 'Apple'), ('Tipo', 'TWS in-ear'),
            ('ANC', 'Sí'), ('Autonomía', 'hasta 6 h (30 h con estuche)'),
        ],
        'images': ['https://loremflickr.com/800/800/airpods?lock=1001'],
    },
    {
        'sku': 'MV-011',
        'name': 'Auriculares Sony WH-1000XM5',
        'name_gn': 'Apysakaha Sony WH-1000XM5',
        'category': 'TV y Audio',
        'price': 2555000,
        'description': 'Sony WH-1000XM5 — auriculares over-ear flagship con la mejor cancelación de ruido.',
        'description_gn': 'Sony WH-1000XM5 over-ear, cancelación iporãvéva.',
        'specs': [
            ('Marca', 'Sony'), ('Tipo', 'Over-ear'),
            ('ANC', 'Sí, adaptativo'), ('Autonomía', 'hasta 30 h'),
        ],
        'images': ['https://loremflickr.com/800/800/headphones,sony?lock=1101'],
    },

    # ========== GAMING ==========
    {
        'sku': 'MV-012',
        'name': 'Consola Sony PlayStation 5 Slim 1TB',
        'name_gn': 'Ñembosaraiha Sony PlayStation 5 Slim',
        'category': 'Gaming',
        'price': 4015000,
        'description': 'PS5 Slim con lector Blu-ray, 1 TB SSD y mando DualSense.',
        'description_gn': 'PS5 Slim Blu-ray, 1 TB SSD ha mando DualSense.',
        'specs': [
            ('Marca', 'Sony'), ('Modelo', 'PS5 Slim'),
            ('Almacenamiento', '1 TB SSD'),
        ],
        'images': ['https://loremflickr.com/800/800/playstation?lock=1201'],
    },
    {
        'sku': 'MV-013',
        'name': 'Consola Nintendo Switch OLED',
        'name_gn': 'Ñembosaraiha Nintendo Switch OLED',
        'category': 'Gaming',
        'price': 2409000,
        'description': 'Nintendo Switch OLED con pantalla de 7" OLED y audio mejorado.',
        'description_gn': 'Nintendo Switch tesa 7" OLED.',
        'specs': [
            ('Marca', 'Nintendo'), ('Pantalla', '7" OLED'),
            ('Memoria', '64 GB'),
        ],
        'images': ['https://loremflickr.com/800/800/nintendo,switch?lock=1301'],
    },

    # ========== PERFUMERÍA ==========
    {
        'sku': 'MV-014',
        'name': 'Perfume Lattafa Eclaire Banoffi 100ML',
        'name_gn': 'Hyakuãva Lattafa Eclaire Banoffi',
        'category': 'Perfumería',
        'price': 182500,
        'description': 'Eau de Parfum unisex con notas orientales dulces, frasco de 100 ML.',
        'description_gn': 'Eau de Parfum unisex, hyakuã oriental he\'ẽ, 100 ML.',
        'specs': [
            ('Marca', 'Lattafa'), ('Volumen', '100 ML'),
            ('Tipo', 'Eau de Parfum'), ('Género', 'Unisex'),
        ],
        'images': ['https://loremflickr.com/800/800/perfume,bottle?lock=1401'],
    },
    {
        'sku': 'MV-015',
        'name': 'Perfume Paco Rabanne 1 Million 100ML',
        'name_gn': 'Hyakuãva Paco Rabanne 1 Million',
        'category': 'Perfumería',
        'price': 876000, 'old_price': 1020000,
        'description': 'Paco Rabanne 1 Million Eau de Toilette masculino con fragancia oriental intensa.',
        'description_gn': 'Paco Rabanne 1 Million kuimba\'épe g̃uarã, hyakuã mbareteva.',
        'specs': [
            ('Marca', 'Paco Rabanne'), ('Volumen', '100 ML'),
            ('Tipo', 'Eau de Toilette'), ('Género', 'Masculino'),
        ],
        'images': ['https://loremflickr.com/800/800/cologne,luxury?lock=1501'],
    },
    {
        'sku': 'MV-016',
        'name': 'Body Splash Armaf Frozen Blossom 250ML',
        'name_gn': 'Body Splash Armaf Frozen Blossom',
        'category': 'Perfumería',
        'price': 73000,
        'description': 'Body splash refrescante con notas florales, 250 ML.',
        'description_gn': 'Body splash ro\'ysã, hyakuã yvoty, 250 ML.',
        'specs': [
            ('Marca', 'Armaf'), ('Volumen', '250 ML'),
            ('Tipo', 'Body Splash'),
        ],
        'images': ['https://loremflickr.com/800/800/perfume,fragrance?lock=1601'],
    },

    # ========== HOGAR ==========
    {
        'sku': 'MV-017',
        'name': 'Cafetera DeLonghi Magnifica S Automática',
        'name_gn': 'Kafembojyha DeLonghi Magnifica S',
        'category': 'Hogar',
        'price': 3285000, 'old_price': 3900000,
        'description': 'Cafetera automática DeLonghi Magnifica S ECAM 22.110.B con capuchinador y depósito de 1.8 L.',
        'description_gn': 'Kafembojyha automática DeLonghi Magnifica S capuchinador reheve.',
        'specs': [
            ('Marca', 'DeLonghi'), ('Modelo', 'ECAM 22.110.B'),
            ('Tipo', 'Automática'), ('Depósito', '1.8 L'),
        ],
        'images': ['https://loremflickr.com/800/800/coffee,espresso?lock=1701'],
    },
    {
        'sku': 'MV-018',
        'name': 'Robot Aspirador Xiaomi S20+',
        'name_gn': 'Mopotĩha robot Xiaomi S20+',
        'category': 'Hogar',
        'price': 2044000,
        'description': 'Xiaomi Robot Vacuum S20+ con navegación láser LDS, 4000 Pa de succión y modo de mopa húmeda.',
        'description_gn': 'Xiaomi Robot Vacuum S20+ láser LDS, 4000 Pa ha mopa akỹva.',
        'specs': [
            ('Marca', 'Xiaomi'), ('Navegación', 'LDS láser'),
            ('Succión', '4000 Pa'), ('Trapeado', 'Sí'),
        ],
        'images': ['https://loremflickr.com/800/800/robot,vacuum?lock=1801'],
    },
]


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, role='admin')
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

        demo_user = User(username='user', email='user@demo.py', role='user')
        demo_user.set_password('user123')
        db.session.add(demo_user)

        for p in DEMO:
            prod = Product(
                sku=p['sku'],
                name=p['name'], name_gn=p.get('name_gn'),
                description=p['description'], description_gn=p.get('description_gn', ''),
                price=p['price'], old_price=p.get('old_price'),
                category=p['category'], stock=50,
            )
            db.session.add(prod)
            db.session.flush()
            for i, url in enumerate(p['images']):
                db.session.add(ProductImage(
                    product_id=prod.id, filename=url, sort_order=i
                ))
            for k, v in p['specs']:
                db.session.add(ProductSpec(product_id=prod.id, key=k, value=v))

        db.session.commit()
        print("=" * 60)
        print("✓ Base de datos creada")
        print(f"✓ Admin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print(f"✓ Usuario demo: user / user123")
        print(f"✓ Productos: {len(DEMO)}")
        print("=" * 60)


if __name__ == '__main__':
    run()
