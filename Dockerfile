FROM alpine AS builder

RUN apk --no-cache add python3

COPY scripts /opt/scripts

RUN /opt/scripts/geofeed/generator.py /srv/geofeed.csv

FROM caddy

COPY Caddyfile /etc/caddy/Caddyfile
COPY src /srv
COPY --from=builder /srv /srv
