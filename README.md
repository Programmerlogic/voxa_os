# Superstore AI Executive Analyst: Project Documentation

## 1. Problem Statement
Business executives and managers need quick, accurate answers to business analytics questions based on company data and reports. However, manually searching through 10,000+ transaction records in raw CSV files or reading through multiple dense analytical documents is highly inefficient. Furthermore, out-of-the-box conversational AI platforms often face strict file size and token limits, making it impossible to directly upload massive raw datasets for querying.

## 2. Concept Explanation
The solution is a **Compound AI Business Analyst Chatbot** that uses aggregated, high-value business analytics `.txt` files as its knowledge base.
Instead of forcing the AI to read thousands of individual transaction rows, the raw data is pre-processed using Python to create compressed "Executive Summaries" and "Entity Profiles." The chatbot uses Retrieval-Augmented Generation (RAG) to semantically search these text files, enabling users to ask natural language questions and receive instant, context-aware answers regarding profitability, supply chain efficiency, and VIP customer metrics.

## 3. Core Documentation
### Introduction
The Superstore AI Executive Analyst is an intelligent web widget designed to act as a 24/7 data analyst for business stakeholders. Embedded directly into a React or Streamlit dashboard, it provides conversational access to complex sales and operational metrics without requiring the user to know SQL or navigate complex BI dashboards.
### Solution Overview
The architecture consists of three main components:
1. **Data Engineering (Python/Pandas):** Scripts that clean a raw 10,000-row CSV and aggregate the data into highly compressed `.txt` summaries (e.g., VIP Customer Profiles, Top Product Profits, Regional Risks).
2. **AI Orchestration (VoiceOS):** The conversational agent framework where the `.txt` files are uploaded to the Knowledge Base. It features "Global Classifications" to route user intent and multi-turn "Task Configurations" (like *Evaluate Discount Impact*) to proactively investigate business problems.
3. **Front-End Deployment (JavaScript/Streamlit):** A lightweight embed snippet that injects the AI chat interface into the existing company web portal.
### Knowledge Base
The AI relies strictly on the following processed text documents to prevent hallucination:
* `1_Master_Executive_Summaries.txt`: Contains macro-level data on overall profitability, sales performance, supply chain efficiency, and market insights.
* `Executive_Cheat_Sheet_Top_Metrics.txt`: A highly compressed file containing lifetime spend data for the Top 100 VIP Customers, Top 100 Profitable Products, and Top 50 Risk (Money-Losing) Products.
### Usage Instructions
1. Navigate to the internal Superstore Analytics web portal.
2. Click the floating chat widget in the bottom right corner.
3. Use one of the pre-configured quick-action buttons (e.g., "Top VIP Customers", "Evaluate Discounts") to start a guided investigation, or simply type a natural language question into the chat box.
### Example Queries
* **Query:** "What is our overall profit margin?"
  * **Expected Response:** "Our overall profit margin is 12.47%. However, 18.7% of our orders are currently loss-making."
* **Query:** "Who are our top VIP customers?"
  * **Expected Response:** "Based on our executive metrics, our top VIPs include [Customer Name] with a total lifetime spend of $[Amount]."
* **Query:** "Why are we losing money in the South region?"
  * **Expected Response:** "The losses in the South are heavily correlated with excessive discounts. Orders with a discount greater than 30% result in an average loss of $-107.21."
### Limitations & Future Work
* **Current Limitations:** Due to chatbot platform upload constraints, the bot currently operates on an aggregated "Executive Cheat Sheet." It cannot perform granular, row-by-row lookups for single, low-value transactions that occurred years ago.
* **Future Work:** Replace the static `.txt` Knowledge Base with an External Tool API connection to a live SQL Database (like BigQuery or PostgreSQL), allowing the agent to generate and execute SQL queries in real-time for unlimited data depth.

## 4. Dataset Description & Analytical Capabilities
The underlying data powering this AI originates from the Superstore dataset. By preprocessing this data, the AI is equipped to handle complex, deep-dive business inquiries across the following core analytical domains:
### 1. Market Basket Analysis (Cross-Selling Opportunities)
* **What it is:** Analyzing `Order ID` against `Sub-Category` or `Product Name` to see which items are frequently bought together.
* **Business Value:** Identifying that customers buying "Copiers" frequently buy "Paper" and "Binders" allows the business to create bundled offers or recommend these items during checkout, actively increasing the Average Order Value (AOV).
### 2. Deep-Dive Product Portfolio Analysis
* **What it is:** Granular analysis at the `Sub-Category` level (e.g., Bookcases, Phones, Chairs).
* **Business Value:** Allows the mapping of a Boston Consulting Group (BCG) Matrix to classify sub-categories into:
  * **Stars:** High Sales, High Profit.
  * **Cash Cows:** Stable Sales, High Profit.
  * **Dogs:** Low Sales, Low Profit (e.g., Tables are notoriously unprofitable in this dataset).
  * **Question Marks:** High Sales, but Negative Margins due to aggressive discounting.
### 3. Price Elasticity & Discount Effectiveness
* **What it is:** Correlating the `Discount` given with the `Quantity` sold.
* **Business Value:** Determines if a 40% discount actually results in customers buying 3x more quantity, or if margins are being sacrificed for no extra volume. This analysis helps identify the "sweet spot" for discounting where revenue and profit are maximized.
### 4. Customer Cohort Analysis & Lifetime Value (CLV)
* **What it is:** Grouping customers by the month/year of their first purchase (`Order Date`) and tracking how often they return in subsequent months.
* **Business Value:** Accurately measures customer retention over time, answering critical strategic questions such as, *"Are customers acquired in 2014 more loyal than those acquired in 2016?"*
### 5. Detailed Time-Series & Seasonality
* **What it is:** Breaking down the `Order Date` into Day of Week, Quarter, and specific Months.
* **Business Value:** Identifies micro-trends for operational planning. For example, discovering if Corporate clients order mostly on Tuesdays, or if office supplies spike exactly in August (Back to School) and November (Holiday Prep). This data perfectly times marketing emails and inventory stocking.

## 5. File Preparation
To maintain the chatbot's accuracy, the knowledge base files must be updated periodically:
1. Download the latest `Superstore.csv` export.
2. Run the provided Python aggregation script (`generate_kb_files.py`) locally.
3. The script will output well-formatted `.txt` files containing natural language narratives of the data. Ensure all files use UTF-8 encoding.
4. Upload the generated files to the VoiceOS Knowledge Base, replacing the older versions.

## 6. Verification
* Review this documentation for clarity and completeness prior to stakeholder handover.
* Test the live chatbot with sample queries to ensure it fetches correct information exclusively from the uploaded `.txt` files.
* Confirm that the initial welcome message and quick-action buttons trigger the correct classification logic.

## 7. Relevant Files
* `app.py`: Main Streamlit front-end logic and widget injection code.
* `generate_kb_files.py`: Data aggregation script for converting CSV rows into compressed RAG-optimized text.
* `Executive_Cheat_Sheet_Top_Metrics.txt`: Core knowledge base source file.
* `1_Master_Executive_Summaries.txt`: Core knowledge base source file.

## 8. Decisions Log
* **Data Aggregation Pivot:** Initially attempted to upload 10,000 distinct transactional narratives. Due to strict platform file size and token limits causing upload timeouts, the architecture was pivoted to aggregate data into "Entity Profiles" and an "Executive Cheat Sheet," successfully bypassing platform restrictions while retaining critical BI value.
* **Knowledge Base Isolation:** Decided to use only the provided `.txt` files generated from the dataset to strictly ground the AI and prevent hallucinations based on external internet data.
* **Documentation Format:** The documentation is written in Markdown (`.md`) for easy readability, version control compatibility, and seamless sharing across developer teams.
