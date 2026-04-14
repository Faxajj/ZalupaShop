function attachUser(req, _res, next) {
  req.user = req.session.user || null;
  next();
}

function ensureAuthenticated(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  return next();
}

function ensureAdmin(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  if (req.session.user.role !== 'admin') {
    return res.status(403).render('error', {
      title: 'Доступ запрещён',
      message: 'Эта страница доступна только администратору.'
    });
  }
  return next();
}

module.exports = {
  attachUser,
  ensureAuthenticated,
  ensureAdmin
};
