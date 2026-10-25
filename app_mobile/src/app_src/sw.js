/* 離線快取。BUILD 由 build.py 每次打包時換成新的編號，換了編號就會更新快取。 */
const BUILD = '__BUILD__';
const CACHE = 'casecard-' + BUILD + '-platform-__PLATFORM__';
const PRECACHE = __PRECACHE__;
// 這些每次都先問網路（有網路就拿最新，沒網路才用快取），新案例才看得到
const FRESH = /\/(cases\/[^/]+\.(json|md)|version\.json)$|\/platform\//;
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
