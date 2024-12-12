# ai-boardgame-service
## Project Clone

Use SSH to clone the project.

## Installation and Configuration

Before starting the project, please ensure that you have installed the following tools:

- VSCode plugin: Dev Containers

### ./.devcontainer Configuration

For Windows systems, the following configurations are required. Mac users can skip these steps.

#### (1) .devcontainer/Dockerfile

Comment out the following code:

```bash
# ARG USERNAME=vscode
# ARG USER_UID=1000
# ARG USER_GID=$USER_UID

# RUN groupadd --gid $USER_GID $USERNAME \
#     && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# RUN usermod -aG sudo $USERNAME
# RUN echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# USER $USERNAME
```

#### (2) .devcontainer/postCreateCommand.sh

Comment out the following code:

```bash
# sudo chown vscode:vscode /workspace
```

#### (3).devcontainer/docker-compose.yml

Replace the vscode user with the root user in this file:

```
services:
  ai-narrative-server:
    container_name: ai-narrative-server-${USER}
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace
    user: root  //change here in original file 
```

#### (4)Global File Encoding Setting

Change the encoding format from CRLF to LF:

1. First, open VSCode settings.
2. Then, type "end of line" in the search box and find the "Files: Eol" setting.
3. Set its value to \n, which represents LF (Line Feed).
4. After setting, restart VSCode.

## Project Start

### Enter the Docker Container

1. Use the VSCode shortcut `ctrl+shift+p` (Mac: `command+shift+p`) to open the command palette.
2. Find and click the command "Dev Containers: Restart and Rebuild Container."

### Add new dependency

If you add new dependencies using pip install, you need to run pip freeze > requirements.txt to refresh the environment.

```
pip freeze > requirements.txt
```

### Start command

```
./run.sh start
```


### Restart command

```
lsof -i:8080

kill -9 [pid]

./run.sh start 
```