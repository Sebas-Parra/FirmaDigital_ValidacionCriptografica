# Gestión de Vulnerabilidades — FirmaDigital

Herramientas utilizadas: **Bandit** (análisis estático Python) · **Trivy** (dependencias) · revisión manual

---

## Bandit — Análisis estático del código Python

Comando ejecutado:
```bash
bandit -r backend/app/ -l
```

### Resultados

| ID | Severidad | Confianza | Descripción | Archivo | Mitigación |
|----|-----------|-----------|-------------|---------|------------|
| B110 | LOW | HIGH | `try/except/pass` detectado | `routes/documents.py:182` | **Aceptado** — el bloque ignora errores de eliminación en Supabase Storage intencionalmente: si el archivo remoto no existe, el registro de BD se elimina igual para mantener consistencia. No expone información ni compromete la seguridad. |

**Resumen:** 0 HIGH · 0 MEDIUM · 1 LOW (aceptado)

---

## Trivy — Escaneo de dependencias

Escaneo del filesystem de `backend/` buscando CVEs con severidad HIGH y CRITICAL en las dependencias declaradas en `requirements.txt`.

Ejecutado en CI automáticamente en cada push. Ver resultados en GitHub Actions → _Dependency vulnerability scan (Trivy)_.

---

## Vulnerabilidades identificadas y mitigadas (revisión manual)

### 1. Inyección SQL
- **Riesgo:** Consultas con datos de usuario no sanitizados
- **Severidad:** Alta
- **Mitigación:** Se utiliza SQLAlchemy ORM con consultas parametrizadas en todos los endpoints. No se construyen queries con concatenación de strings.

### 2. Exposición de credenciales
- **Riesgo:** Claves secretas hardcodeadas en el código fuente
- **Severidad:** Alta
- **Mitigación:** Todas las credenciales (SECRET_KEY, JWT_SECRET_KEY, SERVICE_ROLE_KEY) se cargan desde `.env` vía `python-dotenv`. El archivo `.env` está en `.gitignore`.

### 3. Autenticación débil
- **Riesgo:** Contraseñas almacenadas en texto plano o con hash débil
- **Severidad:** Alta
- **Mitigación:** Se usa bcrypt con `rounds=10` (costo adaptativo). Mínimo 8 caracteres validado en servidor.

### 4. JWT sin expiración adecuada
- **Riesgo:** Tokens de sesión válidos indefinidamente
- **Severidad:** Media
- **Mitigación:** Flask-JWT-Extended aplica expiración por defecto. Los tokens se eliminan del localStorage al hacer logout.

### 5. CORS permisivo
- **Riesgo:** Cualquier origen puede hacer peticiones a la API
- **Severidad:** Media
- **Mitigación:** `ALLOWED_ORIGINS` configurado con lista explícita de orígenes permitidos vía variable de entorno. `supports_credentials=True` solo para el origen autorizado.

### 6. Clave privada RSA en base de datos
- **Riesgo:** Clave privada expuesta si la BD es comprometida
- **Severidad:** Media
- **Mitigación:** La clave privada se cifra con AES-256-GCM antes de persistirla. La clave de cifrado es el `SECRET_KEY` de la aplicación, no almacenado en BD.

### 7. Enumeración de usuarios
- **Riesgo:** El endpoint de login revela si un email existe con mensajes distintos
- **Severidad:** Baja
- **Mitigación:** El endpoint devuelve siempre el mismo mensaje genérico ("Credenciales incorrectas") tanto para email inexistente como contraseña incorrecta.

### 8. File Upload Bypass — extensión falsa
- **Riesgo:** Un atacante puede renombrar un archivo malicioso (ej. `exploit.sh` → `exploit.pdf`) y subirlo al sistema, ya que la validación original solo verificaba la extensión del nombre
- **Severidad:** Alta
- **Detección:** Revisión manual de código (OWASP A04: Insecure Design)
- **Mitigación:** Validación en dos capas:
  1. Verificación de extensión `.pdf`
  2. Verificación de **magic bytes** con regex estricta: el archivo debe iniciar exactamente con `%PDF-1.x` o `%PDF-2.x` según ISO 32000. Un simple prepend de `%PDF` a un script no es suficiente.

```python
# routes/documents.py
if not re.match(rb'^%PDF-[12]\.\d', file_bytes[:10]):
    return jsonify({'error': 'El archivo no es un PDF válido'}), 400
```

### 10. Ausencia de límite de tamaño en uploads
- **Riesgo:** Un atacante podría subir archivos de varios GB para agotar memoria/disco (DoS)
- **Severidad:** Media
- **Detección:** Revisión manual de código
- **Mitigación:** Se configuró `MAX_CONTENT_LENGTH = 10 MB` en Flask. Requests mayores son rechazados automáticamente con HTTP 413 antes de leer el cuerpo.

### 11. Validación débil de campos de texto
- **Riesgo:** Entradas sin límite de longitud o sin validación de formato permiten inyectar datos malformados en la BD (usernames de 10,000 caracteres, emails inválidos)
- **Severidad:** Baja
- **Detección:** Revisión manual de código
- **Mitigación:** Se implementó validación centralizada `_validate_user_fields()` en todos los endpoints que reciben username/email/password:
  - Username: 1-50 caracteres, solo `[\w.\-]`
  - Email: regex `[^@\s]+@[^@\s]+\.[^@\s]+`, máx 120 chars
  - Password: 8-128 caracteres

### 9. Sin límite de intentos de login (rate limiting)
- **Riesgo:** Ataques de fuerza bruta contra credenciales
- **Severidad:** Baja
- **Estado:** **Pendiente de mitigación** — bcrypt con rounds=10 (~57ms/intento) dificulta ataques masivos, pero no existe límite de intentos explícito. Se recomienda implementar Flask-Limiter en producción.

---

## Pruebas desde Kali Linux (entorno virtualizado)

| Prueba | Herramienta | Resultado |
|--------|-------------|-----------|
| Escaneo de puertos | Nmap | Puerto 5000 (Flask) y 5432 (PostgreSQL) expuestos en red interna |
| Análisis de tráfico HTTP | Wireshark | Tokens JWT visibles — se recomienda HTTPS en producción |
| Intento de SQL Injection | Manual | No vulnerable (ORM parametrizado) |
| Intento de acceso sin JWT | curl | 401 Unauthorized correctamente |
| Acceso a endpoint admin sin rol | curl | 403 Forbidden correctamente |

---

*Última actualización: Sprint 4*
