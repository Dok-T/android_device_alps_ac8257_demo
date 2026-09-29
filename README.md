# LineageOS device tree – Jancar UJC201 (AC8257) — SQUELETTE

**Etat : non fonctionnel, en preparation.** Branche `lineage-18.1`.
L'arbre TWRP est sur la branche `main`.

Depots prevus :
- `android_device_alps_ac8257_demo` (ce depot) : arbre de l'appareil
- `android_vendor_alps_ac8257_demo` : blobs proprietaires (a creer, genere par `extract-files.sh`)
- noyau : prebuilt stock 4.9.117 (`prebuilt/`), config et DTS extraits dans `prebuilt/`

## Feuille de route
- [ ] Etape 0 : inventaire de la couche Jancar (paquets, services, /jancar, framework)
- [ ] Etape 1 : test GSI TrebleDroid (A11–A13) sur `system` seul, vendor stock
- [ ] Etape 2 : couche Jancar greffee (module Magisk) : son, MCU, veille, radio, camera
- [ ] Etape 3 : build LineageOS 18.1 (machine : ~300 Go disque, 32 Go RAM)

## Materiel (resume)
AC8257 (4x A53, PowerVR GE8300), eMMC 128 Go, 6 Go RAM, ecran MIPI 1280x720, tactile Goodix GT1x,
DSP BD37534, tuner TEF68xx, decodeurs AHD TP9963/TP2854, MCU sur /dev/ttyS1 (115200).
Bootloader deverrouille d'usine, dm-verity desactive, vbmeta flags=1.
