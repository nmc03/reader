self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(key => caches.delete(key)));
    await self.registration.unregister();
    const windows = await self.clients.matchAll({
      type: "window",
      includeUncontrolled: true
    });
    for (const client of windows) {
      try { await client.navigate(client.url); } catch (_) {}
    }
  })());
});

self.addEventListener("fetch", event => {
  event.respondWith(fetch(event.request));
});
