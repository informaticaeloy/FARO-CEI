//static/fingerprint/orchestrator.js
(async () => {

  async function loadProfiles() {
    const res = await fetch('/static/fingerprint/profiles.json');
    return await res.json();
  }

  async function loadEngineAdapter(engine) {
    return await import(`/static/fingerprint/engines/${engine}/adapter.js`);
  }

  function getActiveProfile(profiles, forcedProfile = null) {
    return forcedProfile || profiles.default;
  }

  async function runFingerprint(profileName = null) {
    const profilesData = await loadProfiles();
    const profileKey = getActiveProfile(profilesData, profileName);
    const profile = profilesData.profiles[profileKey];

    const results = {};
    const metadata = {
      profile: profileKey,
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent
    };

    for (const [engine, enabled] of Object.entries(profile.engines)) {
      if (!enabled) {
        results[engine] = null;
        continue;
      }

      try {
        const adapter = await loadEngineAdapter(engine);
        results[engine] = await adapter.run();
      } catch (e) {
        results[engine] = {
          error: true,
          message: e.toString()
        };
      }
    }

///////////////////////////////////////////////////////// ULTIMO AÑADIDO
// construir payload y mostrarlo en consola antes de enviar
const payload = {
  baliza_id: window.BALIZA_ID,
  timestamp: new Date().toISOString(),
  fingerprint: {
    metadata: {
      ...metadata,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      screen: `${screen.width}x${screen.height}`,
      platform: navigator.platform
    },
    engines: results
  }
};

console.log("[DEBUG] Enviando fingerprint al backend:", payload);

const fpResp = await fetch("/webhook/fingerprint", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});

const fpData = await fpResp.json();
if (fpData.fp_id) {
    // Registrar evento en baliza
    await fetch("/balizas/event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            origen: window.BALIZA_ID,
            fingerprint_id: fpData.fp_id,
            tipo: "HTML",
            evento: "VIEW"
        })
    });
}

///////////////////////////////////////////////////////// FIN ULTIMO AÑADIDO

    return {
      metadata,
      engines: results,
      hash_strategy: profile.hash_strategy
    };
  }

  // Exponer de forma controlada
  window.runFingerprint = runFingerprint;

})();

