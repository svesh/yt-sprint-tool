# Runtime Dockerfile. Copies a pre-built ytsprint binary into a minimal Ubuntu image.

FROM ubuntu:24.04

ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libc6 \
        libgcc-s1 \
        libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

ENV YOUTRACK_URL="" \
    YOUTRACK_TOKEN="" \
    YTSPRINT_CRON="0 8 * * 1" \
    YTSPRINT_FORWARD="1" \
    YTSPRINT_LOG_LEVEL="INFO" \
    YOUTRACK_BOARD="" \
    YOUTRACK_PROJECT=""

COPY dist/ /tmp/dist/

RUN set -eux; \
    arch="${TARGETARCH:-amd64}"; \
    case "$arch" in \
      amd64|x86_64) bin="/tmp/dist/ytsprint-linux-amd64" ;; \
      arm64|aarch64) bin="/tmp/dist/ytsprint-linux-arm64" ;; \
      *) echo "Unsupported TARGETARCH: $arch" >&2; exit 1 ;; \
    esac; \
    if [ ! -f "$bin" ]; then \
      echo "Runtime binary $bin not found. Ensure dist/ytsprint-linux-$arch exists." >&2; \
      ls -R /tmp/dist >&2; \
      exit 1; \
    fi; \
    install -m 0755 "$bin" /usr/local/bin/ytsprint; \
    rm -rf /tmp/dist

USER appuser
WORKDIR /home/appuser

EXPOSE 9108

ENTRYPOINT ["ytsprint"]
CMD ["--daemon"]
