/*
 * lwip_mqtt.h
 *
 *  Created on: Apr 7, 2025
 *      Author: gorob
 */

#ifndef INC_LWIP_MQTT_H_
#define INC_LWIP_MQTT_H_

#include "lwip/apps/mqtt.h"
#include "oled.h"
#include "ina_219.h"

/**
  * @brief  connecting to mqtt brocker
  * @param  *client: pointer client base structure

  *
  */
void mqtt_do_connect(mqtt_client_t *client);
/**
  * @brief  reading from device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  *
  */
void mqtt_connection_cb(mqtt_client_t *client, void *arg, mqtt_connection_status_t status);
/**
  * @brief  reading from device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  *
  */
void mqtt_do_publish(mqtt_client_t *client, void *arg);
/**
  * @brief  reading from device registers
  * @param  *ina: pointer to device structure
  * @param  reg: register address
  * @param  *pData: pointer to data array
  * @param  len: lenth of data array
  *
  */
void mqtt_pub_request_cb(char topic, err_t result);


#endif /* INC_LWIP_MQTT_H_ */
