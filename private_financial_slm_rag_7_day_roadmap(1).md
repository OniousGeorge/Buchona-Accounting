PROJECT 3 — PRIVATE FINANCIAL SLM + RAG ASSISTANT

Portfolio Pitch

A privacy-focused financial AI assistant that uses a local Small Language Model (SLM), Retrieval-Augmented Generation (RAG), and a structured SQLite transaction database to answer questions about personal financial data with deterministic calculations and source-grounded responses.


CORE ARCHITECTURE

                Bank Statement CSV
                       |
                       v
              +-------------------+
              | Parse + Validate  |
              +---------+---------+
                        |
                        v
                   SQLite DB
                        |
              +---------+---------+
              |                   |
              v                   v
        SQL Analytics          RAG Index
              |                   |
              |             Embeddings +
              |             Vector Search
              |                   |
              +---------+---------+
                        |
                        v
                   SLM Router
                        |
              +---------+---------+
              |                   |
              v                   v
          SQL Query        RAG Retrieval
              |                   |
              +---------+---------+
                        |
                        v
                  Verified Data
                        |
                        v
                       SLM
                        |
                        v
                 Grounded Answer


DAY 1 — FINANCIAL DATA PIPELINE

Goal:
Get bank statement data reliably into the application.

Build:
- CSV upload
- CSV parser
- Column mapping
- Data validation
- Required-field validation
- Date normalization
- Amount normalization
- Merchant normalization
- Duplicate detection
- Basic error reporting

Example:

Upload bank_statement.csv

✓ 347 transactions detected
✓ 347 valid transactions
⚠ 3 duplicate transactions
✓ $8,421.73 total transaction volume

Deliverable:

CSV → validated transaction objects

Do not worry about AI yet.


DAY 2 — SQLITE FINANCIAL DATABASE

Goal:
Turn raw transaction data into a proper structured financial dataset.

Database:

users
accounts
statements
transactions
categories

For the MVP, even a single-user schema is fine.

Transaction fields:

id
date
description
merchant
amount
transaction_type
category
account
statement_id

Implement:
- Insert transactions
- Retrieve transactions
- Update transactions
- Delete transactions
- Basic indexes
- Duplicate prevention
- SQL aggregation

Example queries:
- Total spending
- Spending by category
- Spending by month
- Largest transactions
- Income
- Recurring transactions
- Transactions by merchant

Deliverable:

CSV
 ↓
Validation
 ↓
SQLite
 ↓
Reliable financial queries

At this point, you already have a functional financial-data application without AI.


DAY 3 — LOCAL SLM + TRANSACTION CATEGORIZATION

Goal:
Introduce the SLM.

Use a small local model rather than relying on an external API.

Example input:

Merchant: Wawa
Description: WAWA #1234
Amount: $18.47

Example output:

{
  "category": "Food & Dining"
}

Build:
- Local SLM inference
- Categorization prompt
- Structured output
- Category taxonomy
- Confidence score
- Batch categorization

Add human review:

Wawa
Suggested: Food & Dining
Confidence: 94%

[Accept] [Change]

Store user corrections.

Example:

Amazon
SLM → Shopping
User → Groceries

Deliverable:

Transactions
     ↓
Local SLM
     ↓
Suggested categories
     ↓
Human verification


DAY 4 — RAG PIPELINE

Goal:
Add the actual RAG component.

Create searchable representations of financial information.

Pipeline:

Financial records
      ↓
Create textual representations
      ↓
Chunk
      ↓
Embeddings
      ↓
Vector database

Each indexed record should contain metadata such as:

transaction_id
date
merchant
amount
category
statement_id
user_id

Then:

User question
      ↓
Embedding
      ↓
Vector search
      ↓
Relevant transactions/statements

Example:

User:
"What was that large Amazon charge in August?"

RAG retrieves:

08/14/2026
AMAZON MKTPLACE
$487.21
Category: Shopping
Statement: August 2026

Deliverable:

Question → Retrieval → Relevant financial context


DAY 5 — INTELLIGENT QUERY ROUTING

Goal:
Create an SLM-powered query router.

Do not send every question through RAG.

Architecture:

                 User Question
                       |
                       v
                 Query Router
                       |
          +------------+------------+
          |            |            |
          v            v            v
       SQL Query      RAG        Hybrid

SQL questions:

"How much did I spend in August?"
→ SQLite

"How much did I spend on groceries?"
→ SQLite

"What was my largest purchase?"
→ SQLite

RAG questions:

"What was that weird charge from Amazon?"
→ RAG

"Which transaction was labeled as a subscription?"
→ RAG

Hybrid questions:

"Why did I spend more in August than July?"

→ SQLite calculates the difference.
→ RAG retrieves relevant transactions/context.
→ SLM explains the result.

This is the key architectural distinction of the project.


DAY 6 — FINANCIAL ASSISTANT UI

Goal:
Turn the backend into a usable application.

Keep the UI relatively simple.

Dashboard:

Financial Overview

Income       $4,200
Spending     $2,841
Net          $1,359

Spending by Category
Food
Shopping
Bills
Transport

AI assistant:

Ask your finances

"How much did I spend on food in August?"

"You spent $426.18 across 31 transactions."

View transactions →

Important UI feature:

Show how the answer was produced.

Example:

Answer
$426.18

Source:
SQLite → 31 transactions

[View transactions]

For RAG:

Answer
Your largest Amazon charge was $487.21 on August 14.

Retrieved source:
August 2026 statement
Transaction #284

[View source]

This reinforces grounding and auditability.


DAY 7 — EVALUATION + RELIABILITY + PORTFOLIO POLISH

Do not spend Day 7 adding another major feature.

Make what you have demonstrably reliable.

Build an evaluation set.

Example:

Question                         Expected
------------------------------------------------
August spending                  $2,841.22
August food spending             $426.18
Largest transaction              $487.21
Total income                     $4,200.00
Amazon spending                  $612.41
Transactions > $200              8

Run the system against these questions.

Measure:
- SQL accuracy
- Query-routing accuracy
- Categorization accuracy
- Retrieval accuracy
- Answer correctness

Add basic safeguards:
- SLM cannot directly modify the database
- Financial calculations are deterministic
- SQL queries are constrained
- RAG results are user/data scoped
- Responses cite their underlying data
- Invalid questions are rejected gracefully
- Model failures do not corrupt financial records

Final polish:
- README
- Architecture diagram
- Screenshots
- Setup instructions
- Demo dataset
- Evaluation results
- Short demo video
- Explain architectural decisions


FINAL MVP

PRIVATE FINANCIAL AI

CSV Upload
    |
    v
Data Validation
    |
    v
SQLite
    |
    +----------------------+
    |                      |
    v                      v
Financial Engine          RAG
    |                      |
    |                Vector Search
    |                      |
    +----------+-----------+
               |
               v
          SLM Router
               |
          +----+----+
          |         |
          v         v
         SQL       RAG
          |         |
          +----+----+
               |
               v
          Verified Data
               |
               v
              SLM
               |
               v
        Grounded Response


MVP SCOPE — WHAT NOT TO BUILD IN THE WEEK

Do NOT add:
- Plaid/bank APIs
- PDF/OCR ingestion
- Multi-user authentication
- Cloud infrastructure
- Mobile app
- Fine-tuning
- Investment advice
- Financial forecasting
- Autonomous financial actions
- Complex agent architecture

These are Version 2 / production extensions, not MVP requirements.


PROJECT SCOPE

A local-first financial AI assistant that combines SQLite-based deterministic financial analysis with RAG and a local SLM to provide categorized, grounded, and auditable answers over personal transaction data.

Technology responsibilities:

SQLite → source of truth and computation
RAG → retrieval and context
SLM → classification, routing, and explanation
Python → financial logic
UI → human interaction and verification
