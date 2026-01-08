# Arquitectura de la Plataforma CEI (Control de Exposición de la Información)

## 1. Visión general

La Plataforma CEI es un sistema defensivo orientado a la detección, correlación y control
de exposición de información a través de eventos, balizas y fingerprints técnicos.

No es un SIEM ni un SOC tradicional, sino una **capa especializada de control de exposición**
que actúa antes, durante y después de la pérdida de control de información.

---

## 2. Componentes principales

### 2.1 Capa Web (Flask)

- Gestión de sesiones
- Autenticación y control de acceso
- Paneles de visualización
- Configuración de políticas

Rutas organizadas por dominio funcional (`routes/`).

---

### 2.2 Motor de correlación de fingerprints

Responsable de:
- Normalizar señales técnicas (browser, platform, timezone, etc.)
- Aplicar pesos configurables
- Calcular score agregado
- Clasificar nivel de confianza: LOW / MEDIUM / HIGH

La política es **configurable en caliente** vía UI.

---

### 2.3 Persistencia ligera (CSV / JSON)

Diseño intencionado:
- Trazabilidad
- Auditabilidad
- Facilidad de despliegue
- Cero dependencias externas

Tipos de datos:
- Eventos
- Credenciales (hash)
- Configuración de políticas
- Fingerprints históricos

---

## 3. Flujo de datos principal

```text
[ Cliente / Baliza ]
        |
        v
[ Rutas Flask ]
        |
        v
[ Normalización ]
        |
        v
[ Correlación / Scoring ]
        |
        v
[ Persistencia ]
        |
        v
[ Dashboard / Vista SOC ]
```
