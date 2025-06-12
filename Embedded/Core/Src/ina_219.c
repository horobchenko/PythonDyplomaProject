/*
 * ina_219.c
 *
 *  Created on: Apr 1, 2025
 *      Author: gorob
 */

#include "ina_219.h"

extern I2C_HandleTypeDef hi2c1;

void ina219_init()
{

 if(HAL_I2C_IsDeviceReady(&hi2c1, INA219_ADDRESS_0, 3, 2)==HAL_OK)
	{
	 ina219_write_reg(INA219_REG_CONFIG, INA219_REG_CONFIG_RUN_VALUE, sizeof(INA219_REG_CONFIG_RUN_VALUE));
	}
else
	{
	   return;
	}
}

HAL_StatusTypeDef ina219_read_reg(uint16_t reg, uint8_t *pData, uint16_t len) {
 HAL_StatusTypeDef returnValue;
 uint8_t addr[2];

 /* MSB та LSB частини адреси */
 addr[0] = (uint8_t) ((reg & 0xFF00) >> 8);
 addr[1] = (uint8_t) (reg & 0xFF);

 /* Відправляємо адресу, звідки починається зчитування */
 returnValue = HAL_I2C_Master_Transmit( &hi2c1, INA219_ADDRESS_0, addr, 2, HAL_MAX_DELAY);
 if(returnValue != HAL_OK)
 return returnValue;

 /* Отримання даних */
 returnValue = HAL_I2C_Master_Receive(&hi2c1, INA219_ADDRESS_0, pData, len, HAL_MAX_DELAY);

 return returnValue;
}

HAL_StatusTypeDef ina219_write_reg( uint16_t reg, uint8_t *pData, uint16_t len) {

 HAL_StatusTypeDef returnValue;
 uint8_t *data; // тимчасовий буфер для зберыгання адреси

  data = (uint8_t*)malloc(sizeof(uint8_t)*(len+2));

  /* MSB и LSB частини адреси */
  data[0] = (uint8_t) ((reg & 0xFF00) >> 8);
  data[1] = (uint8_t) (reg & 0xFF);

  /* Копіювання даних в тимчасовий буфер */
  memcpy(data+2, pData, len);

  /* Передача даних */
  returnValue = HAL_I2C_Master_Transmit(&hi2c1, INA219_ADDRESS_0, data, len + 2, HAL_MAX_DELAY);
  if(returnValue != HAL_OK)
  return returnValue;

  free(data);//очищення буфера

  /* Очікування збереження даних */
  while(HAL_I2C_Master_Transmit(&hi2c1, INA219_ADDRESS_0, 0, 0, HAL_MAX_DELAY) != HAL_OK);

  return HAL_OK;
 }

float ina219_read_bus_voltage()
{
	uint8_t pData={};
	ina219_read_reg(INA219_REG_BUSVOLTAGE, pData, sizeof(pData));
	float bus_voltage = (float)(pData<<3) * 0.004;
	return bus_voltage;
}


