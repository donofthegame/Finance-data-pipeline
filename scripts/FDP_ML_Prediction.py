# Databricks notebook source
import pandas as pd

df_payments = spark.read.csv('/Volumes/workspace/default/fdp/loan_payments.csv', header=True, inferSchema=True)
df_loans = spark.read.csv('/Volumes/workspace/default/fdp/loans.csv', header= True, inferSchema=True)
display(df_payments)
display(df_loans)

# COMMAND ----------

# MAGIC %md
# MAGIC Cleaning Loans Data

# COMMAND ----------

from pyspark.sql.functions import col, when, regexp_replace, to_date

# Clean interest_rate (% -> double)
df_loans = df_loans.withColumn(
    "interest_rate", regexp_replace("interest_rate", "%", "").cast("double")
)

# Replace invalid end_date with null, then convert to date
df_loans = df_loans.withColumn(
    "end_date",
    when(col("end_date") == "9999-99-99", None).otherwise(col("end_date"))
)
df_loans = df_loans.withColumn("start_date", to_date("start_date", "yyyy-MM-dd"))
df_loans = df_loans.withColumn("end_date", to_date("end_date", "yyyy-MM-dd"))

# Drop rows with essential nulls
df_loans_clean = df_loans.dropna(subset=["loan_id", "customer_id", "start_date", "principal"])


# COMMAND ----------

# MAGIC %md
# MAGIC Cleaing Loan Payments Data

# COMMAND ----------

from pyspark.sql.functions import to_date


# Replace "N/A" with null, parse to date
df_payments = df_payments.withColumn(
    "payment_date",
    when(col("payment_date") == "N/A", None).otherwise(col("payment_date"))
)
df_payments = df_payments.withColumn("payment_date", to_date("payment_date", "yyyy-MM-dd"))

# Fill missing values for method/status if you want to keep them
df_payments = df_payments.fillna({
    "method": "Unknown",
    "status": "Unknown",
    "amount": 0.0
})

# Drop payments without a loan_id
df_payments_clean = df_payments.dropna(subset=["loan_id"])


# COMMAND ----------

# MAGIC %md
# MAGIC Predict loan default using:
# MAGIC
# MAGIC Payment behavior (successful, failed, pending)
# MAGIC
# MAGIC Loan details (principal, interest, etc.)
# MAGIC
# MAGIC

# COMMAND ----------

from pyspark.sql.functions import sum, count, when, col

df_pay_features = df_payments_clean.groupBy("loan_id").agg(
    sum("amount").alias("total_payment_amount"),
    count("*").alias("num_payments"),
    sum(when(col("status") == "Successful", 1).otherwise(0)).alias("num_successful"),
    sum(when(col("status") == "Pending", 1).otherwise(0)).alias("num_pending"),
    sum(when(col("status") == "Failed", 1).otherwise(0)).alias("num_failed"),
    sum(when(col("status") == "Unknown", 1).otherwise(0)).alias("num_unknown"),
    # Binary label: 1 = has failed payment(s)
    (sum(when(col("status") == "Failed", 1).otherwise(0)) > 0).cast("int").alias("default_label")
)


# COMMAND ----------

# MAGIC %md
# MAGIC Joining the features wiht Cleaned Loans Data

# COMMAND ----------

df_ml = df_loans_clean.join(df_pay_features, on="loan_id", how="inner") \
    .select(
        "loan_id", "customer_id", "loan_type", "principal", "interest_rate",
        "total_payment_amount", "num_payments",
        "num_successful", "num_pending", "num_failed", "num_unknown",
        "default_label"
    ).na.drop()


# COMMAND ----------

df_ml_pd = df_ml.toPandas()



# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Convert to Pandas

# COMMAND ----------

df_pd = df_ml.select(
    "principal", "interest_rate", "total_payment_amount",
    "num_payments", "num_successful", "num_pending", "num_failed", "num_unknown",
    "default_label"
).toPandas()


# COMMAND ----------

# MAGIC %md
# MAGIC Logistic Regression

# COMMAND ----------

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X = df_pd.drop("default_label", axis=1)
y = df_pd["default_label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

logreg = LogisticRegression()
logreg.fit(X_train, y_train)

print("Logistic Regression Accuracy:", logreg.score(X_test, y_test))


# COMMAND ----------

y_pred = logreg.predict(X_test)


y_prob = logreg.predict_proba(X_test)[:, 1]

X_test_result = X_test.copy()
X_test_result["actual"] = y_test.values
X_test_result["predicted"] = y_pred
X_test_result["probability"] = y_prob

# X_test_result.head()
id_cols = df_ml_pd.loc[X_test.index, ["loan_id", "customer_id", "loan_type"]]


# Reattach identifier columns
X_test_result_final = pd.concat([id_cols.reset_index(drop=True), X_test_result.reset_index(drop=True)], axis=1)


# Preview
X_test_result_final.head()



# COMMAND ----------

# MAGIC %md
# MAGIC Linear Regression

# COMMAND ----------

from sklearn.linear_model import LinearRegression

# Example: Predict total_payment_amount
X_lin = df_pd.drop(["total_payment_amount", "default_label"], axis=1)
y_lin = df_pd["total_payment_amount"]

X_train_lin, X_test_lin, y_train_lin, y_test_lin = train_test_split(X_lin, y_lin, test_size=0.2, random_state=42)

linreg = LinearRegression()
linreg.fit(X_train_lin, y_train_lin)

print("Linear Regression R²:", linreg.score(X_test_lin, y_test_lin))


# COMMAND ----------

# MAGIC %md
# MAGIC Predictions vs Actuals

# COMMAND ----------

# Predict on test set
y_pred_lin = linreg.predict(X_test_lin)

# Copy test set and add predictions and actuals
X_test_lin_result = X_test_lin.copy()
X_test_lin_result["actual_total_payment_amount"] = y_test_lin.values
X_test_lin_result["predicted_total_payment_amount"] = y_pred_lin

# # Preview the result
# X_test_lin_result.head()
id_cols = df_ml_pd.loc[X_test.index, ["loan_id", "customer_id", "loan_type"]]


# Add back identifiers
X_test_lin_result_final = pd.concat([id_cols.reset_index(drop=True), X_test_lin_result.reset_index(drop=True)], axis=1)

# Preview
X_test_lin_result_final.head()


# COMMAND ----------

# MAGIC %md
# MAGIC Confusion Matrix and Classification Report

# COMMAND ----------

from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

# Predict
y_pred = logreg.predict(X_test)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Not Defaulted", "Defaulted"])
disp.plot(cmap='Blues')


# COMMAND ----------

# Print classification report
print(classification_report(y_test, y_pred))
