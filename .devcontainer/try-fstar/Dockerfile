FROM rust:1.94.0-slim-bookworm@sha256:8e0f5926ce10ec99e12703b315c0043e4709d6bdc740dc1d28753e5fb87c766f AS rust
FROM mcr.microsoft.com/dotnet/sdk:10.0.100-noble@sha256:b84b696efd5c236918761d35975209ad15918c4216cc6f41a573ff62e962ce72 AS tools

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG DEBIAN_FRONTEND=noninteractive
ARG FSTAR_RELEASE=nightly-2026-11-03
ARG FSTAR_SHA256=0e8ec704a786f967ad0b3a3a613fc0cbffba9a4ce770efb0ee6e2aff738b2909
ARG PAL_REV=7b3915e03090394718f1ffb771c2b92f21563247
ARG PAL_CSHARP_REV=3a6c05e15ea21f65ec5e66fe177305b135a7ce42

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    NUGET_PACKAGES=/opt/nuget \
    OPAMROOT=/opt/opam \
    OPAMSWITCH=5.3.0 \
    OPAMYES=1 \
    OPAMJOBS=2 \
    RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    CARGO_BUILD_JOBS=2 \
    FSTAR_EXE=/opt/fstar/bin/fstar.exe \
    PAL_ROOT=/opt/pal \
    PAL_CS_ROOT=/opt/pal-csharp \
    CC=clang-20 \
    CHERRY_CC=gcc-15 \
    PATH=/opt/fstar/bin:/opt/pal/target/release:/opt/opam/5.3.0/bin:/usr/lib/llvm-20/bin:/usr/local/cargo/bin:${PATH}

COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
      build-essential ca-certificates curl git gnupg libgmp-dev libffi-dev \
      libssl-dev libzstd-dev make opam pkg-config python3 sudo unzip \
    && curl --fail --silent --show-error https://apt.llvm.org/llvm-snapshot.gpg.key \
      | gpg --dearmor -o /usr/share/keyrings/llvm.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/llvm.gpg] https://apt.llvm.org/noble/ llvm-toolchain-noble-20 main' \
      > /etc/apt/sources.list.d/llvm.list \
    && curl --fail --silent --show-error --retry 3 \
      'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC8EC952E2A0E1FBDC5090F6A2C277A0A352154E5' \
      | gpg --dearmor -o /usr/share/keyrings/ubuntu-toolchain.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/ubuntu-toolchain.gpg] https://ppa.launchpadcontent.net/ubuntu-toolchain-r/test/ubuntu noble main' \
      > /etc/apt/sources.list.d/ubuntu-toolchain.list \
    && apt-get update -qq && apt-get install -y --no-install-recommends \
      clang-20 llvm-20-dev libclang-20-dev libclang-cpp20-dev gcc-15

RUN curl --fail --location --retry 3 \
      "https://github.com/FStarLang/FStar-nightly/releases/download/${FSTAR_RELEASE}/fstar-Linux-x86_64.tar.gz" \
      -o /tmp/fstar.tar.gz \
    && echo "${FSTAR_SHA256}  /tmp/fstar.tar.gz" | sha256sum --check \
    && mkdir -p /opt/fstar \
    && tar -xzf /tmp/fstar.tar.gz --strip-components=2 -C /opt/fstar \
    && rm /tmp/fstar.tar.gz \
    && fstar.exe --version

RUN opam init --bare --disable-sandboxing -y \
    && opam switch create 5.3.0 ocaml-base-compiler.5.3.0 -y \
    && opam install -y ocamlfind stdint zarith ppx_deriving_yojson

RUN apt-get install -y --no-install-recommends libstdc++-15-dev \
    && git init -q /opt/pal \
    && git -C /opt/pal remote add origin https://github.com/FStarLang/pal.git \
    && git -C /opt/pal fetch -q --depth 1 origin "${PAL_REV}" \
    && git -C /opt/pal checkout -q --detach FETCH_HEAD \
    && cargo build --release --locked --manifest-path /opt/pal/Cargo.toml \
    && make -C /opt/pal/pulse -j2

RUN git init -q /opt/pal-csharp \
    && git -C /opt/pal-csharp remote add origin https://github.com/FStarLang/pal-csharp.git \
    && git -C /opt/pal-csharp fetch -q --depth 1 origin "${PAL_CSHARP_REV}" \
    && git -C /opt/pal-csharp checkout -q --detach FETCH_HEAD \
    && dotnet build /opt/pal-csharp/src/Pal.Tool/Pal.Tool.csproj -c Release --verbosity minimal \
    && dotnet build /opt/pal-csharp/src/Pal.Analyzers/Pal.Analyzers.csproj -c Release --verbosity minimal \
    && make -C /opt/pal-csharp/pulse FSTAR_EXE=/opt/fstar/bin/fstar.exe -j2

RUN printf '#!/bin/sh\nexec dotnet /opt/pal-csharp/src/Pal.Tool/bin/Release/net10.0/palcs.dll "$@"\n' \
      > /usr/local/bin/palcs \
    && chmod +x /usr/local/bin/palcs \
    && groupmod --new-name vscode ubuntu \
    && usermod --login vscode --home /home/vscode --move-home --shell /bin/bash ubuntu \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode \
    && mkdir -p /opt/playground-smoke \
    && chmod -R a+rX /opt/fstar /opt/pal/pulse /opt/pal-csharp/pulse \
    && chown -R vscode:vscode /opt/opam /opt/nuget /opt/pal /opt/pal-csharp /opt/playground-smoke

FROM tools AS playground
COPY playground /opt/playground
COPY examples /opt/playground-seed/examples
COPY tutorial/book/code /opt/playground-seed/tutorials
USER vscode
ENV HOME=/home/vscode \
    CAML_LD_LIBRARY_PATH=/opt/opam/5.3.0/lib/stublibs \
    DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE=true
WORKDIR /opt/playground-smoke
# NuGet scratch locks retain the build UID; Dev Containers may remap it.
RUN python3 /opt/playground/setup.py /opt/playground-smoke && make check \
    && rm -rf /tmp/NuGetScratchvscode
