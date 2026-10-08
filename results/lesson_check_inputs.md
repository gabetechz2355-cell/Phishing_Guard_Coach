# Lesson hand-check inputs, reject cases, no judge

Lessons from 20261007-222717-final-pass1.json (run started 2026-10-07T22:27:17), one per reject case whose reply carries a Coach lesson, with the email body, the answer key's red flags, and the employee's stated reason beside each. Label each box by hand before looking at any judge output. Criteria per PLAN.md: the lesson names the labeled red flags, gives a usable rule, invents nothing, and stays at 120 words or fewer. Word counts are computed here, not judged.

## C-02 (E-002)

**Subject:** Updated bank details for October invoices
**Sender:** Apex Supply Billing <billing@apex-supp1y.example>
**Employee role:** Accounts Payable

**Body:**

```
Hi Dana,

Please note that Apex Supply has moved to a new bank. Starting with the October invoices, remit payment to:

Bank: Harborline Trust
Account: 4471190233
Routing: 081000210

Our previous account will be closed at month end, so please update your records before the next payment run and confirm by reply when done.

Thanks,
Marla Jensen
Billing Coordinator, Apex Supply
```

**Labeled red flags:** lookalike sender domain; reply-to differs from sender; bank detail change request

**Employee's reason for rejecting:** That's Apex, we pay them every month.

**Lesson (84 words):**

1) Red flags: the lookalike sender domain “billing@apex-supp1y.example” imitates “apexsupply.example”; it asks for a “new bank” for payment; and it wants you to “reply confirmation.” The payment/bank/account language is a classic trigger.

2) “We pay them every month” is a common trap: familiar vendors can still be spoofed, and routine invoices can make urgent change requests feel normal.

3) For Accounts Payable: any bank-detail change needs a second check against records before payment. Use the vendor contact already on file to verify the request.

**Hand labels (yes/no):** names the labeled red flags: NO   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES
**Note:** missing "reply-to differs from sender".

## C-05 (E-005)

**Subject:** Quick favor - client appreciation
**Sender:** Elena Marsh <elena.marsh.ceo@quickmail.example>
**Employee role:** Regional Sales

**Body:**

```
Priya,

I'm stuck in back-to-back meetings with the board today. I need five $200 gift cards (any major retailer) for client appreciation gifts by this afternoon. Please buy them, scratch off the codes, and email me the codes and the receipts. I'll have finance reimburse you tomorrow.

Keep this between us until the gifts are out.

Thanks,
Elena
```

**Labeled red flags:** executive request from personal webmail; gift card purchase with codes by email; secrecy and urgency

**Employee's reason for rejecting:** Elena emails from her personal account when she travels.

**Lesson (99 words):**

1) Red flags: the email asks for “five $200 gift cards,” says to “keep it secret,” and wants the “codes/receipts” emailed back; the sender is also from an “external domain” not in Priya’s normal vendor list.

2) Elena using a personal account while traveling is a common trap because it can sound routine and specific. But urgent gift-card requests plus secrecy are classic phishing signals, even when the name looks familiar.

3) Rule for Regional Sales: never buy gift cards or send codes/receipts from an unexpected email—verify any unusual request through a known company contact or your manager first.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: NO   120 words or fewer: YES
**Note:** "not in Priya's normal vendor list" is not in the email, flags, or reason.

## C-06 (E-006)

**Subject:** Delivery attempt failed - action needed
**Sender:** Parcel Track Notifications <notices@parcel-track-updates.example>
**Employee role:** Regional Sales

**Body:**

```
We were unable to deliver your package (tracking 7731-920-114) because the address on file is incomplete.

To schedule redelivery, confirm your address and pay the $2.99 redelivery fee within 48 hours:

https://parcel-track-updates.example/redeliver/88213

Packages not claimed within 48 hours are returned to sender.
```

**Labeled red flags:** blocklisted link; malicious sender domain; payment demand with 48-hour deadline

**Employee's reason for rejecting:** I'm expecting samples from a supplier this week.

**Lesson (90 words):**

1) Red flags: the sender is from a “malicious sender domain,” the message uses a “blocklisted link,” and it pushes an “urgent fee request” tied to a delivery-themed lure (“package delivery failed”).  

2) Expecting samples is a common trap because real shipments make this kind of message feel routine, so urgency and timing can lower caution without anyone doing anything wrong.  

3) Next time, as Regional Sales, verify any delivery issue through the supplier or carrier using a number or site already on file, not the link in the email.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-09 (E-009)

**Subject:** Following up from the Midwest Food Expo - vendor setup
**Sender:** Green Valley Produce <sales@greenvalley-produce.example>
**Employee role:** Accounts Payable

**Body:**

```
Hi Dana,

It was good to meet your team at the Midwest Food Expo last month. As discussed, our 2027 catalog is here:

https://greenvalley-produce.example/catalog

To set Harbor Foods up as a customer, please fill in the attached new-account form with your AP contact and billing address and send it back, and we'll have pricing to you within a week.

Regards,
Sam Okafor
Green Valley Produce
```

**Labeled red flags:** unknown sender domain; request for billing details from a first-contact vendor

**Employee's reason for rejecting:** We met them at the expo last month and I asked for the catalog.

**Lesson (99 words):**

1) Red flags: the sender uses an “Unknown sender domain” (`sales@greenvalley-produce.example`), asks for “AP contact and billing address,” and pushes a “new-account form” with a “link reputation unknown.”  

2) Meeting someone at the expo and asking for the catalog is a normal, helpful context, but it can create trust too quickly. That’s a common trap: familiar-looking follow-up messages can still be unconfirmed.  

3) Rule for AP: before sharing any billing or account setup details, verify the sender using a known, trusted contact method. This email is suspicious and unconfirmed; call Green Valley Produce using a number already on file.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES
**Note:** "link reputation unknown" comes from Guard's tool evidence, which the judge does not see.

## C-12 (E-012)

**Subject:** (blank)
**Sender:** Brendin Mandy <brendin.mandy@pharma-fastship.example>
**Employee role:** HR Coordinator

**Body:**

```
brendin mandy furballkinetxcom searching reliable chemists wont find better solution site everything cure bad stateeven need fast delivery always rely us obtain trustworthy help fast mouse click traditionstreetcom 5 aug 2008 214200 discover new wed 06 aug 2008 020831 0000 bigger tool
```

**Labeled red flags:** malicious sender domain; newly registered sender domain; unsolicited pharmacy offer

**Employee's reason for rejecting:** I thought it was one of the pharmacy discount offers we get through our benefits provider.

**Lesson (92 words):**

1) Red flags: the sender uses a malicious sender domain: “brendin.mandy@pharma-fastship.example,” and it’s a very new domain. The body also uses phishing-style solicitation language: “reliable chemists,” “fast delivery,” plus a suspicious “2008 date string.”

2) Your reasoning is a common trap because legitimate benefits offers can look promotional, so it’s easy to assume a familiar category before checking the source.

3) As an HR Coordinator, treat unsolicited vendor-style emails as unconfirmed. Next time, verify by contacting the benefits provider using a number already on file, not any contact info in the email.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-14 (E-014)

**Subject:** Action required: re-enroll your MFA device by end of day
**Sender:** Harbor Foods IT Service Desk <servicedesk@harb0rfoods.example>
**Employee role:** HR Coordinator

**Body:**

```
Hi Marcus,

As part of this month's security upgrade, every Harbor Foods account must re-enroll its multi-factor authentication device. Accounts not re-enrolled by 5pm today will be locked out of email, Teams, and the HR portal.

Re-enroll here with your current password and the code from your authenticator app:

https://harb0rfoods.example/mfa/re-enroll?u=marcus.lee

It takes less than two minutes.

Harbor Foods IT Service Desk
```

**Labeled red flags:** lookalike of company domain; link to lookalike domain; asks for password and MFA code; same-day lockout threat

**Employee's reason for rejecting:** IT said everyone has to set up MFA again this month.

**Lesson (103 words):**

1) Red flags: the sender domain is a lookalike of “harborfoods.example,” the link is suspicious and looks like “harborfoods.example,” and it asks for “current password and authenticator code” with an urgent “end of day” lockout deadline.  

2) Your reason is a common trap: phish often use a real-sounding IT change and a broad “everyone must do this” message to feel routine and time-sensitive.  

3) Rule for next time: as an HR Coordinator, never enter passwords or MFA codes from an email request; when IT asks for account changes, verify by contacting the IT Service Desk using a number or portal already on file.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-24 (E-024)

**Subject:** Sponsorship invoice for the Gulf Coast Grocers summit
**Sender:** Rob Kessler <rob.kessler@harborfoods.example>
**Employee role:** Accounts Payable

**Body:**

```
Hi Dana,

We agreed to sponsor the Gulf Coast Grocers summit in November. Their invoice is attached: $9,800, payable to Gulf Coast Events LLC by ACH, bank details on the invoice. They aren't set up as a vendor yet, so could you add them directly and include this in Thursday's payment run? They need it before the event.

Thanks,
Rob

Rob Kessler
Chief Financial Officer, Harbor Foods
```

**Labeled red flags:** payment to a payee not in vendor records; request to skip vendor setup; deadline tied to the payment run

**Employee's reason for rejecting:** Rob is our CFO and he sends me sponsorship invoices to add to the run all the time.

**Lesson (97 words):**

1) Red flags: “include a $9,800 ACH payment,” “add a new vendor,” and “rush it into Thursday’s payment run.” A payment request with bank details plus urgency is a classic risk pattern.  

2) Dana’s trust is understandable because familiar internal senders can make requests feel routine. That’s a common trap: attackers or spoofed messages often mimic normal CFO workflows and timing.  

3) Rule for Accounts Payable: any new vendor + ACH + rush request must be verified out of band before processing. This email is unconfirmed; call Rob using a number already on file to verify it.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-26 (E-026)

**Subject:** Shortlist: 5 warehouse candidates available to start Monday
**Sender:** TalentBridge Staffing <recruiting@talentbridge-staffing.example>
**Employee role:** HR Coordinator

**Body:**

```
Hi Marcus,

We saw Harbor Foods is hiring warehouse associates in Tampa. We have five pre-screened candidates with forklift certification who can start Monday. Their resumes are in this folder:

https://talentbridge-staffing.example/candidates/warehouse-shortlist

Our standard placement fee applies only if you hire.

Best,
Derek Shaw
TalentBridge Staffing
```

**Labeled red flags:** unknown sender domain; unknown link; unsolicited first contact with files to open

**Employee's reason for rejecting:** We're hiring for the warehouse and I've been posting on job boards.

**Lesson (90 words):**

1) Red flags: the sender domain is “unknown,” the recruiting link has “unknown reputation,” and it came from “a staffing vendor requiring verification.”  
2) Your reason—“We’re hiring for the warehouse and I’ve been posting on job boards”—is a common trap because real hiring activity makes outside recruiting emails feel expected, even when the source still needs checking.  
3) Rule for next time as an HR Coordinator: before opening candidate folders or acting on a staffing message, verify the vendor through a trusted contact already on file. The email is unconfirmed.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-28 (E-028)

**Subject:** Annual administrator re-verification due Oct 15
**Sender:** PayWell Client Security <security@paywell.example>
**Employee role:** HR Coordinator

**Body:**

```
Hi Marcus,

Each year before W-2 season, PayWell asks every client administrator to re-verify their access. Please sign in and confirm your administrator role by October 15, or your admin access will be paused until you contact us:

https://verify.paywell.example/admin-attestation

If you have questions, call your service team at the number in your PayWell contract.

PayWell Client Security
```

**Labeled red flags:** unknown link on a vendor subdomain; sign-in request with an access-pause deadline

**Employee's reason for rejecting:** PayWell makes us re-verify admin access every year before W-2 season.

**Lesson (94 words):**

1) Red flags: it asks you to “sign in and confirm administrator role,” uses an “external verification link,” and warns “admin access will be paused” if you don’t act.  
2) Your reason is a common trap: when a process sounds familiar—like annual re-verification before W-2 season—it’s easy to trust the message without checking whether this one is real.  
3) Rule for next time: as an HR Coordinator, never use a link in a security email to verify access; treat it as unconfirmed and verify through your normal HR/payroll contact or a known internal portal.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES

## C-29 (E-029)

**Subject:** New expense tool: create your Tallyline account by Friday
**Sender:** Harbor Foods Finance <finance@harborfoods.example>
**Employee role:** Accounts Payable

**Body:**

```
Hi Dana,

As announced at last week's all-hands, Harbor Foods is moving expense reports to Tallyline on November 1. Please create your account by Friday with your work email:

https://harborfoods.tallyline.example/signup

Expense reports submitted the old way after October 31 won't be reimbursed. Questions go to finance@harborfoods.example.

Harbor Foods Finance
```

**Labeled red flags:** unknown third-party sign-up link; account creation with a deadline

**Employee's reason for rejecting:** Finance announced the new expense tool at the all-hands.

**Lesson (104 words):**

1) Red flags: “create a Tallyline account by Friday,” an “external signup link with unknown reputation,” and an “expense tool migration request needs extra verification.”  

2) Seeing a Finance-announced tool from all-hands feels familiar, which is a common trust cue. The trap is that attackers often borrow real announcements and add urgency, so a legitimate topic can still be unconfirmed.  

3) Rule for Accounts Payable: for any new account-creation or expense-tool change, pause before clicking and verify it through a known internal channel. This email is unconfirmed; call Finance using a number already on file or check the request in your approved company portal.

**Hand labels (yes/no):** names the labeled red flags: YES   gives a usable rule: YES   invents nothing: YES   120 words or fewer: YES
