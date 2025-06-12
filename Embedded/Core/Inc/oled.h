/*
 * oled.h
 *
 *  Created on: Mar 31, 2025
 *      Author: gorob
 */

#ifndef INC_OLED_H_
#define INC_OLED_H_
#include "stm32f7xx_hal.h"
#include "stm32f7xx_hal_gpio.h"
#include "stm32f7xx_hal_spi.h"

#include "fonts.h"

#include "stdlib.h"
#include "string.h"

/* C++ detection */
#ifdef __cplusplus
extern C
{
#endif

  /**
 * SSD1306 driver library  for SPI
 *
 *Правильные пины поставить
 *
 *
 *
/*
* General macro
*/
/* Private SSD1306 structure */
typedef struct {
	uint16_t CurrentX;
	uint16_t CurrentY;
	uint8_t Inverted;
	uint8_t Initialized;
} SSD1306_t;

/* Absolute value */
#define ABS(x)   ((x) > 0 ? (x) : -(x))

#define SSD1306_SPI_TIMEOUT 1000

/* Display width in pixels */
#define SSD1306_WIDTH 128

/* Display height in pixels */
#define SSD1306_HEIGHT 64

/* Display pages number*/
#define SSD1306_PAGES SSD1306_HEIGHT / 8

/* Pixel color enum*/
typedef enum {
	SSD1306_COLOR_BLACK = 0x00, /* Empty pixel */
	SSD1306_COLOR_WHITE = 0x01  /* Set pixel */
} SSD1306_COLOR_t;

/*
* Configuration pins control macro
*/
/*Switch data/command  mode  for transition */
#define SSD1306_CMD_MODE() HAL_GPIO_WritePin(GPIOF, GPIO_PIN_6, GPIO_PIN_RESET)
#define SSD1306_DATA_MODE() HAL_GPIO_WritePin(GPIOF, GPIO_PIN_6, GPIO_PIN_SET)

/* On/off reset current */
#define SSD1306_RESET_LOW() HAL_GPIO_WritePin(GPIOF, GPIO_PIN_7, GPIO_PIN_SET)
#define SSD1306_RESET_HIGH() HAL_GPIO_WritePin(GPIOF, GPIO_PIN_7, GPIO_PIN_RESET)

/* On/off display current */
#define SSD1306_DISPLAY_ON() HAL_GPIO_WritePin(GPIOC, GPIO_PIN_6, GPIO_PIN_RESET)
#define SSD1306_DISPLAY_OFF() HAL_GPIO_WritePin(GPIOC, GPIO_PIN_6, GPIO_PIN_SET)

/* On/off logic current */
#define SSD1306_LOGIC_ON() HAL_GPIO_WritePin(GPIOC, GPIO_PIN_5, GPIO_PIN_RESET)
#define SSD1306_LOGIC_OFF() HAL_GPIO_WritePin(GPIOC, GPIO_PIN_5, GPIO_PIN_SET)

/*
* Commands macro
*/

#define CONTRAST_DISPLAY 0x81
#define UPDATE_DISPLAY 0xA4
#define ALL_ON 0xA5
#define NORMAL_DISPLAY 0xA6
#define INVERTED_DISPLAY 0xA7
#define DISPLAY_ON 0xAF
#define DISPLAY_OFF 0xAE
#define ADDR_MODE_PAGE 0x10
#define ADDR_START_PAGE 0xB0
#define ADDR_MODE_HORZ 0x00
#define ADDR_MODE_VERT 0x01
#define ADDR_MODE_MEM 0x20
#define ADDR_START_LINE 0x40
#define SEG_REMAP 0xA0
#define SCAN_NORMAL_DIR 0xC0
#define MUX_RATIO 0xA8
#define DISPLAY_OFFSET 0xD3
#define COM_HW_CONFIG 0xDA
#define CLK_SET 0xD5
#define CLK_VCOM 0xDB
#define SCROLL_DISABLE 0xE
 /**
 * @brief  writing commands to SSD1306
 * @param command: macro for CMD
 *
 */
   void SSD1306_WriteCmd(uint8_t command);

  /**
  * @brief writing data to SSD1306
 *  @param data: data array
  *
  */
    void SSD1306_WriteData(uint8_t data);


  /**
 * @brief  initialization SSD1306
 * @retval 1 (success)
 *
 */
  uint8_t SSD1306_Init(void);

  /**
 * @brief turning off SSD1306
 */
  uint8_t SSD1306_DeInit(void);

  /**
 * @brief  display reset
 */
  void SSD1306_ResetDisplay(void);


  /**
 * @brief  updating RAM buffer
 */
  void SSD1306_UpdateScreen(void);

  /**
 * @brief  removing data on screen
 */
  void SSD1306_ClearScreen(SSD1306_COLOR_t color);


  /**
   * @brief  setting pixel value to the data buffer
   * @param  x: current coordinate
   * @param  y: current coordinate
   * @param  color: SSD1306_COLOR_BLACK or SSD1306_COLOR_WHITE (Set pixel)
   */
  void SSD1306_WrightPixel (uint16_t x, uint16_t y, SSD1306_COLOR_t color);


    /**
    * @brief  setting cursor pointer
    * @param  x: current coordinate
    * @param  y: current coordinate
    */
  void SSD1306_GotoXY(uint16_t x, uint16_t y);

     /**
    * @brief  setting char value to RAM
    * @param  ch: character
    * @param  *Font: Pointer to @ref FontDef_t structure with used font
    * @param  color: SSD1306_COLOR_BLACK or SSD1306_COLOR_WHITE (Set pixel)
    * @retval character
    */
   char SSD1306_WrightChar(char ch, FontDef_t* Font, SSD1306_COLOR_t color);

  /**
 * @brief  writing string to RAM
 * @param  *str: string
 * @param  *Font: Pointer to @ref FontDef_t structure with used font
 * @param  color: SSD1306_COLOR_BLACK or SSD1306_COLOR_WHITE (Set pixel)
 * @retval string
 */
  char SSD1306_WrightString(char *str, FontDef_t *Font, SSD1306_COLOR_t color);


/* C++ detection */
#ifdef __cplusplus
}
#endif


#endif /* INC_OLED_H_ */
