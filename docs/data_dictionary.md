# Bronze_layer

bronze_db.bronze_customers

| Column       | Type   | Description              |
| ------------ | ------ | ------------------------ |
| customer\_id | STRING | Unique customer ID       |
| first\_name  | STRING | First name               |
| last\_name   | STRING | Last name                |
| dob          | STRING | Date of birth (unparsed) |
| email        | STRING | Email address            |
| phone        | STRING | Contact number           |
| address      | STRING | Residential address      |
| city         | STRING | City name                |
| state        | STRING | State or province        |
| zip          | STRING | ZIP or postal code       |

bronze_db.bronze_loans

| Column         | Type   | Description                       |
| -------------- | ------ | --------------------------------- |
| loan\_id       | STRING | Unique loan identifier            |
| customer\_id   | STRING | Customer associated with the loan |
| loan\_type     | STRING | Type of loan (Auto, Home, etc.)   |
| start\_date    | STRING | Start date (raw format)           |
| end\_date      | STRING | End date (raw format)             |
| principal      | DOUBLE | Principal amount                  |
| interest\_rate | STRING | Interest rate (as string with %)  |
| status         | STRING | Loan status (e.g., Defaulted)     |

bronze_db.bronze_accounts

| Column        | Type   | Description             |
| ------------- | ------ | ----------------------- |
| account\_id   | STRING | Unique account ID       |
| customer\_id  | STRING | Owner of the account    |
| account\_type | STRING | Savings, Checking, etc. |
| open\_date    | STRING | Open date (raw format)  |
| status        | STRING | Active, Suspended, etc. |
| balance       | DOUBLE | Account balance         |

bronze_db.bronze_payments

| Column        | Type   | Description                         |
| ------------- | ------ | ----------------------------------- |
| payment\_id   | STRING | Unique payment identifier           |
| loan\_id      | STRING | Loan associated with the payment    |
| payment\_date | STRING | Payment date (raw format)           |
| amount        | DOUBLE | Amount paid                         |
| method        | STRING | ACH, Credit, Debit, etc.            |
| status        | STRING | Payment status (Pending, Failed...) |

bronze_db.bronze_transactions

| Column      | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| txn\_id     | STRING | Unique transaction ID                    |
| account\_id | STRING | Account associated with transaction      |
| txn\_type   | STRING | Transaction type (Deposit, Withdraw\...) |
| amount      | DOUBLE | Amount of transaction                    |
| txn\_date   | STRING | Transaction date (raw format)            |
| merchant    | STRING | Merchant involved                        |
| location    | STRING | Transaction location                     |


# Silver Layer
Cleaned, typed, deduplicated, and enriched data.
Each Silver table includes:
Converted data types (e.g., STRING → DATE, DOUBLE)
Cleaned missing values
Metadata columns:
    silver_<domain>_ingestion_time (TIMESTAMP)
    bronze_file_name (STRING)
    row_hash (STRING)

Example schemas:

| Column         | Type   | Description                |
| -------------- | ------ | -------------------------- |
| loan\_id       | STRING | Unique loan identifier     |
| customer\_id   | STRING | Customer ID                |
| loan\_type     | STRING | Type of loan               |
| start\_date    | DATE   | Cleaned start date         |
| end\_date      | DATE   | Cleaned end date           |
| principal      | DOUBLE | Loan principal             |
| interest\_rate | DOUBLE | Converted from percentage  |
| status         | STRING | Loan status                |
| row\_hash      | STRING | SHA256 of full row content |


Other Silver tables follow similar formatting for payments, accounts, transactions, customers.

# Gold Layer

Final data products for analytics and ML

gold_db.customer_360

| Column Name         | Type   | Description                      |
| ------------------- | ------ | -------------------------------- |
| customer\_id        | STRING | Unique customer ID               |
| num\_loans          | INT    | Total number of loans            |
| total\_principal    | DOUBLE | Total principal across all loans |
| avg\_interest\_rate | DOUBLE | Average loan interest rate       |
| total\_paid         | DOUBLE | Total loan payment amount        |
| failed\_payments    | INT    | Number of failed payments        |
| num\_accounts       | INT    | Number of customer accounts      |
| total\_balance      | DOUBLE | Total account balance            |
| avg\_balance        | DOUBLE | Average account balance          |
| total\_txn\_amount  | DOUBLE | Sum of transaction amounts       |
| txn\_count          | INT    | Number of transactions           |

gold_db.loan_risk_scoring

| Column Name      | Type   | Description                          |
| ---------------- | ------ | ------------------------------------ |
| loan\_id         | STRING | Unique loan ID                       |
| customer\_id     | STRING | Customer ID                          |
| loan\_type       | STRING | Type of loan                         |
| principal        | DOUBLE | Principal amount                     |
| interest\_rate   | DOUBLE | Interest rate                        |
| duration\_years  | INT    | Duration in years                    |
| total\_paid      | DOUBLE | Total payments made                  |
| num\_payments    | INT    | Number of payments                   |
| failed\_payments | INT    | Failed payments                      |
| avg\_balance     | DOUBLE | Customer’s avg account balance       |
| num\_accounts    | INT    | Customer’s number of accounts        |
| is\_defaulted    | INT    | Target label: 1 = Defaulted, 0 = Not |
