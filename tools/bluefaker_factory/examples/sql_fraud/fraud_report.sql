-- Examples SQL for Fraud Dataset

-- Fraud Rate Summary 

SELECT
  COUNT(*) AS total_transactions,
  SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS fraud_count,
  ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_percent
FROM fraud_data;

-- Top Countries by Fraud Rate

SELECT
·   Country,
·   COUNT(*) AS total,
·   SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS fraud_count,
·   ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_percent
· FROM fraud_data
· GROUP BY Country
· HAVING COUNT(*) > 10
· ORDER BY fraud_rate_percent DESC
‣ LIMIT 10;

-- Card Type Risks

SELECT
  Card_Type,
  COUNT(*) AS total,
  SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS frauds,
  ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_percent
FROM fraud_data
GROUP BY Card_Type
ORDER BY fraud_rate_percent DESC;

-- High-Amount Transactions: Legit vs. Fraudulent

SELECT
  Fraudulent,
  COUNT(*) AS tx_count,
  ROUND(AVG(Transaction_Amount), 2) AS avg_amount,
  MAX(Transaction_Amount) AS max_amount
FROM fraud_data
WHERE Transaction_Amount > 800
GROUP BY Fraudulent;

-- Credit Score vs Fraud Rate Buckets

SELECT
  CASE
    WHEN Credit_Score < 400 THEN 'Very Low'
    WHEN Credit_Score < 550 THEN 'Low'
    WHEN Credit_Score < 700 THEN 'Medium'
    ELSE 'High'
  END AS credit_bucket,
  COUNT(*) AS total,
  SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS frauds,
  ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_percent
FROM fraud_data
GROUP BY credit_bucket
ORDER BY credit_bucket;

-- Fraud by Time of Date

SELECT
  SUBSTR(Time_Of_Day, 1, 2) AS hour_bin,
  COUNT(*) AS total,
  SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS fraud_count,
  ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_percent
FROM fraud_data
GROUP BY hour_bin
ORDER BY hour_bin;


-- Top Suspicious Devices

SELECT
  Device,
  COUNT(*) AS total,
  SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) AS fraud_count,
  ROUND(100.0 * SUM(CASE WHEN Fraudulent THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate
FROM fraud_data
GROUP BY Device
HAVING fraud_count > 0
ORDER BY fraud_rate DESC
LIMIT 10;

-- Correlations for ML Feature Engineering (DuckDB)
SELECT
  corr(CAST(Fraudulent AS INT), Transaction_Amount) AS fraud_vs_amount,
  corr(CAST(Fraudulent AS INT), Credit_Score) AS fraud_vs_score,
  corr(CAST(Fraudulent AS INT), Annual_Income) AS fraud_vs_income
FROM fraud_data;

-- Feature Grid for Modeling

SELECT
  Fraudulent,
  ROUND(AVG(Transaction_Amount), 2) AS avg_amount,
  ROUND(AVG(Credit_Score), 2) AS avg_score,
  ROUND(AVG(Annual_Income), 2) AS avg_income
FROM fraud_data
GROUP BY Fraudulent;




