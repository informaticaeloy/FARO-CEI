import FingerprintJS from "./fingerprintjs.min.js";

export async function run() {
  // Inicializar FingerprintJS
  const fp = await FingerprintJS.load({ monitoring: false });
  const result = await fp.get();

console.log("[DEBUG] Datos obtenidos por adapter:", result);

  return {
    engine: "fingerprintjs",
    version: "v5",
    confidence: 0.85,
    data: {
      visitorId: result.visitorId,
      components: result.components
    },
    entropy: {
      bits: Object.keys(result.components || {}).length * 2,
      signals: Object.keys(result.components || {}).length
    }
  };
}

