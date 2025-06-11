/*
 * lwip_mqtt.c
 *
 *  Created on: Apr 7, 2025
 *      Author: gorob
 */

#include "lwip/apps/mqtt.h"
#include <string.h>
#include "stm32f7xx_hal.h"
#include "lwip_mqtt.h"

//private variables
extern const char serial_number = "a_111";
extern SSD1306_COLOR_t color = SSD1306_COLOR_WHITE;
extern FontDef_t Font_7x10;

void mqtt_do_connect(mqtt_client_t *client){
	 struct mqtt_connect_client_info_t ci;
	 err_t err;
     char msg[40];
	  /* Setup an empty client info structure */
	  memset(&ci, 0, sizeof(ci));

	  /* Minimal amount of information required is client identifier, so set it here */
	  ci.client_id = serial_number;
	  /* Initiate client and connect to server, if this fails immediately an error code is returned
	     otherwise mqtt_connection_cb will be called with connection result after attempting
	     to establish a connection with the server.
	     For now MQTT version 3.1.1 is always used */
	  err = mqtt_client_connect(client, ip_addr, MQTT_PORT, mqtt_connection_cb,  ci.will_qos, &ci);
	  //For now just print the result code if something goes wrong
	  if(err != ERR_OK) {
		sprintf(msg, "Connection to the broker is broken %d", err);
		SSD1306_ClearScreen();
		SSD1306_WrightString(msg, &Font_7x10, color);
		SSD1306_UpdateScreen();
	  }

	}


void mqtt_connection_cb(mqtt_client_t *client, void *arg, mqtt_connection_status_t status){
	err_t err;
	char msg[40];
	  if(status == MQTT_CONNECT_ACCEPTED) {
		  sprintf(msg,"Hello! Connection to the broker is successful!");
		  SSD1306_ClearScreen();
		  SSD1306_WrightString(msg, &Font_7x10, color);
		  SSD1306_UpdateScreen();
	      err = mqtt_do_publish(client, topic, pub_payload);
	      if(err != ERR_OK) {
	      sprintf(msg, "mqtt_subscribe return: %d\n", err);
	      SSD1306_ClearScreen();
	      SSD1306_WrightString(msg, &Font_7x10, color);
	      SSD1306_UpdateScreen();
	    }
	  } else {
	      sprintf(msg, "mqtt_connection_cb: Disconnected, reason: %d\n", status);
	      SSD1306_ClearScreen();
	      SSD1306_WrightString(msg, &Font_7x10, color);
	      SSD1306_UpdateScreen();
	    /* Its more nice to be connected, so try to reconnect */
	      mqtt_do_connect(client);
	  }

}

void mqtt_do_publish(mqtt_client_t *client, char *topic,const char *pub_payload){
	char msg[40];
	err_t err;
	u8_t qos = 0;
	u8_t retain = 0;
	err = mqtt_publish(client, topic, pub_payload, strlen(pub_payload), qos, retain, mqtt_pub_request_cb, arg);
	if(err != ERR_OK) {
	    sprintf(msg, "Publish err: %d\n", err);
	    SSD1306_ClearScreen();
	    SSD1306_WrightString(msg, &Font_7x10, color);
	    SSD1306_UpdateScreen();
	  }
}
void mqtt_pub_request_cb(char topic, err_t result){
	char msg[40];
	if(result != ERR_OK)
	 {
		sprintf(msg, "Fail to subscribe the %d\n!", topic);
		SSD1306_ClearScreen();
	    SSD1306_WrightString(msg, &Font_7x10, color);
	    SSD1306_UpdateScreen();
	 }
	sprintf(msg, "Subscription to the %d\n is successful!", topic);
	SSD1306_ClearScreen();
	SSD1306_WrightString(msg, &Font_7x10, color);
    SSD1306_UpdateScreen();

}


