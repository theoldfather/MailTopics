# MailTopics
Tools for extracting topics from imap mailboxes


### Example Usage

```python
import mail_reader as mr
import topics_generator as tg


# put the credentials for your gmail account in  .email in your home directory
# for example, ~/.email is tab delimited with the format
# you@example.com   your_password

# selects credentials from the file and creates an imap connection
con = mr.get_gmail_con("you@example.com")

# show available mailboxes
con.list()

# save subject lines to txt
mr.save_mailbox_subjects(con, "inbox_subjects.txt")
mr.save_mailbox_subjects(con, "all_mail_subjects.txt", mailbox='"[Gmail]/All Mail"')
mr.save_mailbox_subjects(con, "sent_subjects.txt", mailbox='"[Gmail]/Sent Mail"')


# choose parameters for LDA
# see: http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html
opts = {
        'n_topics': 5,
        'learning_method': 'batch',
        'n_jobs': -1
    }

# run LDA on the subject lines collected from each mailbox
tg.run_lda("inbox_subjects.txt", opts, show_n_terms=10)
tg.run_lda("sent_subjects.txt", opts, show_n_terms=10)
tg.run_lda("all_mail_subjects.txt", opts, show_n_terms=10)
```
