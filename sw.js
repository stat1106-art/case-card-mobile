/* 離線快取。BUILD 由 build.py 每次打包時換成新的編號，換了編號就會更新快取。 */
const BUILD = 'c94c9b6b3e';
const CACHE = 'casecard-' + BUILD + '-platform-0.1.6';
const PRECACHE = ["./", "app.css", "cases/cydv_115_laojian_4.json", "cases/index.json", "cases/shilin_110_laosu_72.json", "cases/tydv_115_laosu_114.json", "design/standard.css", "fonts/BarlowCondensed-Bold.woff2", "fonts/BarlowCondensed-ExtraBold.woff2", "fonts/FONTS_LICENSE.md", "fonts/OFL.txt", "fonts/fonts.json", "fonts/sans400a.woff2", "fonts/sans400b.woff2", "fonts/sans500a.woff2", "fonts/sans500b.woff2", "fonts/sans700a.woff2", "fonts/sans700b.woff2", "fonts/sans800a.woff2", "fonts/sans800b.woff2", "fonts/sans900a.woff2", "fonts/sans900b.woff2", "fonts/serif500a.woff2", "fonts/serif500b.woff2", "fonts/serif700a.woff2", "fonts/serif700b.woff2", "fonts/serif900a.woff2", "fonts/serif900b.woff2", "hero_library/hero_chemical_a.provenance.json", "hero_library/hero_collapse_a.provenance.json", "hero_library/hero_commute_a.provenance.json", "hero_library/hero_construction_a.provenance.json", "hero_library/hero_disease_a.provenance.json", "hero_library/hero_electric_a.provenance.json", "hero_library/hero_fall_a.provenance.json", "hero_library/hero_healthcare_a.provenance.json", "hero_library/hero_heat_a.provenance.json", "hero_library/hero_machine_a.provenance.json", "hero_library/hero_neutral_a.provenance.json", "hero_library/hero_overwork_a.provenance.json", "hero_library/hero_stress_a.provenance.json", "hero_library/hero_traffic_a.provenance.json", "hero_library/overwork_night_desk.svg", "hero_library/overwork_night_desk_photo.card.jpg", "hero_library/overwork_night_desk_photo.provenance.json", "hero_library/type_chemical.card.jpg", "hero_library/type_collapse.card.jpg", "hero_library/type_commute.card.jpg", "hero_library/type_construction.card.jpg", "hero_library/type_disease.card.jpg", "hero_library/type_electric.card.jpg", "hero_library/type_fall.card.jpg", "hero_library/type_healthcare.card.jpg", "hero_library/type_heat.card.jpg", "hero_library/type_machine.card.jpg", "hero_library/type_neutral.card.jpg", "hero_library/type_overwork.card.jpg", "hero_library/type_stress.card.jpg", "hero_library/type_traffic.card.jpg", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512-maskable.png", "icons/icon-512.png", "index.html", "js/app.js", "js/engine.js", "js/render.js", "manifest.webmanifest", "skins/skin_original.json", "skins/skin_style1.json", "skins/skin_style1_print.json", "skins/skin_style2.json", "skins/skin_style3.json", "skins/skin_style4.json", "skins/skin_style5.json", "skins/skin_style6.json", "skins/skin_style7.json"];
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
