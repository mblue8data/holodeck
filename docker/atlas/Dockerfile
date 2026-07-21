FROM alpine:3.21 AS base
COPY --from=arigaio/atlas:latest-community /atlas /usr/local/bin/atlas
WORKDIR /migrations
ENTRYPOINT []
CMD ["tail", "-f", "/dev/null"]
