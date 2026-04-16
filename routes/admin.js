const express = require('express');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const { ensureAdmin } = require('../middleware/auth');
const { all, get, run } = require('../models/db');

const router = express.Router();

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, path.join(__dirname, '..', 'public', 'uploads'));
  },
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname || '').toLowerCase();
    cb(null, `${Date.now()}-${Math.round(Math.random() * 1e9)}${ext}`);
  }
});

const upload = multer({ storage });

function parseSpecs(specsText = '') {
  if (!specsText.trim()) return JSON.stringify({});
  try {
    return JSON.stringify(JSON.parse(specsText));
  } catch (_e) {
    return JSON.stringify({ Примечание: specsText });
  }
}

router.get('/admin', ensureAdmin, async (_req, res, next) => {
  try {
    const products = await all('SELECT * FROM products ORDER BY id DESC');
    return res.render('admin/dashboard', {
      title: 'mvideo shop — Админка',
      products
    });
  } catch (error) {
    return next(error);
  }
});

router.get('/admin/products/new', ensureAdmin, (_req, res) => {
  res.render('admin/product-form', {
    title: 'mvideo shop — Новый товар',
    product: null,
    images: [],
    action: '/admin/products/new',
    error: null
  });
});

router.post('/admin/products/new', ensureAdmin, upload.array('images', 3), async (req, res, next) => {
  try {
    const { name, price, description, category, article, specs } = req.body;
    if (!name || !price) {
      return res.render('admin/product-form', {
        title: 'mvideo shop — Новый товар',
        product: req.body,
        images: [],
        action: '/admin/products/new',
        error: 'Название и цена обязательны.'
      });
    }

    const created = await run(
      `INSERT INTO products (name, price, description, category, article, specs)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [name, Number(price), description, category, article, parseSpecs(specs)]
    );

    const filePaths = (req.files || []).map((f) => `/uploads/${f.filename}`);
    if (filePaths.length === 0) {
      await run('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', [
        created.lastID,
        '/uploads/placeholder-tv.svg'
      ]);
    } else {
      for (const filePath of filePaths) {
        // eslint-disable-next-line no-await-in-loop
        await run('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', [created.lastID, filePath]);
      }
    }

    return res.redirect('/admin');
  } catch (error) {
    return next(error);
  }
});

router.get('/admin/products/:id/edit', ensureAdmin, async (req, res, next) => {
  try {
    const product = await get('SELECT * FROM products WHERE id = ?', [req.params.id]);
    if (!product) {
      return res.status(404).render('error', { title: 'Ошибка', message: 'Товар не найден.' });
    }
    const images = await all('SELECT * FROM product_images WHERE product_id = ?', [req.params.id]);
    return res.render('admin/product-form', {
      title: 'mvideo shop — Редактирование товара',
      product,
      images,
      action: `/admin/products/${req.params.id}/edit`,
      error: null
    });
  } catch (error) {
    return next(error);
  }
});

router.post('/admin/products/:id/edit', ensureAdmin, upload.array('images', 3), async (req, res, next) => {
  try {
    const { name, price, description, category, article, specs } = req.body;
    await run(
      `UPDATE products
       SET name = ?, price = ?, description = ?, category = ?, article = ?, specs = ?, updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [name, Number(price), description, category, article, parseSpecs(specs), req.params.id]
    );

    const filePaths = (req.files || []).map((f) => `/uploads/${f.filename}`);
    for (const filePath of filePaths) {
      // eslint-disable-next-line no-await-in-loop
      await run('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', [req.params.id, filePath]);
    }

    return res.redirect('/admin');
  } catch (error) {
    return next(error);
  }
});

router.post('/admin/products/:id/delete', ensureAdmin, async (req, res, next) => {
  try {
    const images = await all('SELECT image_path FROM product_images WHERE product_id = ?', [req.params.id]);
    for (const img of images) {
      if (!img.image_path.includes('placeholder-tv.svg')) {
        const filePath = path.join(__dirname, '..', 'public', img.image_path.replace('/uploads/', 'uploads/'));
        if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
      }
    }
    await run('DELETE FROM products WHERE id = ?', [req.params.id]);
    return res.redirect('/admin');
  } catch (error) {
    return next(error);
  }
});

router.post('/admin/products/:productId/images/:imageId/delete', ensureAdmin, async (req, res, next) => {
  try {
    const image = await get('SELECT * FROM product_images WHERE id = ? AND product_id = ?', [
      req.params.imageId,
      req.params.productId
    ]);
    if (image) {
      if (!image.image_path.includes('placeholder-tv.svg')) {
        const filePath = path.join(__dirname, '..', 'public', image.image_path.replace('/uploads/', 'uploads/'));
        if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
      }
      await run('DELETE FROM product_images WHERE id = ?', [req.params.imageId]);
    }

    const remaining = await get('SELECT COUNT(*) as total FROM product_images WHERE product_id = ?', [req.params.productId]);
    if (remaining.total === 0) {
      await run('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', [
        req.params.productId,
        '/uploads/placeholder-tv.svg'
      ]);
    }

    return res.redirect(`/admin/products/${req.params.productId}/edit`);
  } catch (error) {
    return next(error);
  }
});

router.get('/admin/users', ensureAdmin, async (_req, res, next) => {
  try {
    const users = await all('SELECT id, email, role, created_at FROM users ORDER BY id DESC');
    return res.render('admin/users', {
      title: 'mvideo shop — Пользователи',
      users
    });
  } catch (error) {
    return next(error);
  }
});

router.post('/admin/users/:id/role', ensureAdmin, async (req, res, next) => {
  try {
    const { role } = req.body;
    if (!['admin', 'user'].includes(role)) return res.redirect('/admin/users');
    await run('UPDATE users SET role = ? WHERE id = ?', [role, req.params.id]);
    return res.redirect('/admin/users');
  } catch (error) {
    return next(error);
  }
});

router.post('/admin/users/:id/delete', ensureAdmin, async (req, res, next) => {
  try {
    if (Number(req.params.id) === req.session.user.id) {
      return res.status(400).render('error', {
        title: 'Ошибка',
        message: 'Нельзя удалить текущего администратора, под которым вы вошли.'
      });
    }
    await run('DELETE FROM users WHERE id = ?', [req.params.id]);
    return res.redirect('/admin/users');
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
