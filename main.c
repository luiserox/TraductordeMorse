/* ###################################################################
**     Filename    : main.c
**     Project     : ProyectoB2
**     Processor   : MC9S08QE128CLK
**     Version     : Driver 01.12
**     Compiler    : CodeWarrior HCS08 C Compiler
**     Date/Time   : 2019-06-14, 12:04, # CodeGen: 0
**     Abstract    :
**         Main module.
**         This module contains user's application code.
**     Settings    :
**     Contents    :
**         No public methods
**
** ###################################################################*/
/*!
** @file main.c
** @version 01.12
** @brief
**         Main module.
**         This module contains user's application code.
*/         
/*!
**  @addtogroup main_module main module documentation
**  @{
*/         
/* MODULE main */


/* Including needed modules to compile this module/procedure */
#include "Cpu.h"
#include "Events.h"
#include "TI1.h"
#include "AD1.h"
#include "AS1.h"
#include "TimerBoton.h"
#include "LED.h"
#include "BotonFilt.h"
#include "Digi1.h"
#include "Digi2.h"
#include "PruebaFilt.h"
/* Include shared modules, which are used for whole project */
#include "PE_Types.h"
#include "PE_Error.h"
#include "PE_Const.h"
#include "IO_Map.h"

/* User includes (#include below this line is not maintained by Processor Expert) */

char flag = 0;
char filt=1;

char orden = 28;

void main(void){	
/* Write your local variable definition here */
	char a[29]={0,1,0,-1,0,3,0,-6,0,12,0,-24,0,80,127,80,0,-24,0,12,0,-6,0,3,0,-1,0,1,0};
	char x[29]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
	char size=3;
	unsigned int send=3;
	char	analog, j=0, k=0, cd1=0,cd2=0;
	char 	error = 0;
	char datos[3];
	char contador=orden+1;
	unsigned int filtout;
	int entradas;

  /*** Processor Expert internal initialization. DON'T REMOVE THIS CODE!!! ***/
  PE_low_level_init();
  /*** End of Processor Expert internal initialization.                    ***/

  /* Write your code here */
	TimerBoton_DisableEvent();
	BotonFilt_EnableEvent();
  
	while(1){
		if(flag){
		flag = 0;
		do {error = AD1_Measure(1);} while(error != ERR_OK);
		do {error = AD1_GetValue(&analog);} while(error != ERR_OK);
		if(!Digi1_GetVal())
			cd1 = 0b01000000;
		else cd1 = 0;
		if(!Digi2_GetVal())
			cd2 = 0b01000000;
		else cd2 = 0;
		
		if(filt){
			contador--;
			if(contador==255){ 
				contador = orden;
			}
			x[contador]=analog;
			filtout = 0;
			entradas = 0;
			for(j=0;j<=orden;j++){
				k=(j+contador);
				if(k>orden){k-=(orden+1);}
				if(a[j]>127)filtout -= ((a[j]^255)+1)*x[k];
				else filtout += x[k]*a[j];
//				entradas += x[k];
			}
//			if(filtout>64000 && entradas<(125*orden))filtout=0;
//			if(filtout<1000 && entradas>(200*orden))filtout=65025;
			datos[0] = cd1 |((filtout>>10) & 63);
			datos[1] = 0b10000000 | cd2 |((filtout & 0b0000001111110000)>>4);
			datos[2] = 0b11000000 |(filtout & 0b0000000000001111);
		}
		else{
			datos[0] = cd1 |((analog)>>2);
			datos[1] = 0b10000000 | cd2 |((analog & 0b00000011));
			datos[2] = 0b10000000;
		}
		do {error = AS1_SendBlock(datos,size,&send);} while(error != ERR_OK);	
		PruebaFilt_NegVal();
	  }
  }

  /*** Don't write any code pass this line, or it will be deleted during code generation. ***/
  /*** RTOS startup code. Macro PEX_RTOS_START is defined by the RTOS component. DON'T MODIFY THIS CODE!!! ***/
  #ifdef PEX_RTOS_START
    PEX_RTOS_START();                  /* Startup of the selected RTOS. Macro is defined by the RTOS component. */
  #endif
  /*** End of RTOS startup code.  ***/
  /*** Processor Expert end of main routine. DON'T MODIFY THIS CODE!!! ***/
  for(;;){}
  /*** Processor Expert end of main routine. DON'T WRITE CODE BELOW!!! ***/
} /*** End of main routine. DO NOT MODIFY THIS TEXT!!! ***/

/* END main */
/*!
** @}
*/
/*
** ###################################################################
**
**     This file was created by Processor Expert 10.3 [05.09]
**     for the Freescale HCS08 series of microcontrollers.
**
** ###################################################################
*/

