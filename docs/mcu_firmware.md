# Firmware MCU Jancar (`/vendor/data/mcu/JCST_AC8257_8T7/jacmcu.bin`)

Version `JCST_AC8257_8T7-2024.08.09_12:59`, 17 296 octets, MCU HK32C030C8T7 (Cortex-M0, compatible STM32F030).
Analyse statique (capstone, `tools/mcu/`) : `JACMCU=jacmcu.bin python3 tools/mcu/mdis.py <adresse> [n]`.
Le firmware n'est pas dans le depot (fichier constructeur).

## Image
- En-tete de 16 octets (`JCST_AC8257_8T7 `) retire, puis table des vecteurs : application chargee en **0x08002400**
  (bootloader de mise a jour en dessous ; pas de VTOR sur M0 -> table recopiee en SRAM).
- Compilee avec Keil (SPL ST-like) ; `switch` via `__ARM_common_switch8` (0x080065AE).
- SysTick = SystemCoreClock / 10 000 (100 us). IWDG interne active (0x5555 / 0xAAAA).

## Peripheriques
| Bloc | Usage |
|---|---|
| USART2 (PA2/PA3) | lien SoC, 115200 8N1 (`/dev/ttyS1` cote AC8257) |
| USART1 (PA9/PA10) | boitier CAN (decodeur), vitesse dans la config ; passerelle trame `0x10` dans les deux sens |
| ADC + DMA ch1 | 7 voies en continu : CH1 PA1, CH4 PA4, CH5 PA5, CH6 PA6, CH7 PA7, CH8 PB0, CH9 PB1 ; conversion 8 bits (>>4) |
| TIM1 / TIM3 / TIM17 | PWM (PA8 AF2, PB1 AF1, PB7 AF2, PB14/PB15 AF2) : LED RGB des touches |
| RTC | horloge du MCU (trame `0x09`) |
| EXTI 4-15 | entrees de reveil (telecommande IR / ACC) |

## Trames SoC -> MCU (dispatcher 0x08003164 ; chaque trame est acquittee par `C0 <cmd> ...`)
| Cmd | Effet |
|---|---|
| `01 xx` | extinction (xx 3..5) |
| `08 xx` | mute (sortie PA0) |
| `09 00 aa mm jj` / `09 01 h m s` | reglage date / heure (RTC) |
| `0E` | reset du SoC (envoie l'octet brut `0xAB`) |
| `0F ss ...` | configuration, sous-commandes 0..11 ; `0F 04 panneau R G B mode` = LED ; `0F 0A` / `0F 0B` = tensions de coupure |
| `10 ...` | octets recopies tels quels sur USART1 (boitier CAN) |
| `11 xx` / `21 xx` | mode apprentissage des touches |
| `1F 01` | PC_READY : etat d'alimentation -> 1 (SoC pret) |
| `43 xx` / `44 xx` | alimentation radio (PF6) / ampli externe |
| `80` ... | mise a jour du firmware MCU |
| `F0 qq 00` | requete, voir ci-dessous |
| `F1 xx` | delai de mise en veille |

## Requetes `F0 qq 00` (0x080033C4)
| qq | Reponse |
|---|---|
| `00` | `00` ACC |
| `04` | `04` frein a main |
| `08` | `08` etat mute (PA0) |
| `09` | `09` date + heure |
| `0A` | `0A` version |
| `0B` | `0B` feux (ILL) |
| `0D` | `0D` etat sortie PA15 |
| `0F 07` | `0F 07` + octet de config |
| `43` | `43` alimentation radio (PF6) |

## Trames MCU -> SoC
`00` ACC, `04` frein a main, `09` date/heure, `0A` version, `0B` feux, `10` donnees du boitier CAN,
`20` touche (`30` en apprentissage) : `[canal, valeur, FF, FF, FF]`, canal 5/6 = volant, `C0` acquittement.
**Aucune trame ne transporte la tension batterie** : le MCU la mesure (ADC voie 0, PA1, 8 bits) et la compare
seulement au seuil de coupure de sa configuration (30 mesures au-dessus du seuil -> ACC envoye a 0, extinction).

## Consequences pour TWRP
- Etat des feux disponible des le demarrage : requete `F0 0B 00` (ajoutee a `touchfix`).
- Touches au volant : sur un vehicule equipe d'un boitier CAN, elles arrivent en trames `0x10` (protocole du
  boitier, decode par l'appli canbus Android), pas en `0x20`.
- Tension batterie : pas lisible via le protocole ; rester sur les ADC du SoC (calibration a faire en voiture).
