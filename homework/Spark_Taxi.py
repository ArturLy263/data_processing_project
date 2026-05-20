from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, count, sum, hour, desc, dense_rank
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("TaxiAnalysis") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.read.csv(
    "/Users/arturliashenko/Downloads/archive/yellow_tripdata_2019-01.csv",
    header=True,
    inferSchema=True
)

df.printSchema()
df.show(5)

raw_count = df.count()
print(f"Total rows: {raw_count}")

df.select("trip_distance", "fare_amount", "tip_amount").describe().show()

df.select([
    F.count(F.when(F.col(c).isNull(), c)).alias(c)
    for c in df.columns
]).show()

df_step1 = df.filter(col("trip_distance") > 0)

df_step2 = df_step1.filter(
    (col("fare_amount") > 0) &
    (col("fare_amount") < 500)
)

df_step3 = df_step2.filter(
    col("passenger_count").between(1, 6)
)

df_step4 = df_step3.filter(
    col("tpep_pickup_datetime").isNotNull() &
    col("tpep_dropoff_datetime").isNotNull()
)

df_step5 = df_step4.filter(
    col("tpep_dropoff_datetime") > col("tpep_pickup_datetime")
)

clean_count = df_step5.count()
removed = raw_count - clean_count
percentage = (removed / raw_count) * 100

print(f"Removed rows: {removed}")
print(f"Percentage removed: {percentage:.2f}%")

df_step6 = df_step5.withColumn(
    "trip_duration_minutes",
    (
        col("tpep_dropoff_datetime").cast("long") -
        col("tpep_pickup_datetime").cast("long")
    ) / 60
)

df_step6.select("trip_duration_minutes").show(5)

df_step7 = df_step6.filter(
    (col("trip_duration_minutes") > 0) &
    (col("trip_duration_minutes") <= 180)
)

df_step7 = df_step7.withColumn(
    "time_of_day",
    F.when((F.hour("tpep_pickup_datetime") >= 0) & (F.hour("tpep_pickup_datetime") <= 5), "night")
     .when((F.hour("tpep_pickup_datetime") >= 6) & (F.hour("tpep_pickup_datetime") <= 11), "morning")
     .when((F.hour("tpep_pickup_datetime") >= 12) & (F.hour("tpep_pickup_datetime") <= 17), "afternoon")
     .when((F.hour("tpep_pickup_datetime") >= 18) & (F.hour("tpep_pickup_datetime") <= 23), "evening")
     .otherwise("unknown")
)

df_step7.groupBy("time_of_day").count().show()

df_step8 = df_step7.withColumn(
    "speed_mph",
    (col("trip_distance") * 60) / col("trip_duration_minutes")
)

df_step9 = df_step8.withColumn(
    "is_suspicious_speed",
    col("speed_mph") > 80
)

suspicious_count = df_step9.filter(
    col("is_suspicious_speed") == True
).count()

print(f"Suspicious trips: {suspicious_count}")

df_step10 = df_step9.withColumn(
    "tip_pct",
    F.when(
        col("fare_amount") > 0,
        F.round((col("tip_amount") / col("fare_amount")) * 100, 2)
    ).otherwise(0)
)

df_step11 = df_step10.withColumn(
    "payment_type_label",
    F.when(col("payment_type") == 1, "Credit Card")
     .when(col("payment_type") == 2, "Cash")
     .when(col("payment_type") == 3, "No Charge")
     .when(col("payment_type") == 4, "Dispute")
     .when(col("payment_type") == 5, "Unknown")
     .when(col("payment_type") == 6, "Voided Trip")
     .otherwise("Other")
)

df_step12 = df_step11.withColumn(
    "pickup_hour",
    F.hour("tpep_pickup_datetime")
)

summary_df = df_step12.groupBy("pickup_hour").agg(
    F.count("*").alias("total_trips"),
    F.round(F.avg("fare_amount"), 2).alias("avg_fare"),
    F.avg("tip_pct").alias("avg_tip_pct"),
    F.avg("trip_duration_minutes").alias("avg_duration_minutes")
)

summary_df.orderBy(F.col("pickup_hour").asc()).show()

df_step13 = df_step12.groupBy("payment_type_label").agg(
    F.count("*").alias("total_trips"),
    F.avg("tip_pct").alias("avg_tip_pct"),
    F.percentile_approx("tip_pct", 0.5).alias("median_tip_pct")
)

df_step13.show()

df_step14 = df_step12.groupBy("PULocationID").agg(
    F.round(F.sum("fare_amount"), 2).alias("total_revenue")
)

top_10_df = df_step14.orderBy(
    F.col("total_revenue").desc()
).limit(10)

lookup_data = [
    (132, "JFK Airport"),
    (138, "LaGuardia Airport"),
    (161, "Midtown Center"),
    (237, "Upper East Side South"),
    (236, "Upper East Side North"),
    (186, "Penn Station / Madison Sq West")
]

lookup_df = spark.createDataFrame(
    lookup_data,
    ["PULocationID", "zone_name"]
)

joined_df = top_10_df.join(
    lookup_df,
    on="PULocationID",
    how="left"
)

joined_df.show(truncate=False)

df_step15 = df_step12.withColumn(
    "pickup_date",
    to_date("tpep_pickup_datetime")
)

daily_counts = df_step15.groupBy(
    "pickup_date"
).count()

window_spec = Window.orderBy(
    "pickup_date"
).rowsBetween(
    Window.unboundedPreceding,
    Window.currentRow
)

df_result = daily_counts.withColumn(
    "cumulative_trip_count",
    sum("count").over(window_spec)
)

df_result.orderBy("pickup_date").show()

df_step20 = df_step12.withColumn(
    "pickup_date",
    to_date("tpep_pickup_datetime")
).withColumn(
    "pickup_hour",
    hour("tpep_pickup_datetime")
)

hourly_counts = df_step20.groupBy(
    "pickup_date",
    "pickup_hour"
).count()

window_spec = Window.partitionBy(
    "pickup_date"
).orderBy(
    desc("count")
)

ranked_hours = hourly_counts.withColumn(
    "daily_hour_rank",
    dense_rank().over(window_spec)
)

peak_hours = ranked_hours.filter(
    "daily_hour_rank = 1"
)

peak_hours.orderBy("pickup_date").show()

spark.stop()