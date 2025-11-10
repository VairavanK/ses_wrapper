## Amazon SES Email Function - Complete Documentation

### Function: `send_ses_email()`

Enterprise-grade email sending via Amazon SES with full HTML support, attachments, and secure credential handling.

---

### Quick Start

**Basic text email:**
```python
result = send_ses_email(
    from_email='noreply@example.com',
    to_emails='user@example.com',
    subject='Hello World',
    body_text='This is a simple text email'
)
```

**HTML email with styling:**
```python
result = send_ses_email(
    from_email='reports@example.com',
    to_emails='user@example.com',
    subject='Monthly Report',
    body_text='Please view this email in an HTML client.',
    body_html='<h1>Report</h1><p>Your monthly metrics are attached.</p>'
)
```

**Multiple recipients with CC and attachments:**
```python
result = send_ses_email(
    from_email='system@example.com',
    to_emails=['user1@example.com', 'user2@example.com'],
    cc_emails='manager@example.com',
    subject='Q4 Report',
    body_text='See attached quarterly report.',
    body_html='<h2>Q4 Report</h2><p>Please review the attached PDF.</p>',
    attachments=['q4_report.pdf', 'data.csv']
)
```

---

### Parameters Reference

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_email` | str | ✓ | Verified sender email address in SES |
| `to_emails` | str/list | ✓ | Recipient email(s) |
| `subject` | str | ✓ | Email subject line |
| `body_text` | str | ✓ | Plain text body (fallback) |
| `body_html` | str | ✗ | HTML email body |
| `cc_emails` | str/list | ✗ | CC recipient(s) |
| `bcc_emails` | str/list | ✗ | BCC recipient(s) |
| `attachments` | list | ✗ | File paths to attach |
| `smtp_username` | str | ✗ | SES SMTP username (or env var) |
| `smtp_password` | str | ✗ | SES SMTP password (or env var) |
| `smtp_host` | str | ✗ | SMTP server (auto-generated from region) |
| `smtp_port` | int | ✗ | SMTP port (default: 587) |
| `region` | str | ✗ | AWS region (default: ap-southeast-1) |

---

### Return Value

Returns a dictionary with status and details:

**Success:**
```python
{
    'success': True,
    'message': 'Email sent successfully to 3 recipient(s)',
    'recipients': ['user1@example.com', 'user2@example.com', 'cc@example.com']
}
```

**Failure:**
```python
{
    'success': False,
    'message': 'SMTP authentication failed',
    'error': 'Invalid credentials or permissions: (535, ...)'
}
```

---

### Credential Management

**Option 1: Environment variables (recommended)**
```python
# Set credentials in environment
os.environ['SES_SMTP_USERNAME'] = 'AKIAIOSFODNN7EXAMPLE'
os.environ['SES_SMTP_PASSWORD'] = 'wJalrXUtnFEMI/K7MDENG/...'

# Function will auto-detect
result = send_ses_email(from_email='...', to_emails='...', ...)
```

**Option 2: Direct parameters**
```python
result = send_ses_email(
    from_email='...',
    to_emails='...',
    subject='...',
    body_text='...',
    smtp_username='AKIAIOSFODNN7EXAMPLE',
    smtp_password='wJalrXUtnFEMI/K7MDENG/...'
)
```

**Option 3: Use Hex secrets (in notebook)**
```python
# In Hex, reference secrets directly
result = send_ses_email(
    from_email='...',
    to_emails='...',
    subject='...',
    body_text='...',
    smtp_username=SES_SMTP_USERNAME,  # Hex secret
    smtp_password=SES_SMTP_PASSWORD   # Hex secret
)
```

---

### Common Patterns

**1. Send report with PDF attachment**
```python
result = send_ses_email(
    from_email='reports@company.com',
    to_emails='stakeholder@company.com',
    subject=f'Monthly Report - {datetime.now().strftime("%B %Y")}',
    body_text='Please find attached the monthly performance report.',
    body_html=f'''
        <h2>Monthly Report - {datetime.now().strftime("%B %Y")}</h2>
        <p>Dear Stakeholder,</p>
        <p>Please find attached this month's performance report.</p>
        <p>Key highlights:</p>
        <ul>
            <li>Revenue: $XXX</li>
            <li>Growth: XX%</li>
        </ul>
    ''',
    attachments=['monthly_report.pdf']
)
```

**2. Bulk notification to multiple users**
```python
recipients = df['email'].tolist()  # From a dataframe

result = send_ses_email(
    from_email='notifications@company.com',
    to_emails=recipients,
    subject='System Maintenance Notice',
    body_text='System maintenance scheduled for this weekend.',
    body_html='<h3>Maintenance Notice</h3><p>Our systems will undergo maintenance...</p>'
)
```

**3. Error handling pattern**
```python
result = send_ses_email(...)

if result['success']:
    print(f"✓ Sent to {len(result['recipients'])} recipients")
    # Log success to database
else:
    print(f"✗ Failed: {result['error']}")
    # Log failure, retry, or alert
```

---

### AWS SES Setup Requirements

**1. Verify sender email/domain in SES console**
- Single email verification: SES Console → Email Addresses → Verify
- Domain verification: SES Console → Domains → Verify (requires DNS records)

**2. Generate SMTP credentials**
- SES Console → SMTP Settings → Create SMTP Credentials
- Save the username (starts with `AKIA...`) and password

**3. Move out of sandbox (for production)**
- By default, SES is in sandbox mode (can only send to verified emails)
- Request production access: SES Console → Account Dashboard → Request Production Access

**4. Configure sending limits**
- Sandbox: 200 emails/day, 1 email/second
- Production: Request higher limits if needed

---

### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Invalid credentials | Verify SMTP username/password in SES console |
| MessageRejected | Unverified sender | Verify sender email in SES |
| MessageRejected | Sandbox mode | Verify recipient email or request production access |
| Connection timeout | Network/firewall | Check port 587 is open, verify SMTP host |
| Attachment error | File not found | Check file path exists before sending |

---

### Best Practices

1. **Always provide both text and HTML bodies** for maximum compatibility
2. **Use environment variables** for credentials (never hardcode)
3. **Verify return status** and implement error handling
4. **Rate limit bulk sends** to respect SES quotas
5. **Use meaningful subject lines** to avoid spam filters
6. **Test with verified emails** before production deployment
7. **Monitor bounce/complaint rates** in SES console

---

### Performance & Limits

- **Speed**: ~1 email/second (sandbox), configurable in production
- **Size limit**: 10 MB per email (including attachments)
- **Recipient limit**: 50 recipients per email (to + cc + bcc combined)
- **Daily quota**: 200 emails/day (sandbox), scalable in production

---

### Integration Examples

**With Hex scheduled runs:**
```python
# In a scheduled notebook cell
report_html = generate_report()  # Your report generation logic

result = send_ses_email(
    from_email='automation@company.com',
    to_emails=stakeholder_emails,
    subject=f'Automated Daily Report - {date.today()}',
    body_text='Daily report attached.',
    body_html=report_html,
    attachments=['daily_metrics.pdf']
)

# Log results for monitoring
if not result['success']:
    # Alert ops team
    print(f"ALERT: Email failed - {result['error']}")
```

**With dynamic HTML from dataframe:**
```python
# Build HTML table from dataframe
html_table = df.to_html(index=False, border=0, classes='data-table')

# Create styled email with embedded table
html_email = f'<h2>Weekly Metrics</h2>{html_table}'

result = send_ses_email(
    from_email='metrics@company.com',
    to_emails='team@company.com',
    subject='Weekly Metrics Summary',
    body_text='Please view in HTML email client.',
    body_html=html_email
)
```