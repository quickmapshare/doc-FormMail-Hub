---
title: FormMail Hub - Complete User & Administration Guide
description: Master Google Forms email automation, custom SMTP integration, conditional routing, domain navigation, and email campaigns with FormMail Hub.
---

Welcome to the official **FormMail Hub** documentation. FormMail Hub transforms standard Google Forms™ into an enterprise-grade email automation, lead engagement, and customer communications platform.

Access the central documentation hub and official portal anytime at [https://doc.formmailhub.com/](https://doc.formmailhub.com/).

---

## 1. Core Architecture & Navigation

FormMail Hub is engineered to operate seamlessly inside the Google Workspace ecosystem while offloading heavy email dispatch operations to optimized delivery networks or your own custom SMTP servers.

### Official Portal Navigation
The global navigation across the application connects directly to the official documentation hub at `https://doc.formmailhub.com/`. Users and administrators can use this portal to access:
- Comprehensive setup tutorials and integration walkthroughs.
- Technical specifications for major SMTP email providers.
- Live status updates, policy changes, and compliance frameworks.

### Dual-Routing System Architecture
```
+-----------------------------------------------------------------------+
|                         Google Forms Submissions                      |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                           FormMail Hub Engine                         |
+-----------------------------------------------------------------------+
                /                                       \
               v                                         v
+-------------------------------+       +--------------------------------+
| Internal Admin & Team Alerts  |       | Respondent Auto-Responders     |
| (Dedicated System Relay)      |       | (Custom SMTP: SES, Gmail, etc) |
| * Consumes 0% Personal Quota  |       | * Scalable up to 10,000+/day   |
+-------------------------------+       +--------------------------------+
```

---

## 2. Quick Start & Installation

### Single User Installation
1. Visit the **Google Workspace Marketplace** and search for **FormMail Hub** (or click the Marketplace badge on [doc.formmailhub.com](https://doc.formmailhub.com/)).
2. Click **Install** or approve individual user permissions.
3. Open any existing form or create a new form in [Google Forms™](https://forms.google.com).
4. Click the **Add-ons** puzzle icon in the top toolbar, select **FormMail Hub**, and click **Configure**.

### Domain-Wide Admin Deployment
1. Log into the **Google Workspace Admin Console** (`admin.google.com`).
2. Navigate to **Apps** > **Google Workspace Marketplace apps** > **Apps list**.
3. Click **Domain Install** to grant permissions organization-wide across all user accounts.

---

## 3. Custom SMTP Setup & Quota Optimization

Standard Google Workspace accounts enforce daily email sending limits (typically 100 to 1,500 emails/day depending on account type). FormMail Hub eliminates these restrictions by enabling custom **SMTP (Simple Mail Transfer Protocol)** connections.

### Supported Email Delivery Options

| Provider | Daily Limit | Best Use Case | Protocol |
| :--- | :--- | :--- | :--- |
| **Google Workspace / Free Gmail™** | Up to 500 / day | Standard transactional confirmations and small business forms | TLS (587) / SSL (465) |
| **Amazon SES** | 10,000+ / day | High-volume lead capture, enterprise event registration, and marketing | TLS (587) / API |
| **SendGrid / Mailgun** | Custom / Tiered | Transactional emails requiring detailed bounce tracking and analytics | TLS (587) / API |
| **Custom Corporate SMTP** | Server-Defined | Organizations requiring strict internal relay servers (`smtp.yourdomain.com`) | STARTTLS / SSL |

### Configuring Custom SMTP Credentials

1. Launch the FormMail Hub sidebar in Google Forms.
2. Navigate to **Settings** > **SMTP Configuration**.
3. Choose your SMTP provider or select **Custom SMTP**.
4. Input your connection parameters:
   - **SMTP Host:** (e.g., `email-smtp.us-east-1.amazonaws.com` or `smtp.gmail.com`)
   - **Port:** `587` (TLS) or `465` (SSL)
   - **Authentication:** Username / API Key and Password / Secret Key
   - **Sender Identity:** (e.g., `Support Team <support@yourdomain.com>`)
5. Click **Test Connection** to verify delivery credentials, then save your configuration.

### Intelligent Dual-Routing Architecture

FormMail Hub features a dual-routing mechanism designed to preserve your personal email quota:

- **Internal Admin & Team Alerts:** Routed via FormMail Hub's dedicated internal notification system. This consumes **0%** of your personal SMTP daily quota.
- **External Respondent Emails:** Dispatched via your configured Custom SMTP server, ensuring 100% of your dedicated sending capacity is reserved for customer outreach.

---

## 4. Setting Up Auto-Responders & Smart Routing

### Automated Confirmation Responders
Send instant, tailored confirmation emails to users as soon as they submit a Google Form.

1. Go to **Email Rules** > **Create New Rule**.
2. Select **Trigger: On Form Submit**.
3. Set the **Recipient Field** to match your form's Email question (e.g., `{Email Address}`).
4. Customize the Email Subject and Body using dynamic tags.

### Dynamic Content Tag Matrix (`{tags}`)
Incorporate respondent answers directly into email templates using tags corresponding to form questions:

| Dynamic Tag | Description | Example Output |
| :--- | :--- | :--- |
| `{Full Name}` | Replaced by the submitter's answer to "Full Name". | Jane Doe |
| `{Form Summary}` | Generates a formatted summary table of all submitted questions and answers. | Full question/answer table |
| `{Submission Date}` | Inserts the exact timestamp of form submission. | 2026-03-31 14:30 UTC |
| `{Unsubscribe link}` | Adds a standard opt-out mechanism for email compliance. | Opt-out URL |

### Conditional Email Routing
Route notifications or specific auto-responders based on user responses:

- **Department Rule:** If *"Department Requested"* equals *"Technical Support"*, send email to `support@yourdomain.com`.
- **VIP Responder Rule:** If *"Ticket Type"* equals *"VIP"*, trigger an instant priority response template via custom SMTP.

---

## 5. Email Marketing & Broadcast Campaigns

Beyond automated triggers, FormMail Hub enables direct email marketing campaigns targeting form respondents.

### 1. Managing Collected Leads
FormMail Hub automatically indexes contact information submitted through your forms, organizing them into ready-to-use subscriber lists.

### 2. Creating Broadcast Campaigns
1. In the FormMail Hub dashboard, select **Campaigns** > **New Broadcast**.
2. Choose the target Google Form list or filtered response segment.
3. Draft your email message using rich text or HTML formatting.
4. Insert mandatory compliance elements, such as dynamic `{Unsubscribe link}` tags.
5. Click **Schedule** or **Send Now**.

---

## 6. Security, Deliverability & Compliance

To ensure your automated emails consistently land in the primary inbox rather than spam folders:

1. **Verify Sender Domain (SPF & DKIM):** When using Amazon SES, SendGrid, or custom domains, ensure SPF, DKIM, and DMARC DNS records are fully configured.
2. **Use Clear Sender Names:** Clearly identify your company or team in the "From" name field.
3. **Include Opt-Out Links:** Always place an `{Unsubscribe link}` in bulk broadcast emails to remain compliant with CAN-SPAM and GDPR regulations.
4. **Monitor Quota Usage:** Keep track of your daily limit directly inside the FormMail Hub dashboard settings.

---

*Google Forms™ and Gmail™ are trademarks of Google LLC.*