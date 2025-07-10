# AI Resume Portfolio

Developed an intent-aware AI resume chatbot that classifies user queries and retrieves relevant resume content using a keyword-based BM25 retriever, ensuring precise and explainable context for each answer. Embedded core career and skills details directly into system prompts to provide fallback grounding and robust response handling, maintaining accuracy even for ambiguous or off-topic queries. Designed a hybrid Retrieval-Augmented Generation (RAG) system that balances efficiency and accuracy—with a clear upgrade path to semantic or embedding-based retrieval—enabling scalable, future-proof conversational AI
Deployed with **Python, Flask, and Gunicorn** on Render.

## 📸 Screenshot

![Screenshot](./Screenshots/Screenshot-1.png)

---

## 🚀 Live Demo
**[👉 Try the chatbot here!](https://sarmitha-ai-portfolio.onrender.com/)**  

_⚠️ Note: The demo may take up to a minute to load on first visit due to free-tier hosting. Thanks for your patience!_

---

## 🛠️ Tech Stack

- **Python**
- **Flask**
- **Gunicorn**
- **rank_bm25** (BM25)
- **scikit-learn**
- **requests**
- **python-dotenv**
- **langdetect**
- **deep-translator**

---

## ✨ Features

- **Indent classifier**:  
  Uses BM25 (via `bmrank`) to fetch the most relevant resume chunks for each query.

- **System Prompt Grounding**:  
  Core resume details are included in the system prompt for comprehensive and reliable answers—even when retrieval misses.

- **Hybrid RAG Architecture**:  
  Balances efficient keyword-based retrieval with robust fallback system prompt grounding. Ready for upgrades to semantic or hybrid search.

---



