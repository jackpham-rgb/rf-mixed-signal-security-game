/* STM32G431CBU6 implementation of the HAL for the ASCAM-1 board.
 *
 * Pins (see hardware/kicad/NETLIST.md):
 *   PA0  TRIG      GPIO output to SMA J2
 *   PA2  USART2_TX AF7  -> J6 (115200 8N1, clocked from HSI16 so clock hops do not change the baud rate)
 *   PA3  USART2_RX AF7  <- J6
 *   PA6  DRV0      TIM16_CH1 AF1, 250 kHz carrier for branch 0
 *   PA8  MCO       AF0, SYSCLK out: carrier for branch 1, and the XOR doubler for branch 2
 *   PB0  DRV3      TIM3_CH3 AF2, about 6 MHz carrier for branch 3
 *   PB4-PB7 EN0-EN3  GPIO outputs, written by DMA from a buffer (random gating)
 *
 * Clocks: HSE 8 MHz -> PLL (M = 2, R = 6) -> SYSCLK 32 MHz (N = 48) or 24 MHz (N = 36).
 * Gating: TIM6 update at 1 MHz requests DMA1 channel 1 (DMAMUX request 8 = TIM6_UP),
 * which copies one 32-bit word per microsecond into GPIOB->BSRR.
 *
 * Alternate-function numbers follow the STM32G431 datasheet (DS12589) pin table.
 * Check them against the datasheet before the first power-up.
 */
#include "stm32g4xx.h"
#include "hal.h"

#define HSE_HZ 8000000u
#define DMAMUX_REQ_TIM6_UP 8u   /* from ST's LL driver: LL_DMAMUX_REQ_TIM6_UP */
#define USART_BAUD 115200u
#define HSI_HZ 16000000u

static uint8_t sys_mhz;

/* CMSIS startup calls SystemInit before main: enable the FPU only. */
void SystemInit(void)
{
    SCB->CPACR |= (3UL << (10 * 2)) | (3UL << (11 * 2));
}

static void gpio_mode(GPIO_TypeDef *g, unsigned pin, unsigned mode, unsigned af)
{
    g->MODER = (g->MODER & ~(3u << (2 * pin))) | (mode << (2 * pin));
    g->OSPEEDR |= 3u << (2 * pin);                        /* very high speed */
    if (mode == 2u) {
        volatile uint32_t *afr = &g->AFR[pin >> 3];
        unsigned sh = 4u * (pin & 7u);
        *afr = (*afr & ~(0xFu << sh)) | (af << sh);
    }
}

static void timers_retune(void)
{
    uint32_t f = (uint32_t)sys_mhz * 1000000u;
    /* TIM16 CH1: 250 kHz, 50% duty (branch 0) */
    TIM16->ARR = f / 250000u - 1u;
    TIM16->CCR1 = (TIM16->ARR + 1u) / 2u;
    /* TIM3 CH3: about 6 MHz (6.4 MHz at 32 MHz, 6.0 MHz at 24 MHz), 50% duty (branch 3) */
    uint32_t div = (f + 3000000u) / 6000000u;
    TIM3->ARR = div - 1u;
    TIM3->CCR3 = div / 2u;
    /* TIM6: 1 MHz update events for the gating DMA */
    TIM6->ARR = f / 1000000u - 1u;
    TIM16->EGR = TIM_EGR_UG;
    TIM3->EGR = TIM_EGR_UG;
    TIM6->EGR = TIM_EGR_UG;
}

static void pll_config(uint8_t mhz)
{
    uint32_t n = (mhz == 24u) ? 36u : 48u;               /* VCO = 4 MHz x N; SYSCLK = VCO / 6 */
    RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSE
                 | ((2u - 1u) << RCC_PLLCFGR_PLLM_Pos)
                 | (n << RCC_PLLCFGR_PLLN_Pos)
                 | (2u << RCC_PLLCFGR_PLLR_Pos)          /* PLLR = /6 */
                 | RCC_PLLCFGR_PLLREN;
}

static int switch_sysclk(uint32_t sw)
{
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | sw;
    for (uint32_t t = 0; t < 1000000u; t++)
        if ((RCC->CFGR & RCC_CFGR_SWS) == (sw << RCC_CFGR_SWS_Pos)) return 0;
    return -1;
}

int hal_set_clock_mhz(uint8_t mhz)
{
    if (mhz != 24u && mhz != 32u) return -1;
    /* run from HSE while the PLL is reprogrammed */
    if (switch_sysclk(RCC_CFGR_SW_HSE)) return -1;
    RCC->CR &= ~RCC_CR_PLLON;
    while (RCC->CR & RCC_CR_PLLRDY) {}
    pll_config(mhz);
    RCC->CR |= RCC_CR_PLLON;
    for (uint32_t t = 0; !(RCC->CR & RCC_CR_PLLRDY); t++)
        if (t > 1000000u) return -1;
    if (switch_sysclk(RCC_CFGR_SW_PLL)) return -1;
    sys_mhz = mhz;
    timers_retune();
    return 0;
}

uint8_t hal_clock_mhz(void) { return sys_mhz; }

void hal_init(void)
{
    /* HSE on, 1 flash wait state (enough up to 32 MHz), caches and prefetch on */
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY)) {}
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_1WS
               | FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN;
    /* HSI16 for the UART, so its baud rate is independent of the clock hop */
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY)) {}

    RCC->AHB1ENR |= RCC_AHB1ENR_DMA1EN | RCC_AHB1ENR_DMAMUX1EN;
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN;
    RCC->APB1ENR1 |= RCC_APB1ENR1_TIM3EN | RCC_APB1ENR1_TIM6EN | RCC_APB1ENR1_USART2EN;
    RCC->APB2ENR |= RCC_APB2ENR_TIM16EN;
    (void)RCC->APB2ENR;

    /* pins */
    gpio_mode(GPIOA, 0, 1, 0);                           /* TRIG */
    GPIOA->BSRR = 1u << (0 + 16);
    gpio_mode(GPIOA, 2, 2, 7);                           /* USART2_TX */
    gpio_mode(GPIOA, 3, 2, 7);                           /* USART2_RX */
    gpio_mode(GPIOA, 6, 2, 1);                           /* TIM16_CH1 */
    gpio_mode(GPIOA, 8, 2, 0);                           /* MCO */
    gpio_mode(GPIOB, 0, 2, 2);                           /* TIM3_CH3 */
    GPIOB->BSRR = 0xFu << (4 + 16);                      /* EN0..EN3 low before they become outputs */
    for (unsigned p = 4; p <= 7; p++) gpio_mode(GPIOB, p, 1, 0);

    /* MCO = SYSCLK / 1 */
    RCC->CFGR = (RCC->CFGR & ~(RCC_CFGR_MCOSEL | RCC_CFGR_MCOPRE)) | (1u << RCC_CFGR_MCOSEL_Pos);

    /* TIM16 CH1 PWM mode 1 (needs MOE), TIM3 CH3 PWM mode 1 */
    TIM16->CCMR1 = (6u << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE;
    TIM16->CCER = TIM_CCER_CC1E;
    TIM16->BDTR = TIM_BDTR_MOE;
    TIM16->CR1 = TIM_CR1_ARPE;
    TIM3->CCMR2 = (6u << TIM_CCMR2_OC3M_Pos) | TIM_CCMR2_OC3PE;
    TIM3->CCER = TIM_CCER_CC3E;
    TIM3->CR1 = TIM_CR1_ARPE;
    TIM6->DIER = TIM_DIER_UDE;

    /* DMA1 channel 1 <- DMAMUX channel 0 <- TIM6 update; memory to GPIOB->BSRR, 32-bit */
    DMAMUX1_Channel0->CCR = DMAMUX_REQ_TIM6_UP;
    DMA1_Channel1->CPAR = (uint32_t)&GPIOB->BSRR;
    DMA1_Channel1->CCR = DMA_CCR_DIR | DMA_CCR_MINC | (2u << DMA_CCR_MSIZE_Pos) | (2u << DMA_CCR_PSIZE_Pos);

    /* USART2: HSI16, 115200 8N1 */
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_USART2SEL) | (2u << RCC_CCIPR_USART2SEL_Pos);
    USART2->BRR = (HSI_HZ + USART_BAUD / 2u) / USART_BAUD;
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;

    /* cycle counter for microsecond delays */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    sys_mhz = 0;
    if (hal_set_clock_mhz(32) != 0) {
        for (;;) {}                                      /* no HSE or PLL lock: stop here */
    }
    TIM16->CR1 |= TIM_CR1_CEN;
    TIM3->CR1 |= TIM_CR1_CEN;
}

void hal_trigger(int high) { GPIOA->BSRR = high ? 1u : (1u << 16); }

void hal_gating_start(const uint32_t *words, uint16_t n)
{
    DMA1_Channel1->CCR &= ~DMA_CCR_EN;
    DMA1_Channel1->CMAR = (uint32_t)words;
    DMA1_Channel1->CNDTR = n;
    DMA1->IFCR = DMA_IFCR_CGIF1;
    DMA1_Channel1->CCR |= DMA_CCR_EN;
    TIM6->CNT = 0;
    TIM6->CR1 |= TIM_CR1_CEN;
}

void hal_gating_stop(void)
{
    TIM6->CR1 &= ~TIM_CR1_CEN;
    DMA1_Channel1->CCR &= ~DMA_CCR_EN;
    GPIOB->BSRR = 0xFu << (4 + 16);                      /* all branches off between traces */
}

void hal_delay_us(uint32_t us)
{
    uint32_t start = DWT->CYCCNT, cycles = us * sys_mhz;
    while ((DWT->CYCCNT - start) < cycles) {}
}

int hal_uart_getc(void)
{
    if (USART2->ISR & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE))
        USART2->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NECF;
    if (USART2->ISR & USART_ISR_RXNE_RXFNE) return (int)(USART2->RDR & 0xFFu);
    return -1;
}

void hal_uart_puts(const char *s)
{
    for (; *s; s++) {
        if (*s == '\n') {
            while (!(USART2->ISR & USART_ISR_TXE_TXFNF)) {}
            USART2->TDR = '\r';
        }
        while (!(USART2->ISR & USART_ISR_TXE_TXFNF)) {}
        USART2->TDR = (uint8_t)*s;
    }
}
