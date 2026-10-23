/* 離線快取。BUILD 由 build.py 每次打包時換成新的編號，換了編號就會更新快取。 */
const BUILD = '82bc174f1e';
const CACHE = 'casecard-' + BUILD;
const PRECACHE = ["./", "app.css", "cases/index.json", "cases/shilin_110_laosu_72.json", "design/standard.css", "fonts/BarlowCondensed-Bold.woff2", "fonts/BarlowCondensed-ExtraBold.woff2", "fonts/FONTS_LICENSE.md", "fonts/OFL.txt", "fonts/fonts.json", "fonts/sans400a.woff2", "fonts/sans400b.woff2", "fonts/sans500a.woff2", "fonts/sans500b.woff2", "fonts/sans700a.woff2", "fonts/sans700b.woff2", "fonts/sans800a.woff2", "fonts/sans800b.woff2", "fonts/sans900a.woff2", "fonts/sans900b.woff2", "fonts/serif500a.woff2", "fonts/serif500b.woff2", "fonts/serif700a.woff2", "fonts/serif700b.woff2", "fonts/serif900a.woff2", "fonts/serif900b.woff2", "hero_library/overwork_night_desk.svg", "hero_library/overwork_night_desk_photo.card.jpg", "hero_library/overwork_night_desk_photo.provenance.json", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512-maskable.png", "icons/icon-512.png", "index.html", "js/app.js", "js/engine.js", "js/render.js", "manifest.webmanifest", "skins/skin_original.json", "skins/skin_style1.json", "skins/skin_style1_print.json", "skins/skin_style2.json", "skins/skin_style3.json", "skins/skin_style4.json", "skins/skin_style5.json", "skins/skin_style6.json", "skins/skin_style7.json"];
// 這些每次都先問網路（有網路就拿最新，沒網路才用快取），新案例才看得到
const FRESH = /\/(cases\/[^/]+\.json|version\.json)$/;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE.map(p => new Request(p, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('casecard-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (FRESH.test(url.pathname)) {
    e.respondWith(fetch(req, { cache: 'no-store' }).then(r => {
      if (r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); }
      return r;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || Response.error())));
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req).then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); }
    return r;
  })));
});
