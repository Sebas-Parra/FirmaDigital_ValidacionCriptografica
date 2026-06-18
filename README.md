# FirmaDigital - Validación Criptográfica
Plataforma web segura de firma digital con validación criptográfica.

## Stack
- **Backend:** Python + Flask + SQLAlchemy + Supabase
- **Frontend:** Vue.js 3
- **Base de datos:** PostgreSQL (Supabase)

## Equipo
| Rol | Persona |
|-----|---------|
| Product Owner | Brayan Jacome |
| Scrum Master | Sebastian Parra |
| Apoyo Moral | Juan Granda |

## Sprints

### Sprint 1 (Sem 1-2): Planificación + entorno 
**Retrospectiva:**
- Se configuró el repositorio con estructura Flask + Vue
- Se conectó Flask a Supabase (PostgreSQL)
- Se configuró el pipeline CI con GitHub Actions + Bandit
- Se instalaron y configuraron las 4 VMs en red interna
- Aprendizaje: psycopg2 es necesario para conectar Python con PostgreSQL

### Sprint 2 (Sem 3-4): Frontend + autenticación + hash
**Retrospectiva:**
- Se implementó autenticación con JWT y bcrypt
- Se crearon los modelos de BD con SQLAlchemy (users, certificates, documents, logs)
- Se implementó SHA-256 para verificación de integridad de archivos
- Se desarrolló el frontend con Vue.js 3 y Tailwind CSS
- Se configuró CORS con variables de entorno
- Aprendizaje: flask-cors debe aplicarse a la app, no al JWT manager

### Sprint 3 (Sem 5-6): Criptografía + firma + CA
**Retrospectiva:**
- Se implementó cifrado AES-256-GCM para archivos
- Se generaron pares de claves RSA-2048 por usuario
- Se implementó firma digital y verificación con RSA
- Se simuló una CA con certificados X.509
- Se desarrollaron las vistas de Documentos y Certificados en Vue
- Aprendizaje: to_dict() debe incluir todos los campos necesarios para el frontend

### Sprint 4 (Sem 7-8): Pruebas + artículo
_(pendiente)_
