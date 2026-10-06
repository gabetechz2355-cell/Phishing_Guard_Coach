# New cases review (blind)

Twenty emails, E-011 to E-030, exactly as stored in `data/emails.json`, plus the mock threat-intel results for each sender domain, reply-to domain (when it differs), and link (`data/threat_intel.json`). A domain or link with no row shows the tool's default: unknown. No labels, verdicts, red flags, or tool expectations appear here; see `new_review_key.md`.

## E-011

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Special Offers <offers@rx-bestprice.example>
- **Reply-To:** offers@rx-bestprice.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
roper radiusesqu2isnetworkscom toallcountriescialisfastshipping httpmcbvcwbaylivefilestorecomy1pmwhfe7rsfje4hl3hhrdmpnrqui6nrjhk14eoe5hom9omehcwzbjg9pv_bafk7xpfucvrbjhfc1kmvuoh9ymthgindexhtml wed 06 aug 2008 175645 0400 specialpricesnewofferallproducts
```

**Threat intel**

- Sender domain `rx-bestprice.example`: reputation: malicious, age_days: 4, lookalike_of: None

## E-012

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** Brendin Mandy <brendin.mandy@pharma-fastship.example>
- **Reply-To:** brendin.mandy@pharma-fastship.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
brendin mandy furballkinetxcom searching reliable chemists wont find better solution site everything cure bad stateeven need fast delivery always rely us obtain trustworthy help fast mouse click traditionstreetcom 5 aug 2008 214200 discover new wed 06 aug 2008 020831 0000 bigger tool
```

**Threat intel**

- Sender domain `pharma-fastship.example`: reputation: malicious, age_days: 7, lookalike_of: None

## E-013

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Karen Haas <karen.haas@bulkmail-relay.example>
- **Reply-To:** karen.haas@bulkmail-relay.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
karen haas lisawillardeldercricinfocom gaze lisle accompany concede buckeye chemisorb ace chemisorb phytoplankton bert granular divisible upside theyre murky ace upside rankin strobe hookup upside abbe satyr chemisorb michelangelo prolix whitehorse rite ace moratorium willard muddlehead bert status lurch backboard abidjan divisible attestation murky status mushroom muddlehead rankin attestation abbe bert divisible satyr whitehorse fri 08 aug 2008 010259 0100 abidjan dortmund lurch moratorium muddlehead
```

**Threat intel**

- Sender domain `bulkmail-relay.example`: reputation: malicious, age_days: 15, lookalike_of: None

## E-014

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** Harbor Foods IT Service Desk <servicedesk@harb0rfoods.example>
- **Reply-To:** servicedesk@harb0rfoods.example
- **Subject:** Action required: re-enroll your MFA device by end of day
- **Links:** https://harb0rfoods.example/mfa/re-enroll?u=marcus.lee

**Body**

```text
Hi Marcus,

As part of this month's security upgrade, every Harbor Foods account must re-enroll its multi-factor authentication device. Accounts not re-enrolled by 5pm today will be locked out of email, Teams, and the HR portal.

Re-enroll here with your current password and the code from your authenticator app:

https://harb0rfoods.example/mfa/re-enroll?u=marcus.lee

It takes less than two minutes.

Harbor Foods IT Service Desk
```

**Threat intel**

- Sender domain `harb0rfoods.example`: reputation: suspicious, age_days: 5, lookalike_of: harborfoods.example
- Link `https://harb0rfoods.example/mfa/re-enroll?u=marcus.lee`: reputation: suspicious, lookalike_of: harborfoods.example, on_blocklist: False

## E-015

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Voicemail Service <voicemail@voicemail-notify.example>
- **Reply-To:** voicemail@voicemail-notify.example
- **Subject:** New voicemail from +1 (813) 555-0142 (0:48)
- **Links:** https://voicemail-notify.example/play/msg-40917

**Body**

```text
You have a new voicemail message.

From: +1 (813) 555-0142
Length: 0:48
Received: Today 9:12 AM

To listen, sign in with your Microsoft 365 account:

https://voicemail-notify.example/play/msg-40917

Messages are deleted after 7 days.

Voicemail Service
```

**Threat intel**

- Sender domain `voicemail-notify.example`: reputation: malicious, age_days: 8, lookalike_of: None
- Link `https://voicemail-notify.example/play/msg-40917`: reputation: malicious, lookalike_of: None, on_blocklist: True

## E-016

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Aimee Porter <aimee.porter@harborfoods.example>
- **Reply-To:** aimee.porter@harborfoods.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
vacation vacation friday june 2 monday june 12 absence please direct questions issues people bammel storage george grant texaco stella midtexas carlos cp l charlotte hl p charlotte confirmation meters robert error reports sabrae questions leave let know aimee
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None

## E-017

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Dev Forum Mailing List <list@lists.devforum.example>
- **Reply-To:** list@lists.devforum.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
iybzpoboxcom csv module contains sniffer class supposed deduce delimiter quote character well presence absence header sample taken start purported csv file longer remember wrote ive never big fan determines delimiter based almost solely character frequencies doesnt consider actual structure csv file delimiters quote characters almost always taken set punctuation whitespace characters consequently cause occasional headscratching sample abc8def def8ghi ghi8jkl import csv csvsniffersniffsample ddelimiter 8 sample a8bcdef ab8cdef abc8def abcd8ef csvsniffersniffsample ddelimiter f clear people use letters digits often delimiters samples probably represent data singlecolumn files doublecolumn files 8 f delimiter would happy get rid 30 im also aware people use id like feedback python community removed someone wants badly enough maintain pypi thanks skip montanaro iybzpoboxcom httpwwwwebfastcomskip _______________________________________________ python3000 mailing list smsbmo9552pythonorg httpmailpythonorgmailmanlistinfopython3000 unsubscribe httpmailpythonorgmailmanoptionspython3000python300040tangomucom wed 06 aug 2008 095850 0500 python3000 csvsniffer delete python 30
```

**Threat intel**

- Sender domain `lists.devforum.example`: reputation: clean, age_days: 5100, lookalike_of: None

## E-018

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Ray Calder <ray.calder@harborfoods.example>
- **Reply-To:** ray.calder@harborfoods.example
- **Subject:** (empty)
- **Links:** none

**Body**

```text
schedule c reserves trouble valueing transmission literally forever finally released spread option model last night value transmission spit huge values money transmission valued daily option example transmission big eddy northwest nob spit value 28 million extrinsic given state affairs california right find highly unlikely take power northwest deliver capped market last night recognized 16 million transmission value almost intrinsic value associated closing open positions reserved 36 million associated extrinsic value revalue options week make appropriate adjustments reserves let know questions concerns
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None

## E-019

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** PayWell Client Services <clientservices@paywell.example>
- **Reply-To:** clientservices@paywell.example
- **Subject:** Q4 payroll calendar and holiday processing deadlines
- **Links:** https://portal.paywell.example/calendar/2026-q4

**Body**

```text
Hi Marcus,

The Q4 payroll calendar for Harbor Foods is posted in your client portal:

https://portal.paywell.example/calendar/2026-q4

Please note the earlier submission cutoffs for the Thanksgiving and Christmas pay dates. Nothing has changed in your setup, and there is nothing you need to do today. Questions go to your usual service team.

Best regards,
Jordan Pike
Client Services, PayWell
```

**Threat intel**

- Sender domain `paywell.example`: reputation: clean, age_days: 3300, lookalike_of: None
- Link `https://portal.paywell.example/calendar/2026-q4`: reputation: clean, lookalike_of: None, on_blocklist: False

## E-020

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Coastal Freight Dispatch <dispatch@coastalfreight.example>
- **Reply-To:** dispatch@coastalfreight.example
- **Subject:** Shipment CF-88341 delivered to Tampa warehouse
- **Links:** https://track.coastalfreight.example/shipments/CF-88341

**Body**

```text
Hi Dana,

Shipment CF-88341 (14 pallets, PO 55210) was delivered to the Tampa warehouse this morning and signed for by receiving at 7:42 AM. Proof of delivery is on the tracking page:

https://track.coastalfreight.example/shipments/CF-88341

The freight charge will appear on next month's statement as usual.

Coastal Freight Dispatch
```

**Threat intel**

- Sender domain `coastalfreight.example`: reputation: clean, age_days: 3650, lookalike_of: None
- Link `https://track.coastalfreight.example/shipments/CF-88341`: reputation: clean, lookalike_of: None, on_blocklist: False

## E-021

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Kevin Doyle <kevin.doyle@northstar-grocers.example>
- **Reply-To:** kevin.doyle@northstar-grocers.example
- **Subject:** Holiday order - can you quote these quantities?
- **Links:** none

**Body**

```text
Hi Priya,

We're planning the holiday push for our 12 stores. Could you quote the following for delivery the week of Nov 16?

- Frozen turkey, 12-14 lb: 600 cases
- Cranberry sauce, 14 oz: 300 cases
- Stuffing mix: 250 cases

Same terms as last year is fine. If it's easier, call me Thursday and we can go through it.

Thanks,
Kevin
Northstar Grocers Purchasing
```

**Threat intel**

- Sender domain `northstar-grocers.example`: reputation: clean, age_days: 1800, lookalike_of: None

## E-022

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Harbor Foods IT <it-notices@harborfoods.example>
- **Reply-To:** it-notices@harborfoods.example
- **Subject:** Planned maintenance Saturday: sign-in may be slow 6-8am
- **Links:** none

**Body**

```text
Hi all,

IT will apply updates to the sign-in system this Saturday between 6 and 8 AM. You may be asked to sign in again on Monday. You do not need to do anything before then.

A reminder: IT will never email you a link to re-enroll MFA or ask for your password or authenticator code. If anyone does, report it with the Report Phishing button.

Thanks,
Harbor Foods IT
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None

## E-023

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Alicia Brandt <alicia.brandt@metrodeli.example>
- **Reply-To:** alicia.brandt@metrodeli.example
- **Subject:** Shared with you: Q4 order forecast
- **Links:** https://filedrop-share.example/s/q4-forecast-metrodeli

**Body**

```text
Hi Priya,

I've shared our Q4 order forecast with you ahead of next week's call. It has the store-by-store volumes we talked about.

https://filedrop-share.example/s/q4-forecast-metrodeli

Let me know if you have trouble opening it.

Alicia
Metro Deli Purchasing
```

**Threat intel**

- Sender domain `metrodeli.example`: reputation: clean, age_days: 2200, lookalike_of: None
- Link `https://filedrop-share.example/s/q4-forecast-metrodeli`: reputation: unknown, on_blocklist: False

## E-024

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Rob Kessler <rob.kessler@harborfoods.example>
- **Reply-To:** rob.kessler@harborfoods.example
- **Subject:** Sponsorship invoice for the Gulf Coast Grocers summit
- **Links:** none

**Body**

```text
Hi Dana,

We agreed to sponsor the Gulf Coast Grocers summit in November. Their invoice is attached: $9,800, payable to Gulf Coast Events LLC by ACH, bank details on the invoice. They aren't set up as a vendor yet, so could you add them directly and include this in Thursday's payment run? They need it before the event.

Thanks,
Rob

Rob Kessler
Chief Financial Officer, Harbor Foods
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None

## E-025

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Nora Whitley <nora.whitley@freshmarket-co.example>
- **Reply-To:** nora.whitley.fm@quickmail.example
- **Subject:** Updated price list and contacts for 2027 planning
- **Links:** none

**Body**

```text
Hi Priya,

We're starting 2027 planning. Could you send me your current price list and a contact sheet for your sales and accounts payable teams (names, direct lines, emails)? Please reply to my personal address this week; our shared inbox has been unreliable.

Thanks so much,
Nora
Category Buyer, Fresh Market Co.
```

**Threat intel**

- Sender domain `freshmarket-co.example`: reputation: clean, age_days: 1500, lookalike_of: None
- Reply-to domain `quickmail.example`: reputation: clean, age_days: 6200, lookalike_of: None

## E-026

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** TalentBridge Staffing <recruiting@talentbridge-staffing.example>
- **Reply-To:** recruiting@talentbridge-staffing.example
- **Subject:** Shortlist: 5 warehouse candidates available to start Monday
- **Links:** https://talentbridge-staffing.example/candidates/warehouse-shortlist

**Body**

```text
Hi Marcus,

We saw Harbor Foods is hiring warehouse associates in Tampa. We have five pre-screened candidates with forklift certification who can start Monday. Their resumes are in this folder:

https://talentbridge-staffing.example/candidates/warehouse-shortlist

Our standard placement fee applies only if you hire.

Best,
Derek Shaw
TalentBridge Staffing
```

**Threat intel**

- Sender domain `talentbridge-staffing.example`: reputation: unknown, age_days: None, lookalike_of: None
- Link `https://talentbridge-staffing.example/candidates/warehouse-shortlist`: reputation: unknown, on_blocklist: False

## E-027

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Midwest Food Expo <events@midwestfoodexpo.example>
- **Reply-To:** events@midwestfoodexpo.example
- **Subject:** 48 hours left: early-bird exhibitor pricing ends Friday
- **Links:** https://register.midwestfoodexpo.example/2027/exhibitors

**Body**

```text
Hi Priya,

Thanks for exhibiting at the Midwest Food Expo this year. Early-bird pricing for 2027 exhibitor booths ends in 48 hours. Reserve your booth now for $1,950 (regular price $2,600):

https://register.midwestfoodexpo.example/2027/exhibitors

Prime aisle locations go first, and this year's exhibitors get first pick until Friday at midnight.

Midwest Food Expo Team
```

**Threat intel**

- Sender domain `midwestfoodexpo.example`: reputation: unknown, age_days: None, lookalike_of: None
- Link `https://register.midwestfoodexpo.example/2027/exhibitors`: reputation: unknown, on_blocklist: False

## E-028

- **To:** Marcus Lee (U-02, HR Coordinator)
- **From:** PayWell Client Security <security@paywell.example>
- **Reply-To:** security@paywell.example
- **Subject:** Annual administrator re-verification due Oct 15
- **Links:** https://verify.paywell.example/admin-attestation

**Body**

```text
Hi Marcus,

Each year before W-2 season, PayWell asks every client administrator to re-verify their access. Please sign in and confirm your administrator role by October 15, or your admin access will be paused until you contact us:

https://verify.paywell.example/admin-attestation

If you have questions, call your service team at the number in your PayWell contract.

PayWell Client Security
```

**Threat intel**

- Sender domain `paywell.example`: reputation: clean, age_days: 3300, lookalike_of: None
- Link `https://verify.paywell.example/admin-attestation`: reputation: unknown, on_blocklist: False

## E-029

- **To:** Dana Ruiz (U-01, Accounts Payable)
- **From:** Harbor Foods Finance <finance@harborfoods.example>
- **Reply-To:** finance@harborfoods.example
- **Subject:** New expense tool: create your Tallyline account by Friday
- **Links:** https://harborfoods.tallyline.example/signup

**Body**

```text
Hi Dana,

As announced at last week's all-hands, Harbor Foods is moving expense reports to Tallyline on November 1. Please create your account by Friday with your work email:

https://harborfoods.tallyline.example/signup

Expense reports submitted the old way after October 31 won't be reimbursed. Questions go to finance@harborfoods.example.

Harbor Foods Finance
```

**Threat intel**

- Sender domain `harborfoods.example`: reputation: clean, age_days: 5840, lookalike_of: None
- Link `https://harborfoods.tallyline.example/signup`: reputation: unknown, on_blocklist: False

## E-030

- **To:** Priya Shah (U-03, Regional Sales)
- **From:** Maya Torres <maya.torres@northstar-grocers.example>
- **Reply-To:** maya.torres.work@quickmail.example
- **Subject:** November delivery schedule - please use my other address
- **Links:** none

**Body**

```text
Hi Priya,

Our email server is being migrated this week and replies to my work address are bouncing. Could you send the November delivery schedule for our Westside and Lakeport stores to my personal address in the meantime? IT says we should be back to normal by Monday.

Thanks,
Maya
Store Operations, Northstar Grocers
```

**Threat intel**

- Sender domain `northstar-grocers.example`: reputation: clean, age_days: 1800, lookalike_of: None
- Reply-to domain `quickmail.example`: reputation: clean, age_days: 6200, lookalike_of: None
