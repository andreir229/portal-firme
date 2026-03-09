# 🏢 Portal Firme

**Portal Firme** is a lightweight, high-performance web application designed for browsing and analyzing Romanian company records. It integrates data from the National Trade Register Office (ONRC) and the Ministry of Finance (MFinante) to provide a comprehensive view of business entities.

---

## ✨ Features

-   **🔍 Fast Search:** Instantly search for companies by name or CUI.
-   **📄 Detailed Company Profiles:** Access registration data, addresses, and status from ONRC.
-   **📊 Financial History:** View multi-year financial data (e.g., balance sheets) sourced from MFinante.
-   **🚀 High Performance:** Pre-loads datasets into memory for instantaneous query responses.
-   **🗺️ Automatic Labeling:** Maps cryptic financial field IDs to human-readable Romanian labels.

---

## 🛠 Tech Stack

-   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
-   **Data Processing:** [Pandas](https://pandas.pydata.org/)
-   **Frontend:** Vanilla HTML5, CSS3, and JavaScript (ES6+)
-   **Server:** [Uvicorn](https://www.uvicorn.org/)

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/andreir229/portal-firme.git
    cd portal-firme
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```
Open your browser and navigate to `http://localhost:8000`.

---

## 📂 Project Structure

-   `main.py`: The FastAPI application entry point, handling routing and data loading.
-   `src/`: Contains data processing logic and raw data files.
    -   `onrc/`: ONRC dataset (`od_firme.csv`).
    -   `mfinante/`: Multi-year financial data and label mappings.
-   `static/`: Frontend assets (HTML, CSS, JS).
-   `requirements.txt`: Project dependencies.

---

## 📊 Data Sources

### ONRC (Open Data)
Used for basic entity information. The application parses `od_firme.csv` using a specialized delimiter (`^`) to ensure data integrity.

### MFinante
Used for financial indicators. Data is loaded from CSV/TXT pairs, where CSV files contain field mappings and TXT files contain the actual values. The application currently supports 2023 and 2024 reports.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License.
