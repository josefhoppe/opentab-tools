# opentab-tools

- `python format_feedback.py` outputs feedback to individual html files per judge (needs running opentab on localhost:5000)
    - uses `templates/feedback.html`
- `DataProcessing.ipynb` supports the validation and cleaning of input data
- Send Emails by:
    1. `python export_tablinks.py` (needs running opentab on localhost:5000)
    2. (optional) check *tablinks.csv*
    3. open `send_emails.py` and change the relevant variables for SMTP
    4. `python send_emails.py` to send the emails
        - uses `templates/tablink_email`
- `python get_top_team_categories.py` - custom report for Göttingen (Ehrung der top-Teamkategoriepunkte)

Other files contain library functions for the aforementioned features.