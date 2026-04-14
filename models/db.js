const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const DB_PATH = path.join(__dirname, '..', 'shop.db');
const db = new sqlite3.Database(DB_PATH);

function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function initDb() {
  await run('PRAGMA foreign_keys = ON');

  await run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      price REAL NOT NULL,
      description TEXT,
      category TEXT,
      article TEXT,
      specs TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS product_images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      image_path TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
  `);

  const adminEmail = 'admin@mvideo.com';
  const existingAdmin = await get('SELECT id FROM users WHERE email = ?', [adminEmail]);

  if (!existingAdmin) {
    const passwordHash = await bcrypt.hash('admin123', 10);
    await run(
      'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
      [adminEmail, passwordHash, 'admin']
    );
  }

  const productsCount = await get('SELECT COUNT(*) as total FROM products');
  if (!productsCount || productsCount.total === 0) {
    const sampleSpecs = JSON.stringify({ Бренд: 'Sony', Модель: 'X100', Гарантия: '12 мес' });
    const p = await run(
      'INSERT INTO products (name, price, description, category, article, specs) VALUES (?, ?, ?, ?, ?, ?)',
      [
        'Телевизор Sony 55" 4K',
        59990,
        'Качественный 4K телевизор с HDR и Smart TV.',
        'Телевизоры',
        'TV-SONY-X100',
        sampleSpecs
      ]
    );
    await run('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', [
      p.lastID,
      '/uploads/placeholder-tv.svg'
    ]);
  }
}

module.exports = {
  db,
  run,
  get,
  all,
  initDb
};
