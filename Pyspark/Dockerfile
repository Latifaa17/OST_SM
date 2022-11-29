FROM protonai/pyspark

COPY . . 

RUN pip3 install -r ./requirements_pyspark.txt

ENTRYPOINT ["tail", "-f", "/dev/null"]
