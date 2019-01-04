FROM debian:9.5-slim

LABEL "com.github.actions.name"="Git Commit Email"
LABEL "com.github.actions.description"="Send email containing information about git commit"
LABEL "com.github.actions.icon"="mic"
LABEL "com.github.actions.color"="red"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python \
 && rm -rf /var/lib/apt/lists/*

COPY entrypoint.py /
ENTRYPOINT /entrypoint.py
