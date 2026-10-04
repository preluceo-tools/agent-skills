#include <avr/io.h>
#include <util/delay.h>
int main(void) { DDRB |= 1; for (;;) { PINB = 1; _delay_ms(100); } }
