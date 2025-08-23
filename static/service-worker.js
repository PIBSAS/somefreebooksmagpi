const CACHE_NAME = "revistas-cache-v1";
const urlsToCache = ['./', '/static/logo.webp', '/static/favicon.ico', '/static/site.webmanifest', '/experiment-with-the-sense-hat.pdf', '/experiment-with-the-sense-hat.webp', '/get-started-with-micropython-raspberry-pi-pico.pdf', '/get-started-with-micropython-raspberry-pi-pico.webp', '/wearable-tech-projects.pdf', '/wearable-tech-projects.webp', '/retro-gaming-with-raspberry-pi.pdf', '/retro-gaming-with-raspberry-pi.webp', '/make-games-with-python.pdf', '/make-games-with-python.webp', '/beginners-guide-v4-Japanese.pdf', '/beginners-guide-v4-Japanese.webp', '/beginners-guide-v4-Spanish.pdf', '/beginners-guide-v4-Spanish.webp', '/beginners-guide-v4-Italian.pdf', '/beginners-guide-v4-Italian.webp', '/MagPi_Issue_SE_1.pdf', '/MagPi_Issue_SE_1.webp', '/simple-electronics-with-gpio-zero.pdf', '/simple-electronics-with-gpio-zero.webp', '/conquer-the-command-line-v2.pdf', '/conquer-the-command-line-v2.webp', '/C_and_GUI_programming_v1.pdf', '/C_and_GUI_programming_v1.webp', '/beginners-guide-v4-French.pdf', '/beginners-guide-v4-French.webp', '/book-of-making-vol-1.pdf', '/book-of-making-vol-1.webp', '/beginners-guide-v4-Danish.pdf', '/beginners-guide-v4-Danish.webp', '/beginners-guide-v4-English.pdf', '/beginners-guide-v4-English.webp', '/camera-guide.pdf', '/camera-guide.webp', '/retro-gaming-with-raspberry-pi-2nd-edition.pdf', '/retro-gaming-with-raspberry-pi-2nd-edition.webp', '/build-a-raspberry-pi-media-player.pdf', '/build-a-raspberry-pi-media-player.webp', '/get-started-with-raspberry-pi.pdf', '/get-started-with-raspberry-pi.webp', '/learn-to-code-with-scratch.pdf', '/learn-to-code-with-scratch.webp', '/beginners-guide-v4-Norwegian.pdf', '/beginners-guide-v4-Norwegian.webp', '/beginners-guide-v4-Swedish.pdf', '/beginners-guide-v4-Swedish.webp', '/beginners-guide-v4-Greek.pdf', '/beginners-guide-v4-Greek.webp', '/raspberry-pi-beginners-book.pdf', '/raspberry-pi-beginners-book.webp', '/book-of-making-vol-2.pdf', '/book-of-making-vol-2.webp', '/help-my-computer-is-broken.pdf', '/help-my-computer-is-broken.webp', '/Code_the_classics_v1_1ed.pdf', '/Code_the_classics_v1_1ed.webp', '/beginners-guide-v4-German.pdf', '/beginners-guide-v4-German.webp', '/beginners-guide-v4-Portuguese.pdf', '/beginners-guide-v4-Portuguese.webp'];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request).catch(() => new Response("No hay conexión y el recurso no está en caché.", {
      headers: { "Content-Type": "text/plain" }
    })))
  );
});