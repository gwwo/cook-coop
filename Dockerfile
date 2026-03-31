ARG BASE_IMAGE
FROM ${BASE_IMAGE}

WORKDIR /app
ARG INSTALL_GIT=false
RUN if [ "$INSTALL_GIT" = "true" ]; then \
    apt-get update && apt-get install -y git ca-certificates && rm -rf /var/lib/apt/lists/*; \
    fi

COPY requirements.txt .
RUN grep -Ev "^torch|^pyglet" requirements.txt | pip install --no-cache-dir -r /dev/stdin
# we don't `pip install pyglet` in the container, as it needs to run at the host machine to display a window. 
# if you need to run the game_ui module, consider using a virtualenv at host with all the packages in `requirements.txt` installed

ARG INSTALL_TORCH=false
RUN if [ "$INSTALL_TORCH" = "true" ]; then \
    TORCH_VERSION=$(grep "^torch==" requirements.txt | cut -d'=' -f3) && \
    pip install --no-cache-dir torch==${TORCH_VERSION} --extra-index-url https://download.pytorch.org/whl/cpu; \
    fi