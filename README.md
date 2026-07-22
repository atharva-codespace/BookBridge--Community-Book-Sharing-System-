# BookBridge

BookBridge is a console-based **Used Book Resale Platform** built with pure Python and SQLite (no web or GUI frameworks). It lets users buy, sell, reserve, and review books through an interactive command-line interface, with dedicated dashboards for **Users**, **Administrators**, and **Delivery Boys** - plus AI-powered assistance, analytics, automated PDF reports, and secure authentication.

---

## Problem Statement

Students and book readers often have books they no longer need, while others struggle to find the same books at affordable prices. Most existing platforms only support buying and selling, and lack features like, reservations, wishlist management, delivery tracking, and centralized administration.

BookBridge addresses this by giving users a single place to sell, reserve, and discover books, while giving administrators the tools to manage the entire system end to end.

---

## Features

### User Module
- Registration with OTP email verification
- Secure login with bcrypt password hashing
- Profile and preference management (notifications, location)
- Buy, sell books
- Book search with filters (title, author, ISBN, category, price, location, condition, edition)
- Wishlist management
- Book reservation and request workflow
- Submit reviews & ratings, view personal review history
- AI-powered book recommendations
- AI grammar/spelling enhancement for reviews

### Administrator Module
- User management (activate, deactivate, delete, promote, search)
- Book management and moderation
- Review moderation
- Request & reservation oversight (approve/reject, force-expire)
- Delivery management (register delivery boys, assign deliveries)
- Analytics dashboard with charts
- PDF report generation and automatic email delivery

### Delivery Boy Module
- Secure login
- View assigned deliveries
- Update delivery status (Picked Up -> Delivered)

### AI Features
- **AI Project Assistant** - a chatbot on the main menu that answers only questions about using BookBridge (buying, selling, reservations, wishlist, delivery, registration, login, etc.) and politely declines anything unrelated.
- **AI Book Recommendation** - suggests books to a buyer based on their wishlist, past purchases, and favourite categories/authors, choosing only from books that actually exist in the database.
- **AI Review Enhancement** - corrects grammar and spelling in a submitted review before it's saved, while preserving its original meaning and sentiment.

The AI features run on a multi-provider fallback chain (Gemini -> Groq -> OpenRouter -> Cerebras): if one provider is unavailable or rate-limited, the next one is tried automatically, so the app keeps working even on free-tier limits.

---

## Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python 3 |
| Database | SQLite |
| Terminal UI | Rich (+ pyfiglet for the banner) |
| Password Security | Bcrypt |
| AI Integration | Gemini, Groq, OpenRouter, Cerebras (automatic fallback chain) |
| Environment Variables | python-dotenv |
| Data Visualization | Matplotlib |
| PDF Report Generation | ReportLab |
| Email Services | SMTP (Gmail) |

---

## Project Structure

```
BookBridge/
├── database/
│   └── db.py                                 # SQLite connection singleton
├── models/                                   # Data access layer (one file per entity)
│   ├── user.py, admin.py, delivery_boy.py
│   ├── book.py, book_request.py, reservation.py, wishlist.py, review.py
│   ├── notification.py, delivery.py
│   └── analytics.py, reports.py, mail.py
├── services/                                 # Business logic layer
│   ├── authentication.py, authorization.py, registration.py
│   ├── otp_service.py, password.py, profile.py
│   ├── book_management.py, request_service.py, review_service.py
│   ├── admin_management.py, delivery_management.py, delivery_service.py
│   ├── report_service.py, validation.py
│   └── ai_client.py, ai_chatbot.py, ai_recommendation.py, ai_review.py
├── utils/                                    # Shared helpers
│   ├── ui.py                                 # Rich-based terminal presentation layer
│   ├── menus.py                              # Every menu screen
│   ├── helpers.py, hashing.py, email_sender.py
├── Reports/                                  # Generated charts and PDF reports
├── book_bank.db                              # SQLite database (ships pre-seeded)
├── main.py                                   # Entry point
├── requirements.txt
├── .env                                      # API keys and config (not committed)
└── README.md
```

---

## How to Run the Project

**1. Get the project**


**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Database**

`book_bank.db` ships with the project, already containing every table and some sample data, so no setup step is required. Every sample account uses the password `Password123!`. If you'd rather point the app at a different SQLite file, edit `Database.DB_PATH` in `database/db.py`.

**4. Configure environment variables**

Create a `.env` file in the project root with your AI provider keys:

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
CEREBRAS_API_KEY=your_cerebras_key
```

All four are optional and independent - the AI features fall back gracefully (Gemini -> Groq -> OpenRouter -> Cerebras) and the rest of the app works normally even with none configured.

**5. Run the application**

```bash
python main.py
```

On the very first run, if no administrator account exists yet, the program walks you through creating one before showing the main menu.

---

## Team Members & Responsibilities

BookBridge is organized into 7 modules across a 6-person team.

| Team Member | Module(s) | Focus |
|---|---|---|
| **Atharva Deshmukh** ( | 1 & 7 | Authentication, OTP verification, sessions, profile & preferences, shared database/authorization infrastructure, and Delivery Management |
| **Riddhi** | 2 | Book Inventory & Listing Management |
| **Yash** | 3 | Book Search & Discovery |
| **Shaista** | 4 | Requests, Reservations, Wishlist & Notifications |
| **Dnyaneshwar** | 5 | Reviews & Ratings |
| **Mayuri** | 6 | Administrative Dashboard & Analytics |

## Project Modules
**Atharva Deshmukh - Modules 1 & 7 (Team Lead)**
Owns account registration and OTP-based email verification, login routing across all three account types, session and mode management, profile and preference handling, password recovery, and the shared database and authorization infrastructure. Also owns Delivery Management: delivery boy account administration, delivery-record creation, assignment, and status tracking.

**Riddhi - Module 2**
Owns the book inventory lifecycle - adding, viewing, editing, and soft-deleting listings - along with the logic that ties a listing's Sale/Buy type to the owner's active session mode.

**Yash - Module 3**
Owns book discovery: browsing all listings or listings for sale, and the unified search function covering title, author, ISBN, category, price range, availability, location, condition, and edition.

**Shaista - Module 4**
Owns requests, reservations, wishlist, and notifications - including the admin approval queue, the competing-claim workflow between simultaneous buyers, and the handoff into Delivery once a request is approved.

**Dnyaneshwar - Module 5**
Owns rating and feedback submission, eligibility checks tied to a reviewer's own request history, personal review history, and the admin-side review moderation tools.

**Mayuri - Module 6**
Owns the administrative dashboard: user and book moderation, requests/reservations oversight, and the six-report analytics suite with its tables, charts, PDF generation, and automatic email delivery.

---

## Security Features

- OTP email verification at registration
- Bcrypt password hashing (passwords are never stored in plain text)
- Password recovery via security question
- Parameterized SQL queries (SQL injection protection)
- Soft delete support (`Is_Deleted` flag) so history/audit data is preserved
- Session-based access control (User / Admin / Delivery Boy)

---

## Reports & Analytics

The Admin Dashboard's "See All Reports" generates, on demand:

- Users Report
- Books Report
- Requests Report
- Reservations Report
- Reviews Report
- Wishlist Report

Each report shows a summary and chart on screen, saves a PDF to the `Reports/` folder, and emails the PDF to the logged-in admin automatically.

---

## Project Highlights

- Modular Python architecture (clean separation of models, services, and utils)
- Polished console UI built with Rich - panels, tables, colors, spinners
- Secure authentication with OTP and bcrypt
- AI-powered assistant, recommendations, and review enhancement with automatic provider fallback
- Automated analytics, charts, and PDF reports emailed to admins
- Full delivery lifecycle tracking

---

## Future Enhancements

- Book image upload
- Barcode/QR code integration
- Mobile application
- Online payment gateway
- Real-time notifications
- Machine-learning-based recommendation engine
- Multi-language support

---
