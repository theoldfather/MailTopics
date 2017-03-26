import imaplib as imap
import os


def get_creds(user):
    with open(os.environ['HOME']+"/.email", "r") as f:
        for line in f.readlines():
            u, p = line.strip().split("\t")
            if u == user:
                return {'user': user, 'password': p}
        return None


def get_gmail_con(email_address):
    con = imap.IMAP4_SSL(host="imap.gmail.com", port=993)
    con.login(**get_creds(email_address))
    return con


def save_mailbox_subjects(imap_con, filename, search='ALL', mailbox="inbox"):
    # select the default mailbox (inbox)
    imap_con.select(mailbox=mailbox)

    typ, mb = imap_con.search(None, search)
    msg_ids = mb[0].split()
    subjects = ['']*len(msg_ids)

    stored_msg_ids = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            stored_msg_ids = set([int(l.split("\t")[0].strip()) for l in f.readlines()])
        print("Found %d stored messages" % len(stored_msg_ids))

    with open(filename, "a") as f:
        i = 0
        for num in msg_ids:
            num = num.strip()
            if int(num) not in stored_msg_ids:
                typ, msg_data = imap_con.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
                if (i+1) % 100 == 0:
                    print("%02.2f percent complete" % (100.*float(num)/len(msg_ids)))
                subject = msg_data[0][1].replace(b'Subject:', b'').replace(b"\n", b" ").replace(b"\r", b"").strip()
                subjects[i] = subject
                f.write("%d\t%s\n" % (int(num), subject.decode('utf-8')))
                i += 1

