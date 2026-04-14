const express = require('express');
const bcrypt = require('bcrypt');
const { get, run } = require('../models/db');

const router = express.Router();

router.get('/register', (_req, res) => {
  res.render('register', { title: 'Mvideo Shop — Регистрация', error: null });
});

router.post('/register', async (req, res, next) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.render('register', {
        title: 'Mvideo Shop — Регистрация',
        error: 'Email и пароль обязательны.'
      });
    }

    const existingUser = await get('SELECT id FROM users WHERE email = ?', [email]);
    if (existingUser) {
      return res.render('register', {
        title: 'Mvideo Shop — Регистрация',
        error: 'Пользователь с таким email уже существует.'
      });
    }

    const passwordHash = await bcrypt.hash(password, 10);
    const created = await run(
      'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
      [email, passwordHash, 'user']
    );

    req.session.user = { id: created.lastID, email, role: 'user' };
    return res.redirect('/profile');
  } catch (error) {
    return next(error);
  }
});

router.get('/login', (_req, res) => {
  res.render('login', { title: 'Mvideo Shop — Вход', error: null });
});

router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;

    const user = await get('SELECT * FROM users WHERE email = ?', [email]);
    if (!user) {
      return res.render('login', {
        title: 'Mvideo Shop — Вход',
        error: 'Неверный email или пароль.'
      });
    }

    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      return res.render('login', {
        title: 'Mvideo Shop — Вход',
        error: 'Неверный email или пароль.'
      });
    }

    req.session.user = { id: user.id, email: user.email, role: user.role };
    return res.redirect('/');
  } catch (error) {
    return next(error);
  }
});

router.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});

module.exports = router;
