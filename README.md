# 🎮 TikTok Gaming Analytics & AI Strategy Engine

An end-to-end Business Intelligence (BI) pipeline and interactive analytics dashboard built with Python, Streamlit, and the OpenAI API. 

The application ingests unstructured account exports, reconstructs missing video metadata through temporal segmentation and audio distributions, calculates engagement benchmarks across gaming eras, and leverages an LLM to generate data-driven content strategies.

---

## 🚀 Key Features

* **Automated Data Ingestion & Cleansing:** Parses TikTok account dump files into structured Pandas DataFrames, cleaning metrics and normalizing categorical values.
* **Temporal Era Mapping:** Reconstructs content categories across 480+ posts using custom timeline segmentation and sound matching.
* **Interactive Executive Dashboard:** Built with Streamlit and Plotly to monitor KPIs (Total Likes, Average Engagement, Era Distributions, Audio Breakdowns) with dynamic date and category filters.
* **AI Content Strategy Engine:** Integrates `gpt-4o-mini` to analyze engagement outliers and synthesize structured retrospective reports and video concepts.
* **Data Portability:** Features in-app CSV export functionality for downstream analysis.

---

## 🛠️ Tech Stack

* **Language:** Python
* **Analytics & Data Processing:** Pandas, NumPy
* **Visualization & Web App:** Streamlit, Plotly Express
* **AI Integration:** OpenAI API (`gpt-4o-mini`), python-dotenv
* **Version Control:** Git, GitHub

---

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AaronIGW/TikTok_Analysis.git](https://github.com/AaronIGW/TikTok_Analysis.git)
   cd TikTok_Analysis
