# 🌐 Despliegue de Proyecto IoT en AWS con HTTPS y Dominio Personalizado

Este proyecto despliega una solución IoT con frontend (NiceGUI) y backend (FastAPI + MQTT/AWS IoT) usando AWS Copilot, ECS Fargate y dominio propio con HTTPS.

---

## 🧱 Estructura del Proyecto

```
project-root/
├── docker-compose.yml
├── frontend/     ← NiceGUI
│   └── Dockerfile
└── backend/      ← FastAPI + conexión a AWS IoT + Wemos
    └── Dockerfile
```

---

## ✅ Paso a Paso del Despliegue

### 1. Instalación y Configuración

- AWS CLI (`aws configure`) con IAM `AdministratorAccess`
- Copilot CLI instalada
- Docker instalado y configurado

### 2. Subida de Imágenes Docker a AWS ECR

```bash
# Login a ECR
aws ecr get-login-password | docker login --username AWS --password-stdin 081022247189.dkr.ecr.us-east-1.amazonaws.com

# Backend
docker build -t backend .
docker tag backend:latest 081022247189.dkr.ecr.us-east-1.amazonaws.com/backend
docker push 081022247189.dkr.ecr.us-east-1.amazonaws.com/backend

# Frontend
docker build -t frontend .
docker tag frontend:latest 081022247189.dkr.ecr.us-east-1.amazonaws.com/frontend
docker push 081022247189.dkr.ecr.us-east-1.amazonaws.com/frontend
```

### 3. Inicialización de Copilot

```bash
copilot init
```

- Proyecto: `iot-app`
- Servicio frontend: `Load Balanced Web Service`
- Dockerfile: `./frontend/Dockerfile`
- Puerto: `8080`

### 4. Agregar el Servicio Backend

```bash
copilot svc init --name backend --svc-type "Backend Service" --dockerfile ./backend/Dockerfile
```

### 5. Crear Entorno

```bash
copilot env init --name test --profile default --default-config
```

### 6. Desplegar Servicios

```bash
copilot deploy --env test
```

---

## 🔐 Configurar Dominio Personalizado con HTTPS

### 1. Comprar dominio en [nic.ar](https://nic.ar)

Ej: `iot-services.com.ar`

### 2. Crear Hosted Zone en Route 53

- Tipo: Public Hosted Zone
- Nombre: `iot-services.com.ar`
- Copiar los `NS` generados

### 3. Delegar dominio en nic.ar

- Ingresar los NS en la delegación del dominio

### 4. Editar Manifest de Copilot

```yaml
# copilot/frontend/manifest.yml
http:
  alias: "app.iot-services.com.ar"
```

### 5. Redeploy del frontend

```bash
copilot deploy --name frontend --env test
```

Copilot configura:
- Certificado HTTPS (ACM)
- Load Balancer
- Asociación de dominio

---

## 🌍 Resultado

Aplicación disponible en:

```
https://app.iot-services.com.ar
```

---

## 🚀 Copilot Automáticamente Provee:

- ECS + Fargate
- VPC, subnets, balanceadores
- Certificados SSL (ACM)
- DNS con Route 53
- Despliegue escalable y seguro
