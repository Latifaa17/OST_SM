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
![image](https://github.com/Latifaa17/OST_SM/assets/48823874/fedc1d0b-846a-4a7d-9db2-b82dc4579091)
    

