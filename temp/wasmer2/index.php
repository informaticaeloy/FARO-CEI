<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Visitor Fingerprint</title>
</head>
<body>

<h1>Visitor fingerprint</h1>
<pre id="output">Recolectando datos…</pre>

<script>
(async () => {
    try {
        const FingerprintJS = await import('https://openfpcdn.io/fingerprintjs/v5');
        const fp = await FingerprintJS.load();

        const result = await fp.get();

        const payload = {
            visitorId: result.visitorId,
            confidence: result.confidence?.score ?? null,
            components: result.components,
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth
            }
        };

        // Mostrar por pantalla
        document.getElementById("output").textContent =
            JSON.stringify(payload, null, 2);

        // Enviar al backend
        await fetch("collect.php", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

    } catch (e) {
        document.getElementById("output").textContent =
            "Error obteniendo fingerprint: " + e;
    }
})();
</script>

</body>
</html>
