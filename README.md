# Mvideo Shop

Полностью рабочий интернет-магазин на стеке **Node.js + Express + SQLite + EJS + Multer**.

> ⚠️ Важно: не открывайте проект как `file://...` и не ориентируйтесь на предпросмотр `README.md` в браузере/IDE.
> Приложение работает только через запуск Node.js сервера (`npm start`) и открытие `http://localhost:3000`.

## Возможности
- Каталог товаров на главной странице.
- Страница товара `/product/:id` с галереей, характеристиками (JSON specs) и кнопкой-заглушкой «Добавить в корзину».
- Регистрация и вход по email/паролю (bcrypt).
- Сессии на `express-session`.
- Роли `user` и `admin`.
- Профиль пользователя `/profile`.
- Админка `/admin`:
  - CRUD товаров.
  - Загрузка нескольких фото (до 3) в `public/uploads`.
  - Удаление фото товара.
  - Управление пользователями `/admin/users` (просмотр, удаление, смена роли).

## Структура проекта

```text

├── app.js
├── package.json
├── .env.example
├── shop.db (создаётся автоматически)
├── models/
│   └── db.js
├── middleware/
│   └── auth.js
├── routes/
│   ├── index.js
│   ├── auth.js
│   ├── products.js
│   └── admin.js
├── public/
│   ├── style.css
│   └── uploads/
│       ├── .gitkeep
│       └── placeholder-tv.svg
└── views/
    ├── partials/
    │   ├── header.ejs
    │   └── footer.ejs
    ├── admin/
    │   ├── dashboard.ejs
    │   ├── product-form.ejs
    │   └── users.ejs
    ├── home.ejs
    ├── product.ejs
    ├── register.ejs
    ├── login.ejs
    ├── profile.ejs
    └── error.ejs
```

## Быстрый старт локально

1. Клонируйте репозиторий:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd mvideo-shop
   ```

2. Установите зависимости:
   ```bash
   npm install
   ```

3. Создайте `.env` из примера:
   ```bash
   cp .env.example .env
   ```

4. Запустите проект:
   ```bash
   npm start
   ```

5. Откройте сайт:
   - http://localhost:3000

> База `shop.db` инициализируется автоматически при первом запуске.

## Тестовый админ

Создаётся автоматически при инициализации БД:
- Email: `admin@mvideo.com`
- Пароль: `admin123`

## Публикация в GitHub

```bash
git init
git add .
git commit -m "Initial Mvideo Shop implementation"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Примечания
- Если изображения не загружаются, проверьте права на папку `public/uploads`.
- Для production обязательно задайте сложный `SESSION_SECRET` в `.env`.
