# Unified Dockerfile with ARG-driven build flavor
# Stages: builder -> export -> runtime (linux-only)
# Usage examples:
#  - Linux export:   docker buildx build --build-arg FLAVOR=linux   --target export  -f Dockerfile .
#  - Windows export: docker buildx build --build-arg FLAVOR=wine    --target export  -f Dockerfile .
#  - Linux runtime:  docker buildx build --build-arg FLAVOR=linux   --target runtime -f Dockerfile .

FROM ubuntu:24.04 AS builder

ARG FLAVOR=linux
ARG WINE_TARGET_ARCH=amd64
ENV WINE_TARGET_ARCH=${WINE_TARGET_ARCH}
WORKDIR /app

# Minimal base tools; install specifics via scripts/*-install-deps.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy sources and scripts once; select scripts by FLAVOR
COPY requirements.txt ./
COPY scripts ./scripts

RUN set -eux; \
    case "$FLAVOR" in \
      linux) cp scripts/linux-install-deps.sh scripts/install-deps.sh; cp scripts/linux-build.sh scripts/build.sh ;; \
      wine)  cp scripts/wine-install-deps.sh  scripts/install-deps.sh; cp scripts/wine-build.sh  scripts/build.sh  ;; \
      *) echo "Unknown FLAVOR=$FLAVOR (expected linux|wine)" >&2; exit 1 ;; \
    esac

RUN bash scripts/install-deps.sh

COPY ytsprint ./ytsprint
RUN bash scripts/build.sh

# Export artifacts (copies whole dist)
FROM scratch AS export
COPY --from=builder /app/dist/ /

# Linux runtime image (not used for wine)
FROM ubuntu:24.04 AS runtime
WORKDIR /

RUN apt-get update && apt-get install -y \
    libc6 \
    libgcc-s1 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist /dist
RUN set -eux; \
    bin=$(echo /dist/ytsprint-linux-*); \
    install -m 0755 "$bin" /usr/local/bin/ytsprint; \
    rm -rf /dist

RUN useradd -m appuser
USER appuser
WORKDIR /home/appuser

ENV YOUTRACK_URL="" \
    YOUTRACK_TOKEN="" \
    YTSPRINT_CRON="0 8 * * 1" \
    YTSPRINT_FORWARD="1" \
    YTSPRINT_LOG_LEVEL="INFO" \
    YOUTRACK_BOARD="" \
    YOUTRACK_PROJECT=""

ENTRYPOINT ["ytsprint"]
CMD ["--daemon"]
