-- 1. Top 5 fund houses by total AUM (most recent date)
SELECT fund_house, aum_crore
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month, per fund
SELECT amfi_code, strftime('%Y-%m', date) AS month, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month;

-- 3. Total transaction amount by state
SELECT state, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 4. Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- 5. Transaction count and total by transaction_type
SELECT transaction_type, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- 6. Top 5 funds by Sharpe ratio
SELECT df.scheme_name, fp.sharpe_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY fp.sharpe_ratio DESC
LIMIT 5;

-- 7. Average transaction amount by age group
SELECT age_group, AVG(amount_inr) AS avg_amount
FROM fact_transactions
GROUP BY age_group;

-- 8. Funds per fund house
SELECT fund_house, COUNT(*) AS num_funds
FROM dim_fund
GROUP BY fund_house
ORDER BY num_funds DESC;

-- 9. Highest and lowest NAV recorded per fund
SELECT amfi_code, MIN(nav) AS min_nav, MAX(nav) AS max_nav
FROM fact_nav
GROUP BY amfi_code;

-- 10. City tier split of total investment amount
SELECT city_tier, SUM(amount_inr) AS total_amount, COUNT(*) AS num_transactions
FROM fact_transactions
GROUP BY city_tier;