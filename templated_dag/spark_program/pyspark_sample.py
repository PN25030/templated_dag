# pyspark_sample.py
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("SimplePySparkJob").getOrCreate()

# Create a simple DataFrame
data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
columns = ["Name", "ID"]

df = spark.createDataFrame(data, columns)

# Show the DataFrame content
df.show()

# Stop the Spark session
spark.stop()
