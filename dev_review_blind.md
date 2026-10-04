# Dev set review (blind)

Ten development emails, E-001 to E-010, exactly as stored in `data/emails.json`, plus the mock threat-intel rows for each sender domain, reply-to domain, and link (`data/threat_intel.json`). A domain or link with no row shows the tool's default: unknown. No labels, verdicts, red flags, or tool expectations appear here; see `dev_review_key.md`.

## E-001

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Microsoft 365 Security <no-reply@m365-secure-login.example>
- **Reply-To:** no-reply@m365-secure-login.example
- **Subject:** Action required: your Harbor Foods password expires in 24 hours
- **Links:** https://m365-secure-login.example/reset?u=priya.shah

**Body**

```text
Your Microsoft 365 password for priya.shah@harborfoods.example will expire in 24 hours. To avoid losing access to email and Teams, verify your account and keep your current password now:

https://m365-secure-login.example/reset?u=priya.shah

If you do not act within 24 hours your account will be suspended and you will need to contact your administrator to restore access.

Microsoft 365 Security Team
```

**Threat intel**

- Sender domain `m365-secure-login.example`: reputation: malicious, age_days: 12, lookalike_of: None
- Link `https://m365-secure-login.example/reset?u=priya.shah`: reputation: malicious, lookalike_of: None, on_blocklist: True

## E-002

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Apex Supply Billing <billing@apex-supp1y.example>
- **Reply-To:** apex.billing@mailbox-pay.example
- **Subject:** Updated bank details for October invoices
- **Links:** none

**Body**

```text
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

**Threat intel**

- Sender domain `apex-supp1y.example`: reputation: suspicious, age_days: 6, lookalike_of: apexsupply.example
- Reply-to domain `mailbox-pay.example`: reputation: unknown, age_days: None, lookalike_of: None

## E-003

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Apex Supply Invoicing <invoices@apexsupply.example>
- **Reply-To:** invoices@apexsupply.example
- **Subject:** Invoice 20471 for September deliveries
- **Links:** https://portal.apexsupply.example/invoices/20471

**Body**

```text
Hi Dana,

Invoice 20471 for the September deliveries to the Tampa and Orlando warehouses is now available in the portal:

https://portal.apexsupply.example/invoices/20471

Total $18,420.00, net 30, payable to the same account as always. Let me know if any quantities don't match your receiving reports.

Thanks,
Marla Jensen
Apex Supply
```

**Threat intel**

- Sender domain `apexsupply.example`: reputation: clean, age_days: 4100, lookalike_of: None
- Link `https://portal.apexsupply.example/invoices/20471`: reputation: clean, lookalike_of: None, on_blocklist: False

## E-004

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** Tom Avery <tom.avery@harborfoods-hr.example>
- **Reply-To:** tom.avery@harborfoods-hr.example
- **Subject:** Direct deposit change before Friday payroll
- **Links:** none

**Body**

```text
Hi Marcus,

I switched banks this week. Can you update my direct deposit to the new account before Friday's payroll run?

Account: 920044817
Routing: 071000013
Bank: Harborline Trust

I'm on the road so I can't get to the HR portal. Really appreciate it.

Thanks,
Tom
Warehouse Operations
```

**Threat intel**

- Sender domain `harborfoods-hr.example`: reputation: suspicious, age_days: 3, lookalike_of: harborfoods.example

## E-005

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Elena Marsh <elena.marsh.ceo@quickmail.example>
- **Reply-To:** elena.marsh.ceo@quickmail.example
- **Subject:** Quick favor - client appreciation
- **Links:** none

**Body**

```text
Priya,

I'm stuck in back-to-back meetings with the board today. I need five $200 gift cards (any major retailer) for client appreciation gifts by this afternoon. Please buy them, scratch off the codes, and email me the codes and the receipts. I'll have finance reimburse you tomorrow.

Keep this between us until the gifts are out.

Thanks,
Elena
```

**Threat intel**

- Sender domain `quickmail.example`: reputation: clean, age_days: 6200, lookalike_of: None

## E-006

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Parcel Track Notifications <notices@parcel-track-updates.example>
- **Reply-To:** notices@parcel-track-updates.example
- **Subject:** Delivery attempt failed - action needed
- **Links:** https://parcel-track-updates.example/redeliver/88213

**Body**

```text
We were unable to deliver your package (tracking 7731-920-114) because the address on file is incomplete.

To schedule redelivery, confirm your address and pay the $2.99 redelivery fee within 48 hours:

https://parcel-track-updates.example/redeliver/88213

Packages not claimed within 48 hours are returned to sender.
```

**Threat intel**

- Sender domain `parcel-track-updates.example`: reputation: malicious, age_days: 9, lookalike_of: None
- Link `https://parcel-track-updates.example/redeliver/88213`: reputation: malicious, lookalike_of: None, on_blocklist: True

## E-007

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** BrightPath Benefits <accounts@brightpathbenefits.example>
- **Reply-To:** accounts@brightpathbenefits.example
- **Subject:** Open enrollment materials for Harbor Foods, November window
- **Links:** https://portal.brightpathbenefits.example/harborfoods/enrollment-2026

**Body**

```text
Hi Marcus,

The open enrollment packet for the November window is ready in your administrator portal:

https://portal.brightpathbenefits.example/harborfoods/enrollment-2026

It includes the updated plan comparison sheet and the employee FAQ. No changes to contribution rates this year. Our next check-in is Oct 14 at 10am as scheduled.

Best,
Karen Whitfield
Account Manager, BrightPath Benefits
```

**Threat intel**

- Sender domain `brightpathbenefits.example`: reputation: clean, age_days: 2900, lookalike_of: None
- Link `https://portal.brightpathbenefits.example/harborfoods/enrollment-2026`: reputation: clean, lookalike_of: None, on_blocklist: False

## E-008

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Luis Ortega <luis.ortega@harborfoods.example>
- **Reply-To:** luis.ortega@harborfoods.example
- **Subject:** Agenda: Q4 vendor review, Thursday 2pm
- **Links:** https://intranet.harborfoods.example/meetings/q4-vendor-review

**Body**

```text
Hi Dana,

Agenda for Thursday's Q4 vendor review is posted on the intranet:

https://intranet.harborfoods.example/meetings/q4-vendor-review

Topics: Apex Supply contract renewal, Coastal Freight fuel surcharge, and the new produce vendor shortlist. Bring the September spend summary if you have it. Room 4B.

Thanks,
Luis
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None
- Link `https://intranet.harborfoods.example/meetings/q4-vendor-review`: reputation: clean, lookalike_of: None, on_blocklist: False

## E-009

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Green Valley Produce <sales@greenvalley-produce.example>
- **Reply-To:** sales@greenvalley-produce.example
- **Subject:** Following up from the Midwest Food Expo - vendor setup
- **Links:** https://greenvalley-produce.example/catalog

**Body**

```text
Hi Dana,

It was good to meet your team at the Midwest Food Expo last month. As discussed, our 2027 catalog is here:

https://greenvalley-produce.example/catalog

To set Harbor Foods up as a customer, please fill in the attached new-account form with your AP contact and billing address and send it back, and we'll have pricing to you within a week.

Regards,
Sam Okafor
Green Valley Produce
```

**Threat intel**

- Sender domain `greenvalley-produce.example`: reputation: unknown, age_days: None, lookalike_of: None
- Link `https://greenvalley-produce.example/catalog`: reputation: unknown, on_blocklist: False

## E-010

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Coastal Freight AR <ar@coastalfreight.example>
- **Reply-To:** ar@coastalfreight.example
- **Subject:** Remittance account change effective immediately
- **Links:** none

**Body**

```text
Dear Dana,

Please note that effective immediately, Coastal Freight's remittance account has changed. The new details are in the attached letter.

Kindly update your records and confirm once the pending invoices 3310 and 3312 have been redirected to the new account.

Regards,
Accounts Receivable
Coastal Freight
```

**Threat intel**

- Sender domain `coastalfreight.example`: reputation: clean, age_days: 3650, lookalike_of: None
