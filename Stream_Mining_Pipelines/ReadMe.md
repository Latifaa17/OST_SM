#Pipelines description

***CUSUM is a point change detector. It loops over all columns of the dataset and detects change 
when the cumulative sum is beyond a predefined threshold. In real time streaming, the detector waits for a batch of data points, 
then detects changes if any for a given batch.

***PageHinkley is also a drift detection method and works with only one column. At each timestamp the detector is updated with the new point and checks whether the new point is a change point.

***KSWIN (Kolmogorov-Smirnov Windowing) is a concept change detection method based on the Kolmogorov-Smirnov (KS) statistical test. KS-test is a statistical test with no assumption of underlying data distribution. KSWIN maintains a sliding window fixed size n (window_size). The last r (stat_size) samples of window are considered as R. From the first n−r samples, r samples are uniformly drawn, are considered as W. A drift is detected if the distance between W and R is greater than a given threshold.