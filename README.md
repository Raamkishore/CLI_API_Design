# CLI and API design

## Installations:
- Package **my_cli** must be installed before using the commands directly on the terminal. The package can be installed with the following command:

    ```pip install -e my_cli```

- Install all the requirement packages using the following command:

    ```pip install -r requirements.txt```

<br>
Commands for different operations are given as follows: (Please note that there is no "space" after the hyphen for CLI commands)

## Downloader Initialization

### CLI

```downloader -initialize <project-id>```

### API

```http://localhost:4000/initialize/{project-id}```

## Downloader Query

### CLI

```downloader -query <query-string>```

### API

```http://localhost:4000/query_string?search_string=<string>```

## Download All URLs

### CLI

```downloader -download-all```

### API

```http://localhost:4000/download_all```

## Downloader status

### CLI

The downloader progress will be printed automatically. No need to run any specific command.

### API

```http://localhost:4000/download_all/status```

## Access Swagger documentation

Please use the following API:

```http://localhost:4000/api/docs```

## Docker

Separate installation of packages are not needed for Docker as the installation commands are already provided in the Dockerfile. Once the docker image is built, a container can be started and the Web API server (Flask) runs automatically. Port for both the host and the docker is 4000.

If you would like to access the downloading files, please mount the volume while running the container.

## Location of DB and downloaded files

The database and the folder with the downloaded files are located in the same directory where the flask server is running and the CLI commands are being executed.