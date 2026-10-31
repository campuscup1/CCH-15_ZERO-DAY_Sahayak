# 🇮🇳 SAHAYAK (सहायक)
### Your Benefits. Your Opportunities.

**An Intelligent Government Welfare Scheme Discovery & Eligibility Assistance Platform**

<p align="center">
  <strong>TEAM ZERRODAY</strong>
</p>

---

## 📌 About the Project

SAHAYAK (सहायक) is a web-based platform designed to help Indian citizens discover government welfare schemes and understand their eligibility.

Many citizens miss out on government benefits because they are unaware of available schemes, struggle to understand eligibility criteria, or do not know which documents are required.

SAHAYAK aims to simplify this process through a unified platform that helps users discover schemes, check eligibility, identify missing requirements and compare available benefits.

## 🎯 Problem Statement

Citizens face several challenges when accessing government welfare schemes:

- Limited awareness of available government schemes.
- Complicated eligibility criteria.
- Scheme information scattered across different sources.
- Uncertainty about required documents.
- Difficulty understanding why they may not qualify for a scheme.

## 💡 Our Solution

SAHAYAK provides a simple and accessible platform where citizens can:

- Discover relevant government welfare schemes.
- Enter their personal details to assess eligibility.
- Understand eligibility conditions.
- Identify missing information and unmet requirements.
- Check required documents.
- Compare different government schemes.

## 👥 Target Users

- Students seeking educational scholarships.
- Farmers looking for agricultural benefits.
- Women seeking government welfare support.
- Economically weaker sections.
- Indian citizens looking for government benefits.

## ✨ Key Features

### 1. Citizen Dashboard
Provides an overview of the user's profile, scheme matches and important information.

### 2. Citizen Profile
Allows users to enter relevant details such as age, state, annual income, education and category.

### 3. Discover Schemes
Enables users to browse, search and filter available government schemes.

### 4. My Matches
Displays schemes according to three eligibility categories:
- Match
- Potential Match
- Not Match

### 5. Eligibility Gap Analyzer
Identifies missing information and unmet eligibility conditions, helping users understand what they need to provide or fulfil.

### 6. What-if Simulator
Allows users to temporarily modify profile details and explore how those changes may affect eligibility without overwriting their saved profile.

### 7. Document Readiness
Displays required documents and allows users to track their document checklist completion.

### 8. Scheme Comparison
Helps users compare multiple schemes based on eligibility conditions, benefits and requirements.

## ⚙️ Eligibility Classification

SAHAYAK uses three categories to communicate preliminary eligibility results:

| Category | Meaning |
|---|---|
| 🟢 Match | All mandatory eligibility conditions are satisfied. |
| 🟡 Potential Match | Some required information is missing, so eligibility cannot be fully determined. |
| 🔴 Not Match | At least one mandatory eligibility condition is not satisfied. |

**Important:** Missing information is not automatically treated as a failed eligibility condition.

## 🛠️ Technology Stack

### Frontend
- **HTML5** – Website structure.
- **CSS3** – Styling, layouts, animations and responsive design.
- **Vanilla JavaScript** – Website functionality and interactions.
- **Fetch API** – Frontend-backend communication.
- **LocalStorage** – Browser-based storage for demo profile information and preferences.
- **Lucide Icons** – Interface icons.
- **Google Fonts** – Typography.

### Backend
- **Python** – Backend programming language.
- **FastAPI** – REST API development.
- **Pydantic** – Data validation and schema management.
- **Rule-based Eligibility Engine** – Evaluates scheme eligibility conditions.
- **Configurable Scheme Catalogue** – Organises scheme information and eligibility rules.

### Tools & Deployment
- **Git & GitHub** – Version control and collaboration.
- **Vercel** – Frontend deployment.
- **REST APIs** – Communication between frontend and backend.
- **JSON** – Data exchange format.

## 🏗️ Project Structure

```text
saha/
│
├── assets/
│   └── Images and other static assets
│
├── backend/
│   └── Python FastAPI application
│
├── css/
│   └── Stylesheets
│
├── js/
│   └── JavaScript files and API integration
│
├── index.html
├── dashboard.html
├── profile.html
├── schemes.html
├── matches.html
├── gap-analyzer.html
├── simulator.html
├── documents.html
├── compare.html
│
└── README.md
```

## 🔄 How SAHAYAK Works

1. **Profile Input:** Citizens enter their relevant personal details.
2. **API Request:** The frontend sends the information to the backend using JavaScript Fetch API.
3. **Data Validation:** FastAPI receives and validates the submitted information.
4. **Eligibility Evaluation:** The rule-based engine compares the user's profile against configured scheme eligibility conditions.
5. **Result Generation:** The backend returns the eligibility results and relevant information in JSON format.
6. **Result Display:** The frontend displays matching schemes, missing requirements and other relevant details.

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- Python
- Git
- Visual Studio Code or another code editor.
- A modern web browser.

### 1. Clone the Repository

```bash
git clone https://github.com/samarthtalwar9/saha.git
cd saha
```

### 2. Run the Frontend

From the project root directory, start a local server:

```bash
python -m http.server 5500
```

Open the following address in your browser:

```text
http://localhost:5500
```

### 3. Run the Backend

Open another terminal and navigate to the backend directory:

```bash
cd backend
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application using the correct entry point.

For example, if the application instance is named `app` inside `main.py`:

```bash
uvicorn main:app --reload
```

The backend will generally be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation, if enabled, can be accessed at:

```text
http://127.0.0.1:8000/docs
```

**Note:** Adjust the backend start command according to the actual application entry point and project configuration.

## 🔮 Future Scope

SAHAYAK can be extended with:

- Multilingual support for Indian regional languages.
- Integration with verified government scheme data sources.
- Expanded coverage of government welfare schemes.
- Improved accessibility for different user groups.
- User accounts and secure profile management.
- Notifications about relevant scheme updates.
- Enhanced mobile accessibility.

## ⚠️ Disclaimer

SAHAYAK is an informational prototype developed to simplify government scheme discovery and preliminary eligibility understanding.

- It does not guarantee government scheme approval.
- It does not automatically submit government applications.
- Scheme information should be verified against official government sources.
- Final eligibility verification and approval remain the responsibility of the concerned government authorities.

---

## 👨‍💻 Team ZERRODAY

**Built with dedication by Team ZERRODAY.**

| Team Members |
|---|
| Samarth Talwar |
| Yash Yadav |
| Aditya Gaikwad |
| Zeenath Shaikh |

<p align="center">
  <strong>SAHAYAK (सहायक)</strong><br/>
  Your Benefits. Your Opportunities.<br/><br/>
  <strong>TEAM ZERRODAY 🇮🇳</strong>
</p>
