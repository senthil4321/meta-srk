/*
 * PRU Blink Example
 * Blinks USER LED3 (GPIO1_24) on BeagleBone Black using PRU0
 * This demonstrates PRU is working by toggling a GPIO pin
 */

#include <stdint.h>
#include <pru_cfg.h>
#include <pru_ctrl.h>

/* GPIO registers */
#define GPIO1_BASE 0x4804C000
#define GPIO_CLEARDATAOUT 0x190
#define GPIO_SETDATAOUT   0x194

/* User LED3 is GPIO1_24 */
#define LED_PIN (1 << 24)

/* Simple delay function */
void delay(uint32_t cycles) {
    volatile uint32_t i;
    for (i = 0; i < cycles; i++);
}

void main(void) {
    volatile uint32_t *gpio_clear = (volatile uint32_t *)(GPIO1_BASE + GPIO_CLEARDATAOUT);
    volatile uint32_t *gpio_set = (volatile uint32_t *)(GPIO1_BASE + GPIO_SETDATAOUT);
    
    /* Enable OCP master port for PRU to access memory */
    CT_CFG.SYSCFG_bit.STANDBY_INIT = 0;
    
    /* Blink LED forever */
    while (1) {
        /* Turn LED on */
        *gpio_set = LED_PIN;
        delay(10000000);  /* Delay ~0.5 second at 200MHz */
        
        /* Turn LED off */
        *gpio_clear = LED_PIN;
        delay(10000000);  /* Delay ~0.5 second */
    }
    
    /* Halt PRU */
    __halt();
}
