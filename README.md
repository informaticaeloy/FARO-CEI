<p align="center">
  <img src="docs/assets/logo.png" alt="FARO-CEI" width="180">
</p>

<h1 align="center">FARO-CEI</h1>

<p align="center">
  Plataforma de <strong>Behavioral Information Exposure Control</strong><br>
  Control avanzado de exposición informacional basado en comportamiento, fingerprints y señales contextuales.
</p>

<p align="center">
  <a href="#"><img alt="CI" src="https://img.shields.io/badge/GitHub_Actions-CI-blue"></a>
  <a href="#"><img alt="Stars" src="https://img.shields.io/github/stars/informaticaeloy/faro-cei"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/github/license/informaticaeloy/faro-cei"></a>
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue"></a>
  <a href="#"><img alt="Status" src="https://img.shields.io/badge/Status-Active-success"></a>
</p>

---

## 📌 ¿Qué es FARO-CEI?

**FARO-CEI (Control de Exposición de la Información)** es una plataforma web diseñada para **detectar, correlacionar y analizar accesos persistentes a información expuesta**, incluso cuando el control del canal original ya se ha perdido.

A través de **balizas, fingerprinting de comportamiento y correlación contextual**, FARO-CEI proporciona **visibilidad operativa, trazabilidad y contexto defensivo** sobre el uso real de información sensible.

> FARO-CEI **no sustituye** a un SIEM, SOC o DLP.  
> Se posiciona como una **capa especializada y complementaria**, centrada en la **exposición informacional**, no en el perímetro.

---

## 🎯 Problema que resuelve

FARO-CEI permite responder con evidencias a preguntas críticas como:

- ¿Quién accede a información que ya no debería estar activa?
- ¿Desde qué entorno, red o contexto se produce el acceso?
- ¿Se reutilizan enlaces o recursos fuera de su canal previsto?
- ¿Existen patrones persistentes entre accesos aparentemente aislados?
- ¿Estoy perdiendo control real sobre información ya distribuida?

---

## 🧩 Funcionalidades clave

### 🔹 Balizas (Beacons)

- Creación y gestión de balizas de seguimiento.
- Registro automático de accesos.
- Captura de contexto técnico:
  - IP pública
  - User-Agent
  - Timestamp
  - IP local y hostname (cuando es posible)
- Casos de uso:
  - Documentos
  - Enlaces
  - Recursos compartidos
  - Artefactos de auditoría

---

### 🔹 Fingerprinting y correlación

- Generación de fingerprints basados en comportamiento.
- Agrupación lógica de eventos relacionados.
- Detección de:
  - Reutilización de información
  - Persistencia de accesos
  - Patrones anómalos
- Clasificación por nivel de confianza:
  - **HIGH**
  - **MEDIUM**
  - **LOW** (derivado automáticamente)

---

### 🔹 Umbrales de confianza dinámicos

- Configuración visual e interactiva.
- Reglas de consistencia:
  - HIGH y MEDIUM configurables.
  - LOW calculado automáticamente.
- Representación gráfica:
  - Barra vertical con gradiente
  - Marcadores sincronizados
  - Rangos dinámicos
- Validaciones automáticas para evitar incoherencias.

---

### 🔹 Centro de actividad y análisis

- Dashboard centralizado de eventos.
- Línea temporal de accesos.
- Vista detallada por fingerprint.
- Indicadores de riesgo:
  - Uso de VPN
  - Uso de TOR
  - Repetición de comportamiento
- Enfoque analítico orientado a **Blue Team y post-incidente**.

---

### 🔹 Autenticación y control de acceso

- Usuario administrador único.
- Contraseñas cifradas con **PBKDF2-SHA256 (werkzeug.security)**.
- Protección contra fuerza bruta:
  - Detección de intentos repetidos
  - Bloqueo temporal
  - Registro de eventos
- Cambio obligatorio de contraseña si se detectan credenciales por defecto.
- Auditoría completa de accesos.

---

### 🔹 Registro y auditoría

- Logging estructurado de:
  - Accesos
  - Autenticaciones
  - Bloqueos
- Persistencia ligera en CSV / JSON.
- Diseño auditable, transparente y trazable.

---

## 🔐 Enfoque de seguridad

- Arquitectura defensiva.
- Dependencias mínimas.
- Sin agentes ni fricción.
- Pensado para:
  - Blue Team
  - Auditoría interna
  - Investigación de fugas
  - Análisis post-incidente
- Fácil despliegue y mantenimiento.

---

## ❌ ¿Qué NO es FARO-CEI?

- ❌ No es un SIEM  
- ❌ No es un SOC  
- ❌ No es OSINT  
- ❌ No es un DLP tradicional  

FARO-CEI aporta **control activo sobre la exposición de la información**, no solo monitorización pasiva.

---

## 🧪 Casos de uso

- Auditoría de documentos compartidos
- Seguimiento de enlaces sensibles
- Control de información distribuida
- Pruebas de fuga controladas
- Investigación forense ligera
- Entornos Red Team / Blue Team

---

## ⚙️ Requisitos

- Python 3.10+
- Flask
- Navegador moderno
- Entorno local o servidor interno

> No requiere base de datos externa.

---

## 🚀 Instalación rápida

```bash
git clone https://github.com/informaticaeloy/faro-cei.git
cd faro-cei
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
