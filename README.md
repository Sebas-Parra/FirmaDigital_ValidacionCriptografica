# FirmaDigital - Validación Criptográfica
Plataforma web segura de firma digital con validación criptográfica.

## Stack
- **Backend:** Python 3 + Flask + SQLAlchemy + Flask-JWT-Extended
- **Frontend:** Vue.js 3 + Tailwind CSS
- **Base de datos:** PostgreSQL (Docker local) + Supabase Storage (archivos)
- **CI/CD:** GitHub Actions + Bandit + Trivy

## Equipo
| Rol | Persona |
|-----|---------|
| Product Owner | Brayan Jacome |
| Scrum Master | Sebastian Parra |
| Apoyo Moral | Juan Granda |

## Escenario de red

| VM | Rol | IP (red interna) |
|----|-----|-----------------|
| Ubuntu Server | Backend + BD | 192.168.1.100 |
| Ubuntu Desktop | Cliente legítimo | 192.168.1.101 |
| Kali Linux | Pruebas de seguridad | 192.168.1.102 |
| Metasploitable2 | Análisis de riesgos | 192.168.1.103 |

> Ajusta las IPs según tu configuración de red interna.

---

## Levantar el proyecto

### En Ubuntu Server (backend + BD)

```bash
# 1. Base de datos
docker compose up -d

# 2. Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configurar .env con la IP del servidor en ALLOWED_ORIGINS
# ALLOWED_ORIGINS=http://192.168.1.101:8080
python run.py
```

```bash
# 3. Crear superusuario
flask create-superuser admin@email.com
```

### En Ubuntu Desktop (cliente)

```bash
cd frontend
npm install

# Desarrollo apuntando al servidor
VUE_APP_API_URL=http://192.168.1.100:5000/api npm run serve

# O editar frontend/.env.production con la IP del servidor y compilar
npm run build
# Servir dist/ con cualquier servidor HTTP (python3 -m http.server 8080)
```

### Desarrollo local (sin VMs)
```bash
# Terminal 1
docker compose up -d
cd backend && source venv/bin/activate && python run.py

# Terminal 2
cd frontend && npm run serve
```

---

## Sprints

### Sprint 1 (Sem 1-2): Planificación + entorno
**Retrospectiva:**
- Se configuró el repositorio con estructura Flask + Vue
- Se conectó Flask a PostgreSQL vía SQLAlchemy
- Se configuró el pipeline CI con GitHub Actions + Bandit
- Se instalaron y configuraron las 4 VMs en red interna (Kali, Ubuntu Server, Ubuntu Desktop, Metasploitable2)
- Aprendizaje: psycopg2 es necesario para conectar Python con PostgreSQL

### Sprint 2 (Sem 3-4): Frontend + autenticación + hash
**Retrospectiva:**
- Se implementó autenticación con JWT y bcrypt (rounds=10)
- Se crearon los modelos de BD con SQLAlchemy (users, certificates, documents, logs)
- Se implementó SHA-256 para verificación de integridad de archivos
- Se desarrolló el frontend con Vue.js 3 y Tailwind CSS
- Se configuró CORS con variables de entorno
- Aprendizaje: flask-cors debe aplicarse a la app, no al JWT manager

### Sprint 3 (Sem 5-6): Criptografía + firma + CA
**Retrospectiva:**
- Se implementó cifrado AES-256-GCM para archivos
- Se generaron pares de claves RSA-2048 por usuario
- Se implementó firma digital con RSA-PSS + SHA-256
- Se simuló una CA con certificados X.509 autofirmados
- Se integró Supabase Storage para persistencia de archivos
- Se desarrollaron las vistas de Documentos y Certificados en Vue
- Aprendizaje: to_dict() debe incluir todos los campos necesarios para el frontend

### Sprint 4 (Sem 7-8): Pruebas + seguridad + admin
**Retrospectiva:**
- Se implementó suite de 58 pruebas automatizadas (pytest) cubriendo: hash, AES, RSA, X.509, auth CRUD, documentos y certificados
- Se completó el CRUD de usuarios: registro, consulta, actualización y eliminación de cuenta
- Se añadió panel de administración con roles (user / admin / superuser)
- Se ejecutó análisis estático con Bandit: 0 issues HIGH/MEDIUM, 1 LOW aceptado (B110)
- Se añadió escaneo de dependencias con Trivy al pipeline CI
- Se generó script de análisis estadístico de operaciones criptográficas
- Aprendizaje: `use_reloader=False` necesario en Flask sobre Linux para evitar bloqueos del reloader
