import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker()
random.seed(42)

def random_account_type():
    return random.choice(['Savings', 'Checking', 'Business', ''])

def random_customer_type():
    return random.choice(['Individual', 'Corporate', ''])

def generate_customers(n=10000):
    data = []
    for i in range(n):
        customer_id = f"CUST{i:05}"
        name = fake.name() if random.random() > 0.01 else None  # Some nulls
        email = fake.email()
        phone = fake.phone_number()
        customer_type = random_customer_type()
        data.append([customer_id, name, email, phone, customer_type])
    return pd.DataFrame(data, columns=['customer_id', 'name', 'email', 'phone', 'customer_type'])

def generate_accounts(customers_df):
    data = []
    for _, row in customers_df.iterrows():
        for _ in range(random.randint(1, 2)):
            account_id = f"ACC{random.randint(100000,999999)}"
            customer_id = row['customer_id']
            acc_type = random_account_type()
            balance = round(random.uniform(-100.0, 50000.0), 2)
            data.append([account_id, customer_id, acc_type, balance])
    return pd.DataFrame(data, columns=['account_id', 'customer_id', 'account_type', 'balance'])

def generate_loans(customers_df):
    data = []
    for _, row in customers_df.iterrows():
        if random.random() < 0.3:
            loan_id = f"LOAN{random.randint(1000,9999)}"
            amount = round(random.uniform(5000, 50000), 2)
            term = random.choice([12, 24, 36, 48, 60])
            status = random.choice(['approved', 'pending', 'defaulted'])
            customer_id = row['customer_id']
            data.append([loan_id, customer_id, amount, term, status])
    return pd.DataFrame(data, columns=['loan_id', 'customer_id', 'amount', 'term', 'status'])

def generate_loan_payments(loans_df):
    data = []
    for _, row in loans_df.iterrows():
        for i in range(random.randint(3, 6)):
            payment_id = f"PAY{random.randint(100000,999999)}"
            loan_id = row['loan_id']
            amount = round(random.uniform(100, 1000), 2)
            date = fake.date_this_decade()
            data.append([payment_id, loan_id, amount, date])
    return pd.DataFrame(data, columns=['payment_id', 'loan_id', 'amount', 'date'])

def generate_transactions(accounts_df):
    data = []
    for _, row in accounts_df.iterrows():
        for _ in range(random.randint(5, 10)):
            transaction_id = f"TXN{random.randint(1000000,9999999)}"
            account_id = row['account_id']
            amount = round(random.uniform(-200.0, 2000.0), 2)
            date = fake.date_this_year()
            description = fake.sentence(nb_words=3)
            data.append([transaction_id, account_id, amount, date, description])
    return pd.DataFrame(data, columns=['transaction_id', 'account_id', 'amount', 'date', 'description'])

# Generate
customers = generate_customers()
accounts = generate_accounts(customers)
loans = generate_loans(customers)
loan_payments = generate_loan_payments(loans)
transactions = generate_transactions(accounts)

# Intentionally add duplicates and invalids
customers = pd.concat([customers, customers.sample(10)])
accounts = pd.concat([accounts, accounts.sample(20)])
customers.loc[5, 'email'] = 'not-an-email'

# Save
customers.to_csv("customers.csv", index=False)
accounts.to_csv("accounts.csv", index=False)
loans.to_csv("loans.csv", index=False)
loan_payments.to_csv("loan_payments.csv", index=False)
transactions.to_csv("transactions.csv", index=False)
