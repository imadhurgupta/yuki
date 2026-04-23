# PROJECT REPORT

---

## Yuki — Custom Merchandise E-Commerce Web Application

---

| | |
|---|---|
| **Project Title** | Yuki — Custom Merchandise Online Store |
| **Technology Stack** | Python, Flask, SQLite, HTML5, CSS3, Bootstrap 5, Docker |
| **Type** | Full-Stack Web Application |
| **Date** | March 2026 |

---

## Table of Contents

1. Introduction
2. Objectives
3. Technology Stack
4. System Architecture
5. Database Design
6. Module Description
   - 6.1 Authentication Module
   - 6.2 User / Customer Module
   - 6.3 Admin Module
7. Key Features
8. Application Routes (URL Map)
9. Deployment & Infrastructure
10. Security Considerations
11. Future Scope
12. Conclusion

---

## 1. Introduction

**Yuki** is a full-stack e-commerce web application developed to digitize the operations of a custom merchandise printing business based in Jaipur, India. The platform enables customers to browse, customize, and order printed products such as T-shirts, hoodies, mugs, and more, directly through a web browser.

The project was built entirely from scratch using the **Python Flask micro-framework** and follows the **MVC (Model-View-Controller)** architectural pattern. It provides two distinct user experiences:

- A **customer-facing storefront** where visitors can browse products, manage a shopping cart, and place orders.
- A **secure admin dashboard** where the business owner can manage the entire product catalogue, process orders, handle customers, and configure site settings.

The application is containerized using **Docker**, making it easy to deploy consistently across different environments.

---

## 2. Objectives

The primary objectives of this project are:

1. **Digitize a Physical Business** — Provide an online platform for Yuki to reach customers beyond walk-in clientele.
2. **End-to-End Order Management** — Allow customers to place orders and track them, while giving the admin full control over order status updates.
3. **Secure Authentication** — Implement a robust, multi-layered authentication system including OTP email verification and Google OAuth (Social Login).
4. **Custom Merchandise Workflow** — Support the business-specific requirement of accepting customization file uploads, advance payments, and bulk-order discounts.
5. **Self-Serve Admin Panel** — Empower the non-technical business owner to manage products, banners, coupons, and categories without any coding knowledge.
6. **Production-Ready Deployment** — Package the application with Docker and Gunicorn for stable, scalable deployment.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Language** | Python 3.10 | Core application logic |
| **Web Framework** | Flask | Routing, request handling, blueprint management |
| **ORM** | Flask-SQLAlchemy | Database abstraction & model definition |
| **Database** | SQLite | Persistent data storage (local file-based) |
| **Authentication** | Flask-Login | Session management for logged-in users |
| **Password Security** | Werkzeug | Password hashing using PBKDF2-SHA256 |
| **Social Login** | Authlib (Google OAuth 2.0) | "Sign in with Google" functionality |
| **Email Service** | Flask-Mail (Gmail SMTP) | OTP delivery, order notifications |
| **Token Security** | itsdangerous | Signed, time-limited session tokens |
| **Frontend** | HTML5 + CSS3 + Bootstrap 5 | Responsive, mobile-first UI |
| **Icons** | Font Awesome 6 | UI icon library |
| **Environment Config** | python-dotenv | Loading secrets from `.env` file |
| **WSGI Server** | Gunicorn | Production-grade Python web server |
| **Containerization** | Docker + Docker Compose | Portable deployment environment |

---

## 4. System Architecture

The application follows a strict **Model-View-Controller (MVC)** architecture, implemented using Flask Blueprints for modularity.

### Project Directory Structure

```
yuki/
|
|-- app.py                  # Application factory, extension init, blueprint registration
|-- extensions.py           # Shared extensions (db, mail, oauth)
|-- models.py               # All SQLAlchemy database models (M)
|
|-- routes/                 # URL routing layer (thin, delegates to controllers)
|   |-- auth_routes.py      # /login, /register, /google/*, /forgot-password
|   |-- user_routes.py      # /, /shop, /cart/*, /checkout/*, /profile
|   `-- admin_routes.py     # /admin/dashboard, /admin/products/*, /admin/orders/*
|
|-- controllers/            # Business logic layer (C)
|   |-- auth_controller.py  # Registration, Login, OTP, Google OAuth, Password Reset
|   |-- user_controller.py  # Shop, Cart, Checkout, Orders, Profile, Reviews
|   `-- admin_controller.py # Product CRUD, Order Management, Site Settings
|
|-- templates/              # Jinja2 HTML templates (V)
|   |-- layouts/            # base.html, navbar.html, footer.html
|   |-- guest/              # Public pages: home, shop, product detail, about, contact
|   |-- user/               # Authenticated pages: profile, cart, checkout, invoice
|   `-- admin/              # Admin-only pages: dashboard, order detail
|
|-- static/
|   |-- css/                # Custom stylesheets
|   `-- uploads/            # User-uploaded files (product images, payment proofs, QR)
|
|-- Dockerfile              # Docker image definition
|-- docker-compose.yaml     # Service orchestration
|-- entrypoint.sh           # Container startup script
`-- requirements.txt        # Python dependencies
```

### Architecture Diagram — Request Lifecycle

```
Browser / Client
     |
     |  HTTP Request
     v
[ Flask Router (Blueprints) ]
     |
     |  Delegates to
     v
[ Controller Function ]
     |           |
     v           v
[ Models ]   [ Templates ]
(SQLAlchemy)  (Jinja2)
     |
     v
[ SQLite Database ]
     |
     v
HTTP Response --> Browser
```

---

## 5. Database Design

The application uses **10 SQLAlchemy models** mapped to SQLite database tables.

### Entity Relationship Summary

| Model | Key Fields | Relationships |
|---|---|---|
| **User** | id, full_name, email, password_hash, is_admin, address, mobile | Has many Orders, Cart items |
| **Product** | id, name, base_price, section, category, sizes, stock, advance_percentage, bulk_min_qty | Has many ProductImages, Reviews |
| **ProductImage** | id, image_file, product_id | Belongs to Product (cascade delete) |
| **Order** | id, transaction_id, total_price, status, payment_method, customization_file, payment_proof, advance_amount | Belongs to User, Product |
| **Cart** | id, user_id, product_id, quantity, size | Belongs to User, Product |
| **Carousel** | id, title, subtitle, image_file, link | Standalone (homepage banners) |
| **SiteSetting** | id, qr_code_file, upi_id | Singleton record |
| **Review** | id, product_id, user_id, rating, comment, media_file, date_posted | Belongs to Product, User |
| **Coupon** | id, code, discount_percentage, is_active, applicable_category | Standalone |
| **Category** | id, name, image_file | Standalone (shop navigation) |

### Notable Design Decisions

- **Password Security**: Passwords are never stored in plaintext. The `User` model uses a Python `@property` setter to automatically apply `werkzeug.security.generate_password_hash` (PBKDF2-SHA256) before any value touches the database.

- **Order Snapshots**: The `Order` model stores the customer's name, email, address, and mobile at the time of purchase. This ensures that even if a user updates their profile later, historical order records remain accurate.

- **Cascade Deletes**: `ProductImage` records are set with `cascade="all, delete-orphan"`, ensuring that all gallery images are automatically removed from the database when a product is deleted.

- **Bulk Discount Logic**: A `get_price_for_quantity()` method on the `Product` model encapsulates the discount calculation, keeping business logic in the model layer rather than in controllers or templates.

---

## 6. Module Description

### 6.1 Authentication Module (`auth_controller.py`)

This module handles all identity and access management features.

**Registration Flow:**
1. User fills the registration form (Name, Email, Password).
2. The controller validates the email format using a regular expression.
3. It checks for duplicate emails in the database.
4. A **6-digit OTP** is generated, stored in the Flask session, and sent to the user's email asynchronously (using a Python `Thread` to avoid blocking the HTTP response).
5. Upon correct OTP entry, the user account is committed to the database. If the registered email matches the `ADMIN_EMAIL` environment variable, the user is automatically granted admin privileges.

**Login Flow:**
- Regular customers are logged in directly upon correct credentials using `flask_login.login_user()`.
- Admin users are subjected to an additional **OTP verification step** for enhanced security before being directed to the admin dashboard.

**Google OAuth (Social Login):**
- Implemented using the **Authlib** library with Google's OpenID Connect standard.
- Users can sign in without a password. If the Google account email is new, a user record is created automatically.
- The admin email check is also applied during Google login to correctly assign admin privileges.

**Password Reset Flow:**
1. User submits their email at `/forgot-password`.
2. A time-limited OTP is sent to their email via a background thread.
3. After OTP verification, the user is allowed to set a new password.
4. Session flags (`reset_verified`, `reset_email`) guard against unauthorized access to the password-setting endpoint.

---

### 6.2 User / Customer Module (`user_controller.py`)

This is the largest module and manages all customer-facing functionality.

**Home Page (`/`):**
- Fetches active carousel banners and the 8 most recent products from the database.
- Renders dynamic product category sections based on the `Product.section` field.

**Shop Page (`/shop`):**
- Supports URL-parameter-based filtering by `section` and `category`.
- Products are displayed in a responsive grid with pricing and direct navigation to the product page.

**Product Detail Page (`/product/<id>`):**
- Shows full product information including a multi-image gallery.
- Displays the calculated price based on the requested quantity (bulk discount logic embedded in the model).
- Allows authenticated users to submit star ratings and reviews with optional media attachments.

**Shopping Cart (`/cart`):**
- Persistent, database-backed cart tied to the logged-in user.
- Supports adding, removing, and quantity management.
- Coupon code application via an AJAX endpoint (`/cart/apply_coupon`) that returns a JSON response to update the UI dynamically without a page reload.

**Checkout System:**
The application supports two distinct checkout flows:
1. **Direct / Buy Now** (`/checkout/<product_id>`): For purchasing a single product immediately.
2. **Cart Checkout** (`/cart/checkout`): For purchasing all items in the cart at once.

Both flows collect delivery address, size, quantity, customization instructions, and support uploading a customization design file (PNG, JPG, PDF, ZIP — up to 20 MB).

**Payment System (`/payment/<order_id>`):**
- Supports two payment methods: **Cash on Delivery (COD)** and **UPI/Online**.
- For UPI payments, the page displays the business's QR code (managed by admin from the dashboard).
- Customers upload a **payment screenshot** as proof, which is stored in the uploads directory.
- The system supports **advance payments**: a configurable percentage of the total order value is collected upfront, with the balance due on delivery.

**User Profile (`/profile`):**
- Displays the user's saved address and contact information.
- Shows a full order history with current status indicators.
- Allows the user to generate a **printable invoice** for any completed order.

---

### 6.3 Admin Module (`admin_controller.py`)

The admin module is protected and accessible only to users with `is_admin=True`. All admin routes are prefixed with `/admin`.

**Admin Dashboard (`/admin/dashboard`):**
A single-page control center that provides:

- **Summary Statistics** — Total Revenue, Total Orders, Total Customers, Pending Orders count.
- **Order Management** — Full order list with one-click status updates (Pending → Processing → Shipped → Delivered) and links to view detailed receipts.
- **Product Inventory Management** — Add, edit, and delete products with multi-image gallery upload support, pricing, stock levels, and bulk discount configuration.
- **Carousel / Banner Management** — Add, edit, and delete homepage slideshow banners with images, titles, subtitles, and call-to-action links.
- **Category Management** — Manage product categories with custom thumbnail images that appear on the storefront homepage.
- **Coupon Management** — Create promotional coupon codes with percentage discounts, toggle them active/inactive, and delete them.
- **QR Code Management** — Upload and replace the UPI payment QR code that is displayed to customers during checkout.
- **Review Moderation** — View all customer reviews and delete inappropriate ones.

---

## 7. Key Features

| # | Feature | Description |
|---|---|---|
| 1 | **Multi-Step OTP Registration** | New accounts require email verification via a 6-digit OTP sent asynchronously. |
| 2 | **Google OAuth Sign-In** | Users can register/login with their existing Google account. |
| 3 | **Admin Two-Factor Login** | Admin accounts require OTP verification on every login for enhanced security. |
| 4 | **Password Reset via OTP** | A 3-step secure password reset flow using session-guarded OTP verification. |
| 5 | **Dynamic Product Catalogue** | Fully admin-managed products with sections, categories, sizes, and gallery images. |
| 6 | **Bulk Order Discounts** | Products can have configurable bulk pricing (e.g., 20% off if quantity >= 10). |
| 7 | **Advance Payment System** | Products can require a configurable advance percentage (e.g., 40%) upfront. |
| 8 | **Customization File Upload** | Customers upload their artwork design file during checkout. |
| 9 | **Coupon/Discount System** | Admin creates discount codes with percentage off, category restrictions, and on/off toggle. |
| 10 | **AJAX Coupon Application** | Coupon codes are validated in real-time via Fetch API without page reload. |
| 11 | **Payment Proof Upload** | UPI/Online payers upload a payment screenshot for admin verification. |
| 12 | **Printable Invoice Generation** | Customers generate a branded, printable invoice for any completed order. |
| 13 | **Admin Order Management** | Admin updates order status and views full details via a dedicated receipt page. |
| 14 | **Hero Carousel Management** | Admin controls homepage banner slides (image, title, subtitle, CTA link). |
| 15 | **Star-Rated Reviews with Media** | Authenticated users post star ratings with text and optional image/video on products. |
| 16 | **Fully Responsive Design** | Built with Bootstrap 5; fully functional on mobile, tablet, and desktop screens. |
| 17 | **Docker Containerization** | The entire app is Dockerized; a single `docker compose up` launches the production server. |
| 18 | **Async Email Delivery** | All emails (OTP, notifications) are sent on background threads to avoid blocking requests. |

---

## 8. Application Routes (URL Map)

### Public Routes (Accessible to Everyone)

| Method | URL | Description |
|---|---|---|
| GET | `/` | Home page with carousel and product listings |
| GET | `/shop` | Product catalogue with category/section filters |
| GET | `/product/<id>` | Product detail page with gallery and reviews |
| GET | `/about` | About page |
| GET/POST | `/contact` | Contact form |

### Authentication Routes

| Method | URL | Description |
|---|---|---|
| GET/POST | `/register` | New user registration form |
| GET/POST | `/login` | User login form |
| GET | `/logout` | Logout and clear session |
| GET/POST | `/verify-otp/<action>` | OTP verification (for register or admin login) |
| GET | `/google/login` | Redirects to Google for OAuth |
| GET | `/google/callback` | Google OAuth callback handler |
| GET/POST | `/forgot-password` | Initiate password reset by email |
| GET/POST | `/verify-reset-otp` | Verify OTP for password reset |
| GET/POST | `/reset-new-password` | Set new password after OTP verified |

### Authenticated User Routes (Login Required)

| Method | URL | Description |
|---|---|---|
| GET | `/cart` | View shopping cart |
| POST | `/cart/add/<product_id>` | Add item to cart |
| GET | `/cart/remove/<cart_id>` | Remove item from cart |
| POST | `/cart/apply_coupon` | AJAX endpoint for coupon code validation |
| GET/POST | `/checkout/<product_id>` | Direct product checkout |
| GET/POST | `/cart/checkout` | Full cart checkout |
| GET | `/payment/<order_id>` | Payment page (COD or UPI) |
| POST | `/process-payment/<order_id>` | Submit payment proof |
| GET | `/payment/pending` | Pending payment information page |
| POST | `/process-payment/pending` | Submit payment for a pending order |
| GET | `/profile` | User profile and order history |
| POST | `/profile/update` | Update profile information |
| GET | `/order/<order_id>` | View specific order details |
| GET | `/invoice/<txn_id>` | View and print order invoice |
| POST | `/product/<id>/review` | Submit a product review |

### Admin Routes (Admin Login Required — Prefix: `/admin`)

| Method | URL | Description |
|---|---|---|
| GET | `/admin/dashboard` | Main admin control panel |
| POST | `/admin/carousel/add` | Add new homepage banner |
| GET | `/admin/carousel/delete/<id>` | Delete a banner |
| POST | `/admin/carousel/edit/<id>` | Edit a banner |
| POST | `/admin/products/add` | Add a new product |
| POST | `/admin/products/edit/<id>` | Edit a product |
| GET | `/admin/products/delete/<id>` | Delete a product |
| POST | `/admin/orders/update/<id>` | Update order status |
| GET | `/admin/orders/<txn_id>` | View order receipt |
| GET | `/admin/product/image/delete/<id>` | Delete a product gallery image |
| POST | `/admin/upload_qr` | Upload UPI QR code |
| GET/POST | `/admin/delete_qr` | Delete UPI QR code |
| POST | `/admin/coupons/add` | Create a new coupon |
| POST | `/admin/coupons/toggle/<id>` | Toggle coupon active/inactive |
| POST | `/admin/coupons/delete/<id>` | Delete a coupon |
| POST | `/admin/categories/add` | Add a new category |
| GET/POST | `/admin/categories/delete/<id>` | Delete a category |
| GET/POST | `/admin/review/delete/<id>` | Delete a customer review |

---

## 9. Deployment & Infrastructure

The application is designed for a **containerized production deployment** using Docker.

### Dockerfile

The application uses an official **Python 3.10 Slim** base image. The build process:
1. Installs system dependencies (`gcc`, `libpq-dev`) needed for the PostgreSQL adapter.
2. Installs Python packages from `requirements.txt`.
3. Copies the full application code into the `/app` working directory.
4. Exposes port 5000.
5. Sets `entrypoint.sh` as the container startup command.

### Docker Compose (`docker-compose.yaml`)

The `docker-compose.yaml` file defines the `web` service with:
- **Port Mapping**: `5000:5000` — maps host port to the container.
- **Environment Variables**: Loaded from the `.env` file (API keys, secrets).
- **Named Volume**: The `static/uploads` directory is mounted as `static_volume`, ensuring all uploaded files (product images, payment proofs, QR codes) **persist across container restarts**.

### Entrypoint (`entrypoint.sh`)

On every container startup:
1. Runs `python create_db.py` to initialize all database tables if they do not yet exist.
2. Launches **Gunicorn** (`exec gunicorn --bind 0.0.0.0:5000 app:app`), the production-grade WSGI HTTP server, to serve the Flask application to the network.

### Proxy Fix Middleware

`Werkzeug.middleware.proxy_fix.ProxyFix` is applied in `app.py`. This is essential when Flask runs behind Gunicorn inside Docker (and optionally behind an Nginx reverse proxy), ensuring correct URL generation and proper reading of forwarded client IP addresses.

---

## 10. Security Considerations

| Security Measure | Implementation |
|---|---|
| **Password Hashing** | All passwords are hashed with PBKDF2-SHA256 via Werkzeug before being stored. Plaintext passwords never enter the database. |
| **OTP Verification** | Account registration requires email OTP verification, preventing automated fake account creation. Admin logins require OTP as a second factor. |
| **Session-Based Security** | Flask's cryptographically signed, server-side sessions store OTPs and temporary state. A strong `SECRET_KEY` (from environment variables) signs all sessions. |
| **Fake Success Response** | The `/forgot-password` endpoint returns the same success response whether or not the email exists, preventing user enumeration attacks by malicious actors. |
| **Route Protection** | The `@login_required` decorator (Flask-Login) protects all authenticated user routes. Admin pages perform an explicit `is_admin` check and abort with 403 if unauthorized. |
| **File Upload Validation** | Uploaded files are checked against an allowlist of extensions (`png`, `jpg`, `jpeg`, `gif`, `pdf`, `zip`) and a maximum size of **20 MB**. |
| **Environment Variables** | All secrets (Secret Key, Google OAuth credentials, Admin Email, SMTP password) are stored in a `.env` file, never hardcoded in source code. |
| **Google OAuth via OpenID Connect** | Social login uses the secure, industry-standard OpenID Connect protocol via Authlib, eliminating direct credential handling for Google-authenticated users. |

---

## 11. Future Scope

| Enhancement | Description |
|---|---|
| **Payment Gateway Integration** | Integrate Razorpay or Stripe to process real online payments, replacing the current manual payment-proof upload system. |
| **Automated Email Notifications** | Send automated transactional emails for order confirmation, shipment updates, and payment receipts. |
| **PostgreSQL Migration** | Migrate from SQLite to PostgreSQL (the driver `psycopg2-binary` is already included) for better concurrent write performance and scalability. |
| **Full-Text Product Search** | Add a search bar using SQLAlchemy `LIKE` queries or an integrated search engine. |
| **Review Approval Workflow** | Build a moderation queue so admin approves reviews before they appear publicly. |
| **Low Stock Inventory Alerts** | Notify the admin via email when any product's stock falls below a configurable minimum threshold. |
| **Analytics Dashboard** | Add charts to the admin panel showing revenue trends, best-selling products, and order summaries using Chart.js. |
| **Wishlist Feature** | Allow logged-in users to save products to a personal wishlist for later purchase. |
| **Nginx Reverse Proxy** | Add Nginx to the Docker Compose stack to efficiently serve static files and enable HTTPS via Let's Encrypt SSL certificates. |

---

## 12. Conclusion

The **Yuki** web application is a complete, production-ready e-commerce platform built entirely from first principles using Python and Flask. The project successfully demonstrates:

- **Full-Stack Web Development** using the MVC design pattern with Flask Blueprints.
- **Relational Database Design** with 10 interconnected models and proper foreign-key relationships using SQLAlchemy ORM.
- **Multi-Layer Security** including password hashing, OTP-based two-factor authentication, Google OAuth, and secure session management.
- **Business Logic Implementation** through custom features like advance payment collection, bulk discounts, coupon codes, and customization file uploads — all tailored to the real-world needs of the client business.
- **DevOps and Containerization** by packaging the application with Docker and Gunicorn for a consistent and deployable production environment.

The platform successfully digitizes the complete workflow of a custom printing business — from customer browsing and ordering to admin management and payment verification — into a single, cohesive web application.

---

*Report prepared for academic submission — March 2026*
