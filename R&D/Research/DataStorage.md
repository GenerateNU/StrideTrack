**OPTIMAL STORAGE METHOD**\

**CSV-**\
-**Overview:** Simple to use and understand, CSV files are ideal for smaller, less complex datasets.\
&emsp;-Easy to open and modify\
&emsp;-Slower to query, especially for large datasets\
&emsp;-Efficient for small-scale data but can become slower as the dataset grows

**Tables-**\
-**Overview:** Tables are ideal for transformed or structured data.\
&emsp;-Able to query quickly\
&emsp;-Can handle large datasets efficiently

**Apache Parquet**\
-**Overview:** Designed for large datasets.\
&emsp;-Groups similar data types together\
&emsp;-Compresses data for storage\
&emsp;-Fast queries

**Conclusion:**\
We dont have as much data that would require us to use parquet, and csv is a good option but we think that storing the data in tables would be the best option for us at the moment.