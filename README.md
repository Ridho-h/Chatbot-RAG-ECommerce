# Chatbot RAG E-Commerce

An intelligent e-commerce chatbot powered by Retrieval-Augmented Generation (RAG), combining product database search with real-time internet search capabilities.

## What the Project Does

This project implements an AI chatbot that answers customer queries about products by:
- **Searching product databases** using FAISS vector store with semantic embeddings
- **Retrieving relevant product information** including specifications, prices, ratings, and links
- **Augmenting responses** with real-time web search when needed
- **Using advanced LLMs** (Groq's Llama 3.3 70B) for intelligent reasoning and response generation

The chatbot leverages a ReAct (Reasoning + Acting) agent framework that intelligently decides when to search the product database vs. the internet for optimal responses.

## Key Features

✨ **Dual Search Capability**
- Product Database: Search curated Amazon product data using semantic similarity
- Internet Search: Real-time web search for trends, reviews, and general information

🚀 **Fast & Cost-Effective**
- Free Groq API for LLM inference (much faster than typical APIs)
- Local embeddings using HuggingFace models (no API calls needed)
- CPU-compatible vector storage with FAISS

🤖 **Intelligent Agent**
- ReAct framework for transparent reasoning
- Automatic tool selection based on query type
- Error handling and fallback mechanisms

📊 **Production-Ready Data**
- Amazon sales dataset with 1000+ products
- Rich metadata: prices, ratings, categories, descriptions

## How to Get Started

### Prerequisites

- Python 3.8+
- Access to Google Colab (recommended) or local Jupyter environment
- API Keys for:
  - [Kaggle API](https://www.kaggle.com/settings/account) (for dataset)
  - [Groq API](https://console.groq.com) (for LLM)
  - [Serper API](https://serper.dev) (for web search)

### Installation

1. **Clone or open the notebook** in Google Colab:
   - Upload `Chatbot_RAG_ECommerce.ipynb` to Google Colab
   - Or run locally with Jupyter Notebook

2. **Install required packages** (automatically handled in the notebook):
   ```bash
   pip install langchain langchain-groq langchain_community langchain-core \
       langchain-huggingface langchain_text_splitters google-search-results \
       pandas kaggle sentence-transformers faiss-cpu ipywidgets
   ```

3. **Configure API Keys**:
   - In Google Colab: Use the "Secrets" feature to add your API keys
   - Locally: Set environment variables or modify the notebook cells

### Quick Start

1. **Run the notebook cells in order**:
   - Installation of dependencies
   - Importing libraries
   - API key configuration
   - Dataset download from Kaggle
   - RAG vector store setup
   - Tool configuration
   - Agent initialization
   - Interactive chatbot execution

2. **Start chatting**:
   ```
   You: What are the best wireless headphones under $50?
   Bot: [Searches product database, analyzes results, provides answer]
   
   You: q  # Type 'q' or 'quit' to exit
   ```

### Example Queries

- "Show me laptop recommendations with 16GB RAM"
- "What are the latest smartphone reviews?"
- "Find the highest-rated tablets in the database"
- "Compare prices for 4K TVs"
- "Which products have the best customer ratings?"

## Architecture

```
User Query
    ↓
[ReAct Agent with Groq LLM]
    ↓
    ├─→ [Product Database Tool] → FAISS Vector Store
    │   (Semantic search on Amazon products)
    │
    └─→ [Internet Search Tool] → Google Serper API
        (Real-time web information)
    ↓
[Response Generation & Reasoning]
    ↓
User Response
```

## Key Components

- **LLM**: Groq's Llama 3.3 70B (free, ultra-fast inference)
- **Embeddings**: HuggingFace's all-MiniLM-L6-v2 (local, fast)
- **Vector Store**: FAISS (efficient similarity search)
- **Framework**: LangChain with ReAct agent pattern
- **Data Source**: Amazon Sales Dataset (Kaggle)

## Where to Get Help

- **Documentation**: Refer to inline comments in the notebook
- **LangChain Docs**: https://python.langchain.com/
- **Groq API Docs**: https://console.groq.com/docs
- **FAISS Guide**: https://github.com/facebookresearch/faiss

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes and test thoroughly
4. Commit your changes (`git commit -m 'Add improvement'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Open a Pull Request

### Areas for Contribution

- Improving prompt engineering for better responses
- Adding support for additional datasets
- Implementing caching mechanisms for faster responses
- Enhanced error handling and logging
- Performance optimizations
- UI/UX improvements (web interface, Streamlit app)

## Project Structure

```
.
├── Chatbot_RAG_ECommerce.ipynb    # Main notebook with full implementation
└── README.md                      # This file
```

## Authors & Maintainers

- Created for GDG Final Project

## Performance Notes

- **Dataset processing**: ~2-5 minutes (depends on connection)
- **Vector store creation**: ~3-10 minutes (depends on document count)
- **Query response time**: ~2-10 seconds (depends on Groq API load)
- **Memory usage**: ~1-2 GB for full vectorstore

## Future Enhancements

- [ ] Support for multiple product databases
- [ ] Conversation memory for multi-turn interactions
- [ ] User feedback collection for continuous improvement
- [ ] Analytics dashboard for query tracking
- [ ] Multi-language support
- [ ] Web interface or Telegram bot integration
- [ ] Deployment on cloud platforms (Azure, AWS, GCP)

---

**Last Updated**: November 2025

For questions or issues, please open a GitHub issue or contact the maintainers.
