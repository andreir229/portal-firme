# Portal Firme

A lightweight web application for browsing Romanian company records from the ONRC dataset.

## 🛠 Tech Stack
- **Backend:** Python (FastAPI)
- **Data Processing:** Pandas
- **Database:** None (Flat-file CSV: `od_firme.csv`)

## 🚀 How to Run
1. Clone the repository: `git clone https://github.com/andreir229/portal-firme.git`
2. Install dependencies: `pip install fastapi uvicorn pandas`
3. Start the server: `uvicorn main:app --reload`

## 📊 Data Source
The application parses `od_firme.csv` using `^` as a delimiter. 
The data includes CUI, registration dates, and full addresses.
