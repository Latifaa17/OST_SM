FROM godatadriven/pyspark

COPY . . 

RUN pip3 install -r ./requirements_pyspark.txt

#RUN python consume_detect_store.py
ENTRYPOINT ["tail", "-f", "/dev/null"]
