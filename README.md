# Mvideo Shop 🛒 — Paraguay 🇵🇾

Tienda online de tecnología para Paraguay, construida con **Flask + SQLite + Tailwind**.
Interfaz bilingüe **Español / Guaraní**, precios en **PYG / USD**, panel de administración, carga de fotos, registro de usuarios.

## ✨ Qué incluye

- 🌐 **Bilingüe:** Español + Guaraní (se cambia todo: UI, productos, descripciones, admin)
- 💰 **Dos monedas:** PYG / USD — conversión automática por `USD_RATE = 7300`
- 📦 **Catálogo:** 18 productos demo (Celulares, Informática, TV y Audio, Gaming, Perfumería, Hogar)
- 🖼️ **Páginas de producto** con galería de fotos, tabla de características, descripción
- 👤 **Registro / login** (email + contraseña), roles user/admin
- 🛒 **Carrito** en localStorage (funciona sin login, checkout requiere login)
- 📜 **Perfil** con historial de pedidos
- 🔐 **Admin panel** (`/admin`) — solo rol `admin`:
  - CRUD de productos (campos ES + GN separados)
  - Upload de fotos (local o URL)
  - Características flexibles (Marca, Modelo, Color...)
  - Gestión de usuarios y roles
  - Dashboard con estadísticas
- 📱 **Responsive** (móvil / tablet / desktop)

## 🛠️ Stack

- **Backend:** Flask 3 + Flask-SQLAlchemy + Flask-Login
- **BD:** SQLite (archivo `mvideo.db`)
- **Frontend:** Jinja2 + Tailwind (CDN) + vanilla JS
- **Fotos:** upload multipart a `static/uploads/` o URLs externas

## 📁 Estructura

```
mvideo-shop/
├── app.py                    # Flask app: modelos, rutas, auth, admin
├── i18n.py                   # Traducciones ES / GN
├── init_db.py                # Crea BD + admin GlazAdmin + 18 productos
├── requirements.txt
├── mvideo.db                 # (se crea con init_db.py)
├── static/
│   ├── css/style.css
│   ├── js/cart.js            # carrito en localStorage
│   └── uploads/              # fotos subidas
└── templates/
    ├── base.html             # layout común + selector ES/GN y PYG/USD
    ├── index.html            # catálogo
    ├── product.html          # página de producto (galería + specs)
    ├── login.html / register.html / profile.html / error.html
    └── admin/
        ├── dashboard.html
        ├── products.html
        ├── product_form.html # formulario con campos ES + GN
        └── users.html
```

## 🚀 Inicio rápido

```bash
cd mvideo-shop

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python init_db.py               # crea BD + admin + 18 productos
python app.py                   # → http://localhost:5000
```

## 🔐 Credenciales por defecto

| Rol | Usuario | Contraseña |
|---|---|---|
| **Admin** | `GlazAdmin` | `GlazAdmin123!` |
| User | `user` | `user123` |

⚠️ **Cambia la contraseña del admin** en `init_db.py` (constante `ADMIN_PASSWORD`) antes de producción.

## 🌐 Cómo funciona la bilingüismo

### UI (menús, botones, errores)
Todo en `i18n.py` como diccionario `TRANSLATIONS['es']` y `TRANSLATIONS['gn']`.
En los templates se usa `{{ t('clave') }}`.

Para añadir un string nuevo:
```python
# i18n.py
'es': { ..., 'mi_clave': 'Hola' },
'gn': { ..., 'mi_clave': 'Mba'éichapa' },
```
```html
<!-- en template -->
<span>{{ t('mi_clave') }}</span>
```

### Productos
Cada producto tiene `name` (ES) + `name_gn` (GN) y `description` (ES) + `description_gn` (GN).
Los helpers `loc_name(p)` y `loc_desc(p)` devuelven la versión correcta según el idioma actual.

### Selector
El idioma y la moneda se guardan en `session`. Enlaces en el top bar:
- `/set-lang/es` · `/set-lang/gn`
- `/set-currency/PYG` · `/set-currency/USD`

## 💰 Precios PYG ↔ USD

- Todos los precios se guardan en **guaraníes (PYG)** en la BD
- Conversión a USD se hace al renderizar, usando `USD_RATE = 7300` en `app.py`
- Helpers: `fmt_primary(pyg)` (moneda activa) y `fmt_secondary(pyg)` (la otra)
- Cambiar el tipo de cambio: edita la línea `USD_RATE = 7300.0` en `app.py`

## 📊 Esquema de BD

```
users            → id, username, email, password_hash, role, created_at
products         → id, sku, name, name_gn, description, description_gn,
                   price (PYG), old_price, category, stock
product_images   → product_id, filename (local o http-URL), sort_order
product_specs    → product_id, key, value (características flexibles)
orders           → id, user_id, total (PYG), status, created_at
order_items      → order_id, product_id, name, price, qty
```

## 🔑 Rutas principales

### Públicas
- `GET /` — catálogo (`?q=` búsqueda, `?cat=` categoría)
- `GET /product/<id>` — página de producto
- `GET/POST /register` · `/login` · `/logout`
- `GET /profile` — perfil + historial (requiere login)
- `POST /checkout` — realizar pedido (JSON desde `cart.js`)
- `GET /set-lang/<es|gn>` · `/set-currency/<PYG|USD>`

### Admin (requiere `role='admin'`)
- `GET /admin` — dashboard
- `GET /admin/products` — lista
- `GET/POST /admin/products/new` · `/<id>/edit`
- `POST /admin/products/<id>/delete`
- `POST /admin/image/<id>/delete`
- `GET /admin/users` · `POST /admin/users/<id>/toggle`

## 🧪 Smoke test (ya pasado)

```
/                                 → 200
/product/1 , /product/15          → 200
/login , /register                → 200
/set-lang/gn → /                  → muestra "Pumbyry" ✓
/set-currency/USD → /product/1    → muestra "US$" ✓
login GlazAdmin                   → 302 → /admin
/admin                            → 200
/admin/products                   → 200
/admin/users                      → 200
/admin/products/new               → 200
/admin/products/1/edit            → 200
register + checkout + /profile    → 200 (pedido creado)
```

## ✏️ Cómo añadir un producto

**Opción A: admin panel (recomendado)**
1. Login como `GlazAdmin`
2. `/admin/products` → "+ Añadir producto"
3. Rellena SKU, nombre ES, nombre GN, descripción ES/GN, precio en PYG
4. Añade características (Marca, Modelo, Color...)
5. Sube fotos o pega URLs
6. Guardar

**Opción B: `init_db.py`**
Añade un bloque en el array `DEMO` y ejecuta `python init_db.py` (⚠️ esto recrea la BD).

## 🌐 Despliegue en VPS (gunicorn + nginx)

```bash
# En el servidor
git clone ... && cd mvideo-shop
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt gunicorn
python init_db.py

# systemd: /etc/systemd/system/mvideo.service
[Unit]
Description=Mvideo Shop
After=network.target
[Service]
User=www-data
WorkingDirectory=/var/www/mvideo-shop
Environment="SECRET_KEY=your-production-secret-xxxxxxxxxx"
ExecStart=/var/www/mvideo-shop/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always
[Install]
WantedBy=multi-user.target

sudo systemctl enable --now mvideo

# nginx: /etc/nginx/sites-available/mvideo
server {
    listen 80;
    server_name tutienda.com.py;
    client_max_body_size 20M;
    location /static/ {
        alias /var/www/mvideo-shop/static/;
        expires 7d;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

sudo ln -s /etc/nginx/sites-available/mvideo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d tutienda.com.py
```

## 🛣️ Futuras mejoras

- Integración real de pago (Pagopar, Bancard, MercadoPago)
- Confirmación por email + recuperar contraseña
- Reseñas/ratings en productos
- Búsqueda full-text (PostgreSQL + tsvector)
- Migración a PostgreSQL (una línea en `app.py`)
