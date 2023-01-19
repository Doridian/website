FROM golang:1.19-alpine AS golang

ENV CGO_ENABLED=0
COPY apiserver /src/apiserver
WORKDIR /src/apiserver
RUN go build -o /bin/apiserver *.go

FROM alpine AS generator

RUN apk --no-cache add python3
COPY scripts /opt/scripts
RUN /opt/scripts/geofeed/generator.py /srv/geofeed.csv

FROM caddy:2-alpine

RUN apk add --no-cache s6 s6-overlay

COPY rootfs /
COPY static /srv
COPY --from=generator /srv /srv
COPY --from=golang /bin/apiserver /bin/apiserver

ENTRYPOINT [ "/init" ]
CMD [ ]
