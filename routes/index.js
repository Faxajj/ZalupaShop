const express = require('express');
const { all, get } = require('../models/db');
const { ensureAuthenticated } = require('../middleware/auth');

const router = express.Router();

router.get('/', async (req, res, next) => {
  try {
    const products = await all(`
      SELECT p.*, pi.image_path AS main_image
      FROM products p
      LEFT JOIN product_images pi ON pi.product_id = p.id
      AND pi.id = (
        SELECT id FROM product_images WHERE product_id = p.id ORDER BY id ASC LIMIT 1
      )
      ORDER BY p.id DESC
    `);

    res.render('home', {
      title: 'mvideo shop — Главная',
      products
    });
  } catch (error) {
    next(error);
  }
});

router.get('/profile', ensureAuthenticated, async (req, res, next) => {
  try {
    const user = await get('SELECT id, email, role, created_at FROM users WHERE id = ?', [req.session.user.id]);
    res.render('profile', {
      title: 'mvideo shop — Профиль',
      profile: user
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
