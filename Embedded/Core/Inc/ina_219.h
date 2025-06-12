/*
 * ina_219.h
 *
 *  Created on: Apr 1, 2025
 *      Author: gorobchenko
 */

#ifndef INC_INA_219_H_
#define INC_INA_219_H_
#include "main.h"

//	Register adresses

#define	INA219_REG_CONFIG						(0x00)
#define	INA219_REG_BUSVOLTAGE					(0x02)


/*
 *@brief ina219 Configuration register values
 * RUN for default values
 * RESET for reset
 *
 */

#define INA219_REG_CONFIG_RESET_VALUE 			(0x8000)
#define INA219_REG_CONFIG_RUN_VALUE             (0x3E1F)

// Default device address

#define INA219_ADDRESS_0                        (0x40 << 1)       /**< A0 = GND, A1 = GND */



// Functions
  /**
    * @brief  initialization of device
    * @param  *i2c: I2C descriptor
    * @param  *address: INA219 adress
    *
    */
void ina219_init(void);
/**
  * @brief  writing to device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  */
HAL_StatusTypeDef ina219_write_reg( uint16_t reg, uint8_t *pData, uint16_t len);
/**
  * @brief  reading from device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  *
  */
HAL_StatusTypeDef ina219_read_reg( uint16_t reg, uint8_t *pData, uint16_t len);
/**
  * @brief  reading voltage data
  * @param  *ina: pointer to device structure
  * @retval voltage
  *
  */
float ina219_read_bus_voltage(void);
/**
  * @brief  deinitialisation of device
  * @param  *ina: pointer to device structure
  *
  */
void ina219_deinit(void);

#endif /* INC_INA_219_H_ */
