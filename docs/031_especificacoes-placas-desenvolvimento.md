# Especificações das placas de desenvolvimento

Este documento resume as características físicas dos microcontroladores das três placas de desenvolvimento usadas no projeto BALAS.

| Placa de desenvolvimento | Microcontrolador | Núcleo Arm Cortex | Frequência de operação | RAM interna | Flash interna |
| --- | --- | --- | ---: | ---: | ---: |
| NXP FRDM-MCXN947 | NXP MCXN947 | 2x Arm Cortex-M33 | Até 150 MHz por núcleo | 512 KB de SRAM | 2 MB |
| ST NUCLEO-H723ZG | ST STM32H723ZG | Arm Cortex-M7 | Até 550 MHz | 564 KB | 1 MB |
| Nordic nRF52840 DK (PCA10056) | Nordic nRF52840 | Arm Cortex-M4 com FPU (Cortex-M4F) | 64 MHz | 256 KB | 1 MB |

## Observações

- Na MCXN947, aproximadamente 416 KB da SRAM permanecem disponíveis quando o ECC completo está habilitado.
- O STM32H723ZG suporta até 550 MHz, mas o firmware STM32 atualmente registrado no projeto BALAS está configurado para 520 MHz.
- Os valores de RAM e Flash da tabela representam a capacidade física interna dos microcontroladores, não o consumo atual do firmware nem apenas as regiões disponibilizadas pelos respectivos linkers.

## Fontes oficiais

- NXP, FRDM-MCXN947: <https://www.nxp.com/design/design-center/development-boards-and-designs/FRDM-MCXN947>
- STMicroelectronics, STM32H723ZG: <https://www.st.com/en/microcontrollers-microprocessors/stm32h723zg>
- Nordic Semiconductor, nRF52840 DK: <https://www.nordicsemi.com/Products/Development-hardware/nRF52840-DK>
