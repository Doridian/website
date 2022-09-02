FROM caddy

COPY Caddyfile /etc/caddy/Caddyfile
COPY src /srv
