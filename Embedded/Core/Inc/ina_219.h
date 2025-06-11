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

// INA219 structure

typedef struct {
	I2C_HandleTypeDef *i2c;
	uint8_t address;
} ina219_handle_t;


// Functions
  /**
    * @brief  initialization of device
    * @param  *i2c: I2C descriptor
    * @param  *address: INA219 adress
    *
    */
void ina219_init(ina219_handle_t *ina);
/**
  * @brief  writing to device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  */
HAL_StatusTypeDef ina219_write_reg(ina219_handle_t *ina, uint16_t reg, uint8_t *pData, uint16_t len);
/**
  * @brief  reading from device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  *
  */
HAL_StatusTypeDef ina219_read_reg(ina219_handle_t *ina, uint16_t reg, uint8_t *pData, uint16_t len);
/**
  * @brief  reading voltage data
  * @param  *ina: pointer to device structure
  * @retval voltage
  *
  */
float ina219_read_bus_voltage(ina219_handle_t *ina);
/**
  * @brief  deinitialisation of device
  * @param  *ina: pointer to device structure
  *
  */
void ina219_deinit(ina219_handle_t *ina );

#endif /* INC_INA_219_H_ */
