const express = require('express');
const { get, all } = require('../models/db');

const router = express.Router();

router.get('/product/:id', async (req, res, next) => {
  try {
    const product = await get('SELECT * FROM products WHERE id = ?', [req.params.id]);
    if (!product) {
      return res.status(404).render('error', {
        title: 'Товар не найден',
        message: 'Товар с таким id не существует.'
      });
    }

    const images = await all('SELECT * FROM product_images WHERE product_id = ? ORDER BY id ASC', [product.id]);
    let specs = {};
    if (product.specs) {
      try {
        specs = JSON.parse(product.specs);
      } catch (_e) {
        specs = {};
      }
    }

    return res.render('product', {
      title: `mvideo shop — ${product.name}`,
      product,
      images,
      specs
    });
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
