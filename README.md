
# 💰 Finance Data Pipeline Project

A complete end-to-end data lakehouse pipeline built using AWS services including S3, Glue, Athena, and Delta Lake, with data processed using PySpark and orchestrated through Glue Jobs and Terraform.

---

## 📌 Project Objectives

- Ingest raw finance-related data (accounts, loans, customers, transactions, payments) into an AWS S3-based Bronze layer.
- Clean, enrich, and deduplicate data using PySpark ETL jobs.
- Store transformed data in Delta Lake format in Silver and Gold layers.
- Use AWS Glue Data Catalog for table management and schema evolution.
- Enable downstream BI and ML use cases (QuickSight, SageMaker).
- Automate infrastructure using Terraform for reproducibility and scalability.

---

## 📁 Project Structure

```
Finance-data-pipeline/
│
├── scripts/                     # PySpark ETL scripts for each dataset
│   ├── accounts_etl.py
│   ├── customers_etl.py
│   ├── loans_etl.py
│   ├── payments_etl.py
│   ├── transactions_etl.py
│
├── terraform/                   # Infrastructure as Code (IaC)
│   ├── main.tf                  # Root configuration
│   ├── variables.tf             # Input variables
│   ├── outputs.tf               # Output values
│   ├── providers.tf             # AWS provider setup
│   ├── backend.tf               # Remote state config (optional)
│   ├── modules/
│   │   ├── s3/                  # S3 buckets (bronze, silver, gold)
│   │   ├── s3_public/          # Public S3 buckets for Databricks access
│   │   ├── glue/               # Glue databases, crawlers
│   │   └── iam/                # IAM roles and policies
│
├── data/                        # Synthetic data (optional for testing)
│
└── README.md                    # Project documentation
```

---

## 🏗️ Infrastructure Setup

All infrastructure is managed via Terraform modules:

### Modules

| Module       | Resources Provisioned                     |
|--------------|--------------------------------------------|
| `s3`         | Bronze, Silver, and Gold S3 buckets       |
| `s3_public`  | Public Silver/Gold S3 buckets (for Databricks) |
| `glue`       | Glue Databases and Crawlers               |
| `iam`        | IAM Roles for Glue Jobs and Crawlers      |

> 🔐 Access is restricted using least-privilege IAM roles. Public buckets explicitly allow read/write for demo purposes.

---

## 🔁 ETL Process Overview

Each ETL script performs the following steps:

1. **Read raw data from Bronze layer (S3 or Glue Catalog)**
2. **Apply data cleaning and enrichment**
3. **Generate data lineage (e.g., ingestion timestamp, filename)**
4. **Deduplicate using window functions and SHA2 row hashes**
5. **Write to Silver layer in Delta format and register to Glue**

---

## 📊 Data Lake Architecture

```
S3 (Bronze Layer - Raw CSV)
   │
   └──▶ Glue Job (PySpark) → Delta Tables (Silver Layer)
                                  │
                                  └──▶ Gold Layer (Aggregated Views, KPIs)

Other Integrations:
- 🧠 ML Models (SageMaker)
- 📈 Dashboards (QuickSight)
```

---

## 🔒 Security & Compliance

- **PII Tagging**: Sensitive fields (e.g., email, phone, dob) are tagged during Silver layer processing.
- **Access Control**:
  - S3 bucket policies restrict unauthorized access.
  - IAM roles created with scoped permissions.
- **Logging**: Glue Jobs and Crawlers write logs to CloudWatch.

---

## 🚀 Getting Started

### 🧱 Deploy Infra

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 🧪 Run ETL Jobs

Upload your PySpark ETL scripts to `s3://<glue-script-bucket>/scripts/` and trigger the jobs manually or using the AWS Console.

---

## 📚 Future Enhancements

- Add CI/CD for Glue Jobs (using CodePipeline or Jenkins)
- Add partitioning strategy for performance
- Automate Gold layer aggregations
- Integrate with Amazon SageMaker for ML models

---

## 🧑‍💻 Author

**[@donofthegame](https://github.com/donofthegame)** – Building scalable data platforms with AWS and open-source tools.

---

## 📝 License

This project is licensed under the MIT License.
