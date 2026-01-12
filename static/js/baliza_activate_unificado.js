//static/js/baliza_activate_unificado.js

(async () => {
  if (!window.runFingerprint || !window.BALIZA_ORIGEN_VISITA) return;

  // Aseguramos ejecución única
  if (window.__balizaFingerprintSent) return;
  window.__balizaFingerprintSent = true;

  document.addEventListener("DOMContentLoaded", async () => {
    try {
      const fpData = await window.runFingerprint();

      // POST unificado: fingerprint + evento VIEW
      const resp = await fetch("/fingerprint/collect_baliza", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origen: window.BALIZA_ORIGEN_VISITA || "HTML",
          baliza_id: window.BALIZA_ID,
          evento: "VIEW",
          fingerprint: fpData
        })
      });

      const data = await resp.json();
      console.log("[BALIZA] Fingerprint y evento VIEW registrados:", data.fp_id);

    } catch (e) {
      console.warn("[BALIZA] Error al registrar fingerprint/VIEW:", e);
    }
  });
})();




//(async () => {
//  if (!window.runFingerprint || !window.BALIZA_ORIGEN_VISITA) return;
//
//  document.addEventListener("DOMContentLoaded", async () => {
//    try {
//      const fpData = await window.runFingerprint();
//
//      // POST unificado: fingerprint + evento VIEW
//      const resp = await fetch("/fingerprint/collect_baliza", {
//        method: "POST",
//        headers: { "Content-Type": "application/json" },
//        body: JSON.stringify({
//          origen: window.BALIZA_ORIGEN_VISITA,
//          evento: "VIEW",
//          fingerprint: fpData
//        })
//      });
//
//      const data = await resp.json();
//      console.log("[BALIZA] Fingerprint y evento VIEW registrados:", data.fp_id);
//
//    } catch (e) {
//      console.warn("[BALIZA] Error al registrar fingerprint/VIEW:", e);
//    }
//  });
//})();
