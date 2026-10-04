#include <avr/io.h>
int main(void) { DDRB |= 1; for (;;) { PORTB ^= 1; } }
