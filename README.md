# 🇮🇳 SAHAYAK (सहायक)
### Your Benefits. Your Opportunities.

**An intelligent Government Welfare Scheme Discovery & Eligibility Assistance Platform**

<p align="center">
  <strong>Team ZERRODAY</strong>
</p>

<p align="center">
  <a href="https://saha-chi.vercel.app/">🌐 Live Demo</a> •
  <a href="https://github.com/samarthtalwar9/saha">💻 GitHub Repository</a>
</p>

---

## 📌 About the Project

SAHAYAK (सहायक) is a web-based platform designed to help Indian citizens discover government welfare schemes and understand their eligibility.

Many citizens miss out on government benefits because they are unaware of available schemes, struggle to understand eligibility criteria, or do not know which documents are required.

SAHAYAK aims to simplify this process through a unified platform that helps users discover schemes, check eligibility, identify missing requirements and compare benefits.

## 🎯 Problem We Solve

- Limited awareness of government welfare schemes.
- Complicated eligibility conditions.
- Scheme information scattered across multiple sources.
- Uncertainty about required documents.
- Difficulty understanding eligibility gaps.

## 💡 Our Solution

SAHAYAK provides a simple and accessible platform where citizens can explore schemes, enter their profile details and understand which schemes may be relevant to them.

## ✨ Key Features

| Feature | Description |
|---|---|
| Citizen Dashboard | Overview of profile and scheme information |
| Citizen Profile | Enter personal and eligibility-related details |
| Discover Schemes | Browse, search and filter schemes |
| My Matches | View scheme eligibility results |
| Gap Analyzer | Identify missing information and unmet conditions |
| What-if Simulator | Explore how temporary profile changes affect eligibility |
| Document Readiness | Track required documents |
| Scheme Comparison | Compare schemes and their requirements |

## ⚙️ Eligibility Classification

SAHAYAK uses three eligibility categories:

- 🟢 **Match:** All mandatory eligibility conditions are satisfied.
- 🟡 **Potential Match:** Some required information is missing, so eligibility cannot be fully determined.
- 🔴 **Not Match:** At least one mandatory eligibility condition is not satisfied.

Missing information is not automatically treated as failed eligibility.

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- Browser LocalStorage
- Lucide Icons

### Backend
- Python
- FastAPI
- Pydantic
- Rule-based Eligibility Engine

### Tools & Deployment
- Git and GitHub
- Vercel
- REST APIs
- JSON

## 🏗️ Project Structure

```text
saha/
│
├── assets/
│
├── backend/
│   └── Backend application and modules
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

## 🔄 How It Works

1. Citizens enter their relevant profile information.
2. The frontend sends information to the backend through API requests.
3. The backend validates the submitted information.
4. The eligibility engine evaluates the profile against scheme conditions.
5. Eligibility results and relevant information are returned.
6. The frontend presents the results in an understandable format.

## 🚀 Getting Started

### Prerequisites

- Python installed.
- A modern web browser.
- Git.
- A code editor such as Visual Studio Code.

### 1. Clone the Repository

```bash
git clone https://github.com/samarthtalwar9/saha.git
cd saha
```

### 2. Run the Frontend

From the project root, start a local static server:

```bash
python -m http.server 5500
```

Open:

```text
http://localhost:5500
```

### 3. Run the Backend

Navigate to the backend directory:

```bash
cd backend
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application using the actual application entry point configured in the backend project.

For example, if the application instance is named `app` in `main.py`:

```bash
uvicorn main:app --reload
```

FastAPI documentation, when enabled, is available at:

```text
http://127.0.0.1:8000/docs
```

**Note:** Backend commands and dependencies should match the actual files and application entry point in the repository.

## 🌐 Live Demo

Explore SAHAYAK:

https://saha-chi.vercel.app/

## 🔮 Future Scope

- Support for more government welfare schemes.
- Multilingual support for Indian regional languages.
- Integration with verified government data sources.
- Improved accessibility.
- Scheme update notifications.
- Enhanced citizen profile management.

## ⚠️ Disclaimer

SAHAYAK is an informational prototype developed to simplify government scheme discovery and preliminary eligibility understanding.

It does not guarantee eligibility or government approval and does not automatically submit applications. Final eligibility verification and approval remain with the concerned government authorities.

---

## 👥 Team ZERRODAY

**Built with dedication by Team ZERRODAY.**

| Team Member |
|---|
| Samarth Talwar |
| Yash Yadav |
| Aditya Gaikwad |
| Zeenath Shaikh |

<p align="center">
  <strong>SAHAYAK (सहायक)</strong><br/>
  Your Benefits. Your Opportunities.<br/><br/>
  <strong>Team ZERRODAY 🇮🇳</strong>
</p>
