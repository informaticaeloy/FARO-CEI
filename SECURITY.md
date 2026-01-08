
---

# 🔐 `SECURITY.md`

```markdown
# Política de Seguridad

## 1. Autenticación

- Autenticación basada en usuario único administrador
- Sesiones gestionadas por Flask
- Logout explícito

---

## 2. Gestión de contraseñas

- Las contraseñas **NO se almacenan en claro**
- Hashing mediante `werkzeug.security`:
  - Algoritmo: PBKDF2-SHA256
  - Iteraciones elevadas

---

## 3. Credenciales por defecto

Si el sistema detecta credenciales por defecto (`usuario / usuario`):
- Se fuerza cambio de contraseña
- No se permite acceso al sistema hasta cumplir política

---

## 4. Política mínima de contraseña

Requisitos:
- Longitud mínima: 10 caracteres
- Al menos:
  - 1 mayúscula
  - 1 minúscula
  - 1 número
  - 1 carácter especial

---

## 5. Protección frente a ataques

### Brute-force
- Control de intentos fallidos
- Bloqueo temporal por IP + usuario
- Registro de eventos de bloqueo

### Logging
- Todos los intentos de login quedan registrados
- Se conserva información de contexto (IP, host, agente)

---

## 6. Persistencia y datos

- Datos almacenados localmente en CSV / JSON
- Recomendación:
  - Cifrar disco
  - Proteger permisos de ficheros
  - No exponer el directorio `data/`

---

## 7. Despliegue recomendado

- Entorno aislado
- HTTPS obligatorio
- Reverse proxy (Nginx)
- No ejecutar como root

---

## 8. Disclaimer

Esta plataforma es defensiva y de análisis.
No ejecuta acciones ofensivas ni intrusivas.

---
