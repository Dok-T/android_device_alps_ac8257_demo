# TWRP device tree – Jancar UJC201 (AC8257, carte JAC_8258C)

Arbre genere avec twrpdtgen a partir du recovery stock `UJC201-V1.1.04R1-240907`,
puis adapte a la main (branche TWRP : **twrp-12.1**).

- SoC : Autochips AC8257 (vu comme MT6761), noyau 4.9 arm64, noyau prebuilt stock (Image.gz-dtb)
- Boot image header v1, recovery_dtbo inclus, system-as-root, pas d'A/B
- Ecran MIPI 1280x720 (paysage), tactile Goodix GT1x, densite 160
- Bootloader deverrouille d'usine (ATC_DEFAULT_UNLOCK=yes), dm-verity coupe

## Build (GitHub Actions, template azwhikaru/Action-TWRP-Builder)
- MANIFEST_URL : https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp
- MANIFEST_BRANCH : twrp-12.1
- DEVICE_PATH : device/alps/ac8257_demo
- DEVICE_NAME : ac8257_demo
- MAKEFILE_NAME : twrp_ac8257_demo
- BUILD_TARGET : recovery

## Reglages a ajuster apres le premier test
- Image tournee : decommenter `TW_ROTATION` (90 ou 270) dans BoardConfig.mk
- Couleurs inversees : `TARGET_RECOVERY_PIXEL_FORMAT := "RGBX_8888"` (ou BGRA_8888)
- Luminosite : verifier `/sys/class/leds/lcd-backlight/brightness`

## Securite
Garder le recovery stock : les mises a jour ATCUPG passent par lui.
Ne jamais restaurer la partition "Preloader" depuis TWRP.

## AVB (vbmeta stock analyse)
- flags = 1 : dm-verity deja desactive, verification des signatures active
- `recovery` et `system` sont en *chain partition* (cle Jancar), `recovery` sur rollback location 1
- `boot` et `dtbo` en hash, `vendor` en hashtree
- Le TWRP est signe avec la cle de test AVB : accepte car le bootloader est deverrouille
  (meme mecanisme que le boot Magisk). Si le recovery est refuse au demarrage,
  flasher `vbmeta_disabled.img` (flags = 3) sur la partition vbmeta, en gardant le vbmeta stock.
