from time import sleep
import csv
from json import dumps
from kafka import KafkaProducer



def json_serializer(data):
    return dumps(data).encode('utf-8')

producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
rdr = csv.reader(open("test.csv"))

next(rdr)


while True:
    try:
        line=next(rdr,None)
        if line is None:
            break
        sleep(5)
        timestamp,	FIT101,	LIT101,	 MV101,	P101,	P102,	 AIT201,	AIT202,	AIT203,	FIT201,	 MV201,	 P201,	 P202,	P203,	 P204,	P205,	P206,	DPIT301,	FIT301,	LIT301,	MV301,	MV302,	 MV303,	MV304,	P301,	P302	,AIT401,	AIT402,	FIT401,	LIT401,	P401,	P402	,P403,	P404	,UV401,	AIT501,	AIT502,	AIT503,	AIT504,	FIT501,	FIT502,	FIT503,	FIT504,	P501,	P502,	PIT501,	PIT502,	PIT503,	FIT601,	P601,	P602	,P603,	label=line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10],line[11],line[12],line[13],line[14],line[15],line[16],line[17],line[18],line[19],line[20],line[21],line[22],line[23],line[24],line[25],line[26],line[27],line[28],line[29],line[30],line[31],line[32],line[33],line[34],line[35],line[36],line[37],line[38],line[39],line[40],line[41],line[42],line[43],line[44],line[45],line[46],line[47],line[48],line[49],line[50],line[51],line[52]
        result={"timestamp":timestamp,"FIT101":FIT101,"LIT101":LIT101,"MV101":MV101,"P101":P101,"P102":	P102,	"AIT201": AIT201,"AIT202":	AIT202,"AIT203":	AIT203,"FIT201":	FIT201,"MV201":	 MV201,"P201":	 P201,"P202":	 P202,"P203":	P203,"P204":	 P204,	"P205":P205,"P206":	P206,"DPIT301":	DPIT301,"FIT301":	FIT301,	"LIT301": LIT301,"MV301":	MV301,"MV302":	MV302,	"MV303": MV303,"MV304":	MV304,	"P301": P301,"P302"	:P302	,"AIT401": AIT401,	"AIT402":AIT402,"FIT401":	FIT401,	"LIT401":LIT401,"P401":	P401,"P402":	P402	,"P403": P403,"P404":	P404	,"UV401": UV401,"AIT501":	AIT501,	"AIT502":AIT502,"AIT503":	AIT503,"AIT504":	AIT504,	"FIT501":FIT501,	"FIT502": FIT502,	"FIT503":FIT503,"FIT504":	FIT504,	"P501":P501,"P502":	P502,	"PIT501": PIT501,"PIT502":	PIT502,	"PIT503":PIT503,"FIT601":	FIT601,	"P601":P601,	"P602":P602	,"P603":P603,	"label":label}
        producer.send('SWAT',value=result)
        print(result)
    except Exception as e: 
        print("Error")
        print(f"Type {e}")
        break