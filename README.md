## Real-time change detection for monitoring Secure Water Treatment (SWaT)

### Run the Project:

  1. Run main.sh , this will start the containers and the kafka producer
  2. From the Stream_Mining_Pipeline folder, run the desired pipeline\
     Example: python ADWIN.py
  3. Login to Grafana or to chronograf to visualize the results\
     Grafana & chronograf credentials: 
     - username: admin
     - password: admin
     - Connection URL to influxdb: http://influxdb:8086
     - DB name: swat


### Architecture:
![image](https://github.com/Latifaa17/OST_SM/OST-SM Architecturw_final.png)

    

