//static/js/baliza_activate.js

(function () {
    if (!window.runFingerprint || !window.BALIZA_ORIGEN) {
        console.warn("[BALIZA] Orquestador o origen no disponible");
        return;
    }

    document.addEventListener("DOMContentLoaded", async () => {
        try {
            const fpData = await window.runFingerprint();
            await fetch("/fingerprint/collect", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    source_type: "baliza",
                    origen: window.BALIZA_ORIGEN,
                    profile: window.BALIZA_PROFILE || "default",
                    fingerprint: fpData
                })
            });

        } catch (e) {
            console.warn("[BALIZA] Error en activación de baliza", e);
        }


    });
})();
