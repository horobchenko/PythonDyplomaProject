/*
 * oled.c
 *
 *  Created on: Mar 31, 2025
 *      Author: gorob
 */

#include "oled.h"

extern SPI_HandleTypeDef hspi1;
/* Private variable */

static SSD1306_t SSD1306;//SSD1306_t structure instance
static uint8_t SSD1306_Buffer[SSD1306_WIDTH * SSD1306_HEIGHT / 8] = {};//SSD1306 data buffer

void SSD1306_WriteCmd(uint8_t command)
{
	SSD1306_CMD_MODE();
    HAL_SPI_Transmit_IT(&hspi1, &command, sizeof(command));

}

void SSD1306_WriteData(uint8_t data)
{
	SSD1306_DATA_MODE();
	HAL_SPI_Transmit_IT(&hspi1, &data, sizeof(data));
}


uint8_t SSD1306_Init(void){

	/* Power ON sequence with External VCC  */

	SSD1306_LOGIC_ON();//Power ON VDD
	SSD1306_RESET_LOW();//After VDD become stable, set RES# pin LOW (logic low) for at least 3us (t1)
	HAL_Delay(3);//3us (t1)
	SSD1306_RESET_HIGH();//and then HIGH (logic //high).
	SSD1306_RESET_LOW();//After set RES# pin LOW (logic low), wait for at least 3us (t2). Then Power ON VCC.
	HAL_Delay(3);//3us (t2)
	SSD1306_DISPLAY_ON();//Then Power ON VCC

	/* Display regulation commands */

	SSD1306_WriteCmd(DISPLAY_ON);//After VCC become stable, send command AFh for display ON. SEG/COM will be ON after 100ms (tAF).
	SSD1306_WriteCmd(ADDR_MODE_MEM);
	SSD1306_WriteCmd(ADDR_MODE_HORZ);
	SSD1306_WriteCmd(ADDR_MODE_PAGE);
	SSD1306_WriteCmd(ADDR_MODE_VERT);
	SSD1306_WriteCmd(ADDR_START_PAGE);
	SSD1306_WriteCmd(SCAN_NORMAL_DIR);
	SSD1306_WriteCmd(ADDR_START_LINE);
	SSD1306_WriteCmd(CONTRAST_DISPLAY);
	SSD1306_WriteCmd(SEG_REMAP);
	SSD1306_WriteCmd(NORMAL_DISPLAY);
	SSD1306_WriteCmd(DISPLAY_OFFSET);
	SSD1306_WriteCmd(COM_HW_CONFIG);
	SSD1306_WriteCmd(SCROLL_DISABLE);

	/* Clear screen */
	SSD1306_ClearScreen(SSD1306_COLOR_BLACK);

	/* Update screen */
	SSD1306_UpdateScreen();

    /* Set SSD1306 values*/
	SSD1306.CurrentX = 0;
	SSD1306.CurrentY = 0;
	SSD1306.Initialized = 1;

	return 1;

}

uint8_t SSD1306_DeInit(){

	/* Check if display is in initialized */
		if (!SSD1306.Initialized)
		{
			return;
		}

		/*Power OFF sequence with External VCC*/

		/* Display off register command and stop display pin current*/
		SSD1306_WriteCmd(DISPLAY_OFF);//Send command AEh for display OFF.
		SSD1306_DISPLAY_OFF();//Power OFF VCC.

		/* 100 ms delay */
		HAL_Delay(100);

		/*Stop logic pin current*/
		SSD1306_LOGIC_OFF();//Power OFF VDD after tOFF.  (Typical tOFF=100ms)


		/* Set SSD1306value */
		SSD1306.Initialized = 0;

		return 1;
}

void SSD1306_ResetDisplay(){

	SSD1306_RESET_ON();
	HAL_Delay(1);
	SSD1306_RESET_OFF();

}

void SSD1306_UpdateScreen(){

	SSD1306_WriteData(SSD1306_Buffer);
}

SSD1306_ClearScreen(SSD1306_COLOR_t color){
	memset(SSD1306_Buffer, (color == SSD1306_COLOR_BLACK) ? 0x00 : 0xFF, sizeof(SSD1306_Buffer));
}

void SSD1306_WrightPixel(uint16_t x, uint16_t y, SSD1306_COLOR_t color){
	if (
		x >= SSD1306_WIDTH ||
		y >= SSD1306_HEIGHT
	) {
		/* Error */
		return;
	}

	/* Check if pixels are inverted */
	if (SSD1306.Inverted) {
		color = (SSD1306_COLOR_t)!color;
	}

	/* Set color */
	if (color == SSD1306_COLOR_WHITE) {
		SSD1306_Buffer[x + (y / 8) * SSD1306_WIDTH] |= 1 << (y % 8);
	} else {
		SSD1306_Buffer[x + (y / 8) * SSD1306_WIDTH] &= ~(1 << (y % 8));
	}
}

void SSD1306_GotoXY(uint16_t x, uint16_t y){

		SSD1306.CurrentX = x;
		SSD1306.CurrentY = y;
}

char SSD1306_WrightChar(char ch, FontDef_t* Font, SSD1306_COLOR_t color){
	uint32_t i, b, j;

		/* Check if display is available */
		if (
			SSD1306_WIDTH <= (SSD1306.CurrentX + Font->FontWidth) ||
			SSD1306_HEIGHT <= (SSD1306.CurrentY + Font->FontHeight)
		) {
			/* Error */
			return 0;
		}

		/* Go through font starting with 32 smbl*/
		for (i = 0; i < Font->FontHeight; i++) {
			b = Font->data[(ch - 32) * Font->FontHeight + i];
			for (j = 0; j < Font->FontWidth; j++) {
				if ((b << j) & 0x8000) {
					SSD1306_WrightPixel(SSD1306.CurrentX + j, (SSD1306.CurrentY + i), (SSD1306_COLOR_t) color);
				} else {
					SSD1306_WrightPixel(SSD1306.CurrentX + j, (SSD1306.CurrentY + i), (SSD1306_COLOR_t)!color);
				}
			}
		}
		SSD1306.CurrentX += Font->FontWidth;
		return ch;
}

char SSD1306_WrightString(char *str, FontDef_t *Font, SSD1306_COLOR_t color){
		while (*str) {
			if (SSD1306_WrightChar(*str, Font, color) != *str) {
				break;
			}

			str++;
		}

		return *str;
}


