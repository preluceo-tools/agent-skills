#include <avr/io.h>
#include <avr/interrupt.h>
ISR(TIMER0_OVF_vect) { PORTF.OUTTGL = PIN5_bm; }
int main(void) { PORTF.DIRSET = PIN5_bm; sei(); for (;;) { } }
