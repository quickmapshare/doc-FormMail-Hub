---
title: FormMail Hub - Complete User & Administration Guide
description: Master Google Forms email automation, custom SMTP integration, conditional routing, and email campaigns with FormMail Hub.
---

Welcome to the official **FormMail Hub** documentation. FormMail Hub transforms standard Google Forms™ into an enterprise-grade email automation, lead engagement, and customer communications platform.

Whether you need instant notifications for internal team members, dynamic auto-responders for respondents, or high-volume outreach via enterprise custom SMTP servers, FormMail Hub provides a seamless workflow directly integrated with your Google Workspace ecosystem.

---

## Quick Start & Installation

### 1. Installing FormMail Hub
1. Visit the **Google Workspace Marketplace** and search for **FormMail Hub** (or click the Marketplace badge on [doc.formmailhub.com](https://doc.formmailhub.com/)).
2. Click **Install** or **Domain Install** (if managing organization-wide deployment).
3. Grant the required permissions to allow FormMail Hub to access Google Forms responses and trigger email dispatches.

### 2. Opening the Add-On in Google Forms
1. Open any existing form or create a new form in [Google Forms™](https://forms.google.com).
2. Click the **Add-ons** puzzle icon in the top toolbar.
3. Select **FormMail Hub** and click **Configure** to open the main sidebar interface.

---

## Custom SMTP Setup & Quota Optimization

Standard Google Workspace accounts are subject to daily email sending limits (typically 100 to 1,500 emails/day depending on account type). FormMail Hub eliminates these restrictions by enabling custom **SMTP (Simple Mail Transfer Protocol)** connections.

### High-Volume Email Delivery Options

FormMail Hub supports standard SMTP connections for various email services:

| Provider | Daily Limit | Best Use Case |
| :--- | :--- | :--- |
| **Google Workspace / Free Gmail™** | Up to 500 / day | Standard transactional confirmations and small business forms |
| **Amazon SES** | 10,000+ / day | High-volume lead capture, enterprise event registration, and marketing |
| **SendGrid / Mailgun** | Custom / Tiered | Transactional emails requiring detailed bounce tracking and analytics |
| **Custom Corporate SMTP** | Server-Defined | Organizations requiring strict internal relay servers (`smtp.yourdomain.com`) |

### Configuring Custom SMTP Credentials

1. Launch the FormMail Hub sidebar in Google Forms.
2. Navigate to **Settings** > **SMTP Configuration**.
3. Choose your SMTP provider or select **Custom SMTP**.
4. Input your connection parameters:
   - **SMTP Host:** (e.g., `email-smtp.us-east-1.amazonaws.com` or `smtp.gmail.com`)
   - **Port:** `587` (TLS) or `465` (SSL)
   - **Authentication:** Username / API Key and Password
   - **Sender Name & Email:** (e.g., `Support Team <support@yourdomain.com>`)
5. Click **Test Connection** to verify delivery credentials, then save your configuration.

### Dual-Routing Architecture

FormMail Hub features an intelligent dual-routing mechanism designed to preserve your personal email quota:

- **Internal Admin & Team Alerts:** Routed via FormMail Hub's dedicated internal notification system. This consumes **0%** of your personal SMTP daily quota.
- **External Respondent Emails:** Dispatched via your configured Custom SMTP server, ensuring 100% of your dedicated sending capacity is reserved for customer outreach.

---

## Setting Up Auto-Responders & Notifications

### Automated Confirmation Responders
Send instant, tailored confirmation emails to users as soon as they submit a Google Form.

1. Go to **Email Rules** > **Create New Rule**.
2. Select **Trigger: On Form Submit**.
3. Set the **Recipient Field** to match your form's Email question (e.g., `{Email Address}`).
4. Customize the Email Subject and Body using dynamic tags.

### Dynamic Content Tags (`{tags}`)
Incorporate respondent answers directly into email templates using tags corresponding to form questions:

- `{Full Name}` - Replaced by the submitter's answer to "Full Name".
- `{Form Summary}` - Generates an formatted summary table of all submitted questions and answers.
- `{Submission Date}` - Inserts the exact timestamp of form submission.
- `{Unsubscribe link}` - Adds a standard opt-out mechanism for email compliance.

### Conditional Email Routing
Route notifications or specific auto-responders based on user responses:

- **Example Rule:** If *"Department Requested"* equals *"Technical Support"*, send email to `support@yourdomain.com`.
- **Example Rule:** If *"Ticket Type"* equals *"VIP"*, trigger an instant priority response template via custom SMTP.

---

## Email Marketing & Broadcast Campaigns

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

## Best Practices & Email Deliverability

To ensure your automated emails consistently land in the primary inbox rather than spam folders:

1. **Verify Sender Domain (SPF & DKIM):** When using Amazon SES, SendGrid, or custom domains, ensure SPF, DKIM, and DMARC DNS records are fully configured.
2. **Use Clear Sender Names:** Clearly identify your company or team in the "From" name field.
3. **Include Opt-Out Links:** Always place an `{Unsubscribe link}` in bulk broadcast emails to remain compliant with CAN-SPAM and GDPR regulations.
4. **Monitor Quota Usage:** Keep track of your daily limit directly inside the FormMail Hub dashboard settings.

---

*Google Forms™ and Gmail™ are trademarks of Google LLC.*