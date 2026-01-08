async function getFingerprint() {
    const fp = {};

    // Básico
    fp.ua              = navigator.userAgent;
    fp.platform        = navigator.platform;
    fp.languages       = navigator.languages;
    fp.cookieEnabled   = navigator.cookieEnabled;
    fp.doNotTrack      = navigator.doNotTrack;

    // Pantalla
    fp.screen = {
        width: screen.width,
        height: screen.height,
        colorDepth: screen.colorDepth,
        pixelRatio: window.devicePixelRatio
    };

    // Timezone
    fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Hardware
    fp.hardware = {
        cores: navigator.hardwareConcurrency,
        memory: navigator.deviceMemory || null
    };

    // Canvas fingerprint
    try {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        ctx.textBaseline = "top";
        ctx.font = "14px Arial";
        ctx.fillText("fingerprint-test", 2, 2);
        fp.canvas = canvas.toDataURL();
    } catch {
        fp.canvas = null;
    }

    // WebGL
    try {
        const gl = document.createElement("canvas").getContext("webgl");
        const dbg = gl.getExtension("WEBGL_debug_renderer_info");
        fp.webgl = {
            vendor: gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL),
            renderer: gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)
        };
    } catch {
        fp.webgl = null;
    }

    // Audio fingerprint (simplificado)
    try {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const analyser = ctx.createAnalyser();
        osc.connect(analyser);
        osc.start(0);
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        fp.audio = Array.from(data.slice(0, 20));
        ctx.close();
    } catch {
        fp.audio = null;
    }

    return fp;
}

(async () => {
    const clientFP = await getFingerprint();
    const payload = {
        server: SERVER_DATA,
        client: clientFP,
        timestamp: new Date().toISOString()
    };

    document.getElementById("output").textContent =
        JSON.stringify(payload, null, 2);

    // Envío JSON al backend
    fetch("collect.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
})();
