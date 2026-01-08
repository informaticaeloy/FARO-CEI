import os
import sys

# Añadir la ruta del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.fingerprint_matcher import comparar_fingerprints, cargar_fingerprints

if __name__ == "__main__":
    fps = cargar_fingerprints()
    print("[*] Cargando fingerprints...")

    for i in range(len(fps)):
        for j in range(i + 1, len(fps)):
            fp1 = fps[i]
            fp2 = fps[j]
            print(f"Comparando {os.path.basename(fp1)} vs {os.path.basename(fp2)}")
            resultado = comparar_fingerprints(fp1, fp2)
            print("Score      :", resultado["score"], "/ 100")
            print("Matches    :", resultado["matches"])
            print("Mismatches :", resultado["mismatches"])
            print("----------------------------------------")



# import sys
# import os
#
# # Añadir la ruta del proyecto al path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#
# from utils.fingerprint_matcher import comparar_fingerprints
# import json
# import glob
#
# fingerprints_folder = "data/fingerprints"
#
# print("[*] Cargando fingerprints...")
#
# files = glob.glob(f"{fingerprints_folder}/*.json")
# fingerprints = []
#
# for f in files:
#     with open(f, "r", encoding="utf-8") as fp_file:
#         data = json.load(fp_file)
#         fingerprints.append((f, data))
#
# print("[*] Inspeccionando estructura de fingerprints...\n")
#
# for fname, fp in fingerprints:
#     print(f"Archivo: {fname}")
#     # Imprime las claves principales
#     print("Claves top-level:", list(fp.keys()))
#
#     # Si existe engine fingerprintjs
#     if "engines" in fp and "fingerprintjs" in fp["engines"]:
#         fpjs_data = fp["engines"]["fingerprintjs"]["data"]
#         print("Claves dentro de data:", list(fpjs_data.keys()))
#
#         # Si existe components
#         if "components" in fpjs_data:
#             print("Claves dentro de components:", list(fpjs_data["components"].keys()))
#
#     print("\n" + "-" * 40 + "\n")
