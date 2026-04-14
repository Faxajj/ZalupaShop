const path = require('path');
const express = require('express');
const session = require('express-session');
const dotenv = require('dotenv');
const { initDb } = require('./models/db');
const { attachUser } = require('./middleware/auth');

const indexRoutes = require('./routes/index');
const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const adminRoutes = require('./routes/admin');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use('/uploads', express.static(path.join(__dirname, 'public', 'uploads')));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(
  session({
    secret: process.env.SESSION_SECRET || 'dev_secret_please_change',
    resave: false,
    saveUninitialized: false,
    cookie: {
      maxAge: 1000 * 60 * 60 * 24
    }
  })
);

app.use(attachUser);

app.use((req, res, next) => {
  res.locals.currentUser = req.session.user || null;
  next();
});

app.use(indexRoutes);
app.use(authRoutes);
app.use(productRoutes);
app.use(adminRoutes);

app.use((req, res) => {
  res.status(404).render('error', {
    title: '404',
    message: 'Страница не найдена'
  });
});

app.use((err, req, res, _next) => {
  // eslint-disable-next-line no-console
  console.error('Unhandled error:', err);
  res.status(500).render('error', {
    title: '500',
    message: 'Внутренняя ошибка сервера'
  });
});

(async () => {
  try {
    await initDb();
    app.listen(PORT, () => {
      // eslint-disable-next-line no-console
      console.log(`Mvideo Shop started: http://localhost:${PORT}`);
    });
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Failed to initialize database:', error);
    process.exit(1);
  }
})();
