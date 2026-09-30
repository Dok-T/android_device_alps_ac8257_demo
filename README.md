# TWRP – Jancar UJC201 (Autochips AC8257, carte JAC_8258C)

Arbre TWRP (branche **twrp-12.1**) pour les autoradios Android « UJC201 » (SIXWIN, Podofo, Hikity…).
**Teste et fonctionnel** sur une unite SIXWIN, firmware `UJC201-V1.1.35R6-250718_0429` (noyau `4.9.117+ #25`).

| Fonction | Etat |
|---|---|
| Demarrage sans bootloop d'Android | OK (signature AVB du recovery stock) |
| Affichage | OK, paysage (rotation 90) |
| Tactile + touches du bandeau (power, home, back, vol+, vol-) | OK (`touchfix`) |
| Luminosite | OK (pilote inverse, corrige par `touchfix`) |
| ADB / MTP | OK (configfs, `musb-hdrc`) |
| Cle USB | OK sur le port hote (xhci) ; port OTG basculable (Advanced > USB: Host mode) |
| /data | OK (non chiffre sur ce firmware) |
| Barre d'etat | temperature CPU (mtktscpu) + tension d'entree (2 sondes ADC, a valider en voiture) |

## Installer
```
adb reboot bootloader
fastboot flash recovery twrp_ujc201.img
fastboot oem reboot-recovery
```
Retour au recovery stock : `fastboot flash recovery <recovery stock>.img`.
Faire d'abord une sauvegarde complete de l'eMMC (SP Flash Tool, Readback : `EMMC_BOOT_1` 0x0/0x400000,
`EMMC_USER` 0x0/0x1A0000000, fin de disque `EMMC_USER` 0x1D1A000000/0x4000000).

**Flasher `twrp_ujc201.img` (post-traite), jamais le `recovery.img` brut du build.**

## Build
GitHub Actions (`.github/workflows/build-twrp.yml`, lancement manuel) :
build TWRP puis `tools/ujc201_postprocess.py` → `twrp_ujc201.img`.

Localement, a partir d'un `recovery.img` deja construit :
```
python3 tools/ujc201_postprocess.py recovery.img twrp_ujc201.img \
    --avb prebuilt/avb/recovery_stock_vbmeta_250718.bin --overlay recovery/root
```

## Ce qu'on a appris (pieges de cette plateforme)

### 1. AVB : ne pas signer le recovery avec une cle de test
Le `vbmeta` stock chaine `recovery` (cle Jancar, rollback location 1). Avec une autre cle :
- le LK tolere (bootloader deverrouille) ;
- mais le **fs_mgr d'Android 9** refait `avb_slot_verify` au premier etage de `init` et ne tolere que
  `ERROR_VERIFICATION`, pas `PUBLIC_KEY_REJECTED` (result 5) → `Failed to mount required partitions early`
  → kernel panic → **bootloop d'Android** (visible dans la partition `expdb`).

Solution : `BOARD_AVB_ENABLE := false` et le post-traitement pose le **vbmeta du recovery stock** en footer
(`prebuilt/avb/`) : cle correcte, seul le hash differe → erreur de verification toleree.

### 2. Noyau : `skip_initramfs`
Le LK ajoute `skip_initramfs ro rootwait init=/init` hors mode recovery (system-as-root).
Le noyau prebuilt est patche `skip_initramfs` → `want_initramfs` (meme methode que Magisk).
`fastboot boot` ne permet pas de demarrer TWRP sur cette unite : il faut flasher `recovery`.

### 3. Ecran noir : jamais de FBIOBLANK
Au demarrage, minui fait `FBIOBLANK` (eteindre) puis `FBIOBLANK` (rallumer). Le pilote LCM Jancar lance a
l'extinction un kthread `jac_set_lcd_power_kthread` qui coupe l'alimentation de la dalle (GPIO 170/164)
~100 ms plus tard, donc **apres** le rallumage → dalle eteinte, retro-eclairage allume, `VSYNC timeout`.
`TW_SCREEN_BLANK_ON_BOOT` est proscrit et le post-traitement neutralise les `ioctl(FBIOBLANK)` de
`libminuitwrp.so`. La dalle est une MIPI 720x1280 (portrait) derriere un pont LVDS ; Android utilise
`persist.sf.hwrotation=90`.

### 4. Tactile (`tools/touchfix`)
`mtk-tpd` (Goodix, id 0911) annonce 720x1280 mais envoie des coordonnees paysage ~1024x600, X inverse
(X ≈ 1008 a gauche, 13 a droite ; Y 14 en haut, 590 en bas). Il ne remonte rien tant qu'il n'a pas recu
la notification « ecran allume » (ecriture de `0` dans `/sys/class/graphics/fb0/blank`, sans eteindre).
`touchfix` capture `mtk-tpd` (EVIOCGRAB) et reemet sur un peripherique uinput. TWRP (`ev_get`) met l'axe X a
l'echelle de la largeur affichee apres rotation : pas d'echange X/Y, seulement l'inversion de X.
Le bandeau gauche (X brut > 1030) porte les touches : power Y≈108, home 189, back 271, vol+ 355, vol- 430.

### 5. Luminosite
`/sys/class/leds/lcd-backlight` : `max_brightness = 0`, `min_brightness = 179` → echelle inversee.
TWRP ecrit dans `/tmp/twbl` (`TW_BRIGHTNESS_PATH`), `touchfix` convertit (`179 - v*179/255`).

### 6. USB
- Port OTG : `musb-hdrc` (seul UDC). Le gadget est en **configfs** : l'`init.recovery.usb.rc` legacy
  (`android_usb`) de TWRP ne marche pas → `recovery/root/init.recovery.usb.rc` (mtp.gs0 + ffs.adb).
- Bascule hote/peripherique : `dual_role_usb/dual-role-usb20/data_role` = `host` / `device`
  (`mode` ufp/dfp est ignore par le pilote MTK, `cmode` aussi). Script `usbmode`.
- Second port : `xhci-mtk` (11280000.usb), **hote uniquement** → adb impossible dessus, cle USB OK.

### 7. Sondes
- Temperature CPU : `thermal_zone1` (`mtktscpu`). `thermal_zone0` = `mtktsbattery` = -127000 (pas de batterie).
- Pas de `power_supply` (`ATC_DISABLE_BATTERY_CHARGER`). Tension d'entree : ADC SoC canal 4
  (`/sys/devices/virtual/mtk-adc-cali/mtk-adc-cali/AUXADC_read_channel`, 902 mV a 12,02 V, x13,33) et
  PMIC `VCDT` (`iio:device0/in_voltage2_VCDT_input`, 649 mV, x18,52). Les deux suivent une chute sous charge ;
  rapports a confirmer entre 12,5 V et 14 V.

## Fichiers
- `prebuilt/kernel` : noyau stock 250718 (#25) + patch `want_initramfs`
- `prebuilt/dtbo.img` : recovery_dtbo du recovery stock 250718
- `prebuilt/avb/recovery_stock_vbmeta_250718.bin` : vbmeta (footer) du recovery stock
- `recovery/root/` : rc, `touchfix`, `usbmode`, `powerinfo`
- `tools/touchfix/` : source de `touchfix` (C autonome, sans libc) + `build.sh`
- `tools/ujc201_postprocess.py` : post-traitement de l'image

## Securite
Ne jamais restaurer la partition « Preloader » depuis TWRP. Garder le recovery stock pour les mises a jour.
Ne pas publier ses propres partitions `nvram`, `nvdata`, `proinfo`, `persist`, `metazone` (identifiants,
certificat CarPlay).
