# Lesson Planner 📝  

An AI-powered **Lesson Planner** built with Python and the Groq API.  
This project helps generate, organize, and manage lesson plans quickly and efficiently.  

---

## 🚀 Features
- Generate lesson plans with AI.  
- Simple and easy-to-use interface.  
- Environment-based configuration for security.  
- Powered by [Groq API](https://console.groq.com/).  

---

## 📦 Installation  

Follow these steps to set up and run the project locally:

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/lesson-planner.git
cd lesson-planner
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

* **Windows (PowerShell):**
  ```bash
  venv\Scripts\activate
  ```
* **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Install Dependencies  

First, install the dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

If you face issues with missing libraries, install them manually using:
```bash
pip install streamlit python-dotenv langchain-core langchain-groq reportlab
```

---

## 🔑 Setup Groq API Key  

This project uses the **Groq API**, and each user must use their own API key.  
Follow these steps to set it up:

1. Go to the [Groq Console](https://console.groq.com/) and create an account (if you don’t have one already).  
2. Generate your **API Key** from the dashboard.  
3. In your project folder, create a file named `.env`.  
4. Add the following line inside the `.env` file:  

   ```env
   KEY=your_api_key_here
   ```

---

## ▶️ Running the Project  

Once everything is set up, run the project with:

```bash
python main.py
```

If using **Streamlit UI**, run:

```bash
streamlit run main.py
```

---

## 📂 Project Structure  

```
lesson-planner/
│── main.py               # Entry point of the application
│── requirements.txt      # Python dependencies
│── .gitignore            # Ignored files (e.g., __pycache__, .env)
│── README.md             # Project documentation
│── /__pycache__/         # Auto-generated cache (ignored)
```

---

## ⚡ Troubleshooting  

* If you see missing module errors, re-run:
  ```bash
  pip install -r requirements.txt
  ```
* If that doesn’t fix it, try:
  ```bash
  pip install streamlit python-dotenv langchain-core langchain-groq reportlab
  ```
* Make sure your `.env` file exists and contains your Groq API key.  

---

## 🤝 Contributing  

Contributions are welcome! Feel free to fork the repo and submit a pull request.
