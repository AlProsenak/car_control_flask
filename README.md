# 🚗 Car Control 🚗 -- Demo Backend Application in Flask

## 📖 About 📖

Car Control is a RESTful API application built with Flask. It allows for CRUD operations,
such as retrieving vehicle data, creating new vehicles, updating existing vehicles and deleting vehicles.

APIs that alter vehicle state (CUD) are secured via JWT, using Keycloak.

## 🚀 Start Application Locally 🚀

### Pre-requisites:

1. Installed Python 3.13+
    - Debian based distro:
      ```shell
      apt update && apt upgrade -y
      apt install python3
      ```
    - Arch based distro:
      ```shell
      pacman -Syu
      pacman -S python
      ```
2. Installed pip 25.0+:
    - Debian based distro:
      ```shell
      apt install python3-pip
      ```
    - Arch based distro:
      ```shell
      pacman -S python-pip
      ```
3. Install docker-engine docker-cli and docker-compose
    - Debian based distro:
      ```shell
      apt install docker.io docker-compose
      ```
    - Arch based distro:
      ```shell
      pacman -S docker docker-compose
      ```
      Consult [Arch-wiki](https://wiki.archlinux.org/title/Docker) to run `docker` CLI commands as a non-root user.

If Docker daemon is not running:

```shell
# Start docker.service
systemctl start docker
# or ensure it starts automatically on system boot
systemctl enable docker
```

### Setup

1. Clone the repository:
   ```shell
   git clone https://github.com/AlProsenak/car-control-flask.git
   cd car-control-flask
   ```
2. Start virtual environment:
   ```shell
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install application dependencies:
   ```shell
   pip install -r requirements.txt
   ```
4. Start docker-compose:
   ```shell
   docker compose -f docker/docker-compose.yaml up -d
   ```
   > Keycloak will auto-configure itself by importing file `./docker/keycloak/car-control-realm.json` via Docker-compose
   command `kc.sh start-dev --import-realm`.
5. Start application:
   ```shell
   flask run
   ```
   Export for `src` directory is already configured in `.flaskenv`, which auto-sources environment variables, such as
   `export FLASK_APP=src`

### Start application in Docker

1. Build Docker image:
   ```shell
   docker build --tag ${IMAGE_NAME}:${IMAGE_VERSION} .
   ```
2. Start Docker container
   ```shell
   docker run --name ${CONTAINER_NAME} \ 
   -p ${HOST_MACHINE_PORT}:5000 \
   -e FLASK_ENV=docker \
   --network docker_carctrl_network \
   ${IMAGE_NAME}:${IMAGE_VERSION} \
   -d
   ```

   Mandatory:
    - port
    - Flask environment variable
    - network (check with `docker network ls`)

> By setting the environment variable `FLASK_ENV=docker`, the application will automatically configure itself to
> successfully connect to the correct hostnames within the Docker network stack.

---

## 🌍 Environment Variables 🌍

-- WIP --  
(see `./src/config/Environment.py` for now)

---

## 🔐 API Overview 🔐

> ⚠️There is included Postman export file with all locally configured endpoints, including Keycloak ⚠️  
> File location: `./postman/car_control_local.postman_collection.json`

> TODO: OpenAPI specification and Swagger implementation

### Get vehicle data

`GET http://localhost:5000/api/v1/vehicle`

Example:

```shell
curl --location 'http://localhost:5000/api/v1/vehicle?model_like=X&sort_by=make&sort_order=DESC&page_size=20&page_number=2'
```

### Get vehicle data by ID

`GET http://localhost:5000/api/v1/vehicle/:id`

Example:

```shell
curl --location 'http://localhost:5000/api/v1/vehicle/1'
```

### Create vehicle

`POST http://localhost:5000/api/v1/vehicle/:id`

Example:

```shell
curl --location 'http://localhost:5000/api/v1/vehicle' \
--header 'Content-Type: application/json' \
--header 'Authorization: ••••••' \
--data '{
    "vehicle":   {
        "make": "Ford",
        "model": "Mustang",
        "year": 2022,
        "fuel_type": "GASOLINE",
        "door_count": 2,
        "price": 35000.00,
        "currency_code": "USD",
        "description": "Car is in pristine condition."
    }
}'
```

### Update vehicle

`PUT http://localhost:5000/api/v1/vehicle`

Example:

```shell
curl --location --request PUT 'http://localhost:5000/api/v1/vehicle' \
--header 'Content-Type: application/json' \
--header 'Authorization: ••••••' \
--data '{
    "vehicle":   {
        "id": 1,
        "make": "Ford",
        "model": "Mustang",
        "year": 2021,
        "fuel_type": "GASOLINE",
        "door_count": 2,
        "price": 35000.00,
        "currency_code": "USD",
        "description": "New vehicle descirption"
    }
}'
```

### Delete vehicle

`DELETE http://localhost:5000/api/v1/vehicle/:id`

Example:

```shell
curl --location --request DELETE 'http://localhost:5000/api/v1/vehicle/1' \
--header 'Authorization: ••••••'
```

---

## Development

### IDE Configurations

- Run:
   ```
   Python 3.13
   ```
- Script:
   ```
   /home/grumpy/Development/car_control_flask/src/__init__.py
   ```
- Working directory:
   ```
   /home/grumpy/Development/car_control_flask/
   ```
- Environment variables (optional):
   ```
   FLASK_ENV=local;FLASK_DEBUG=1
   ```

### Export new Keycloak configurations

1. Exec into Docker container running Keycloak:
   ```shell
   docker exec -it ${KEYCLOAK_CONTAINER_NAME} bash
   ```
2. Export Keycloak config:
   ```shell
   `/opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data/import --users realm_file`
   ```
   It generates configuration inside Keycloak Docker container in directory:
   ```
   /opt/keycloak/data/import/${REALM_NAME}-realm.json
   ```
3. Copy configuration to host machine:
   ```shell
   docker cp ${KEYCLOAK_CONTAINER_NAME}:/opt/keycloak/data/import/${REALM_NAME}-realm.json ~/${DESIRED_HOST_DIRECTORY_LOCATION}
   ```
4. [OPTIONAL] Override previous configuration by placing new in the project directory:
   ```
   ./docker/keycloak/${REALM_NAME}-realm.json`
   ```
 