"""Default consent and contract template bodies (DRAFT — for legal review)."""

from __future__ import annotations

from dataclasses import dataclass

from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey


@dataclass(frozen=True, slots=True)
class ConsentTemplateDefault:
    key: ConsentDocumentTemplateKey
    title: str
    body_text: str


def _croa_disclosure_body() -> str:
    return """IMPORTANT INFORMATION FOR CONSUMERS

Credit Repair Organization: {{organization_name}}
{{organization_address}}
Phone: {{organization_phone}} | Email: {{organization_email}}

Consumer: {{client_name}}
Date: {{effective_date}}

NOTICE REQUIRED BY THE CREDIT REPAIR ORGANIZATIONS ACT (15 U.S.C. § 1679 et seq.)

You have a right to dispute inaccurate information in your credit report by contacting the credit bureau directly. Neither you nor any credit repair organization has the right to have accurate, current, and verifiable information removed from your credit report. The credit bureau must remove accurate, negative information from your report only if it is over seven years old (ten years for bankruptcies) or cannot be verified.

You have a right to obtain a copy of your credit report from each of the nationwide consumer reporting agencies once every 12 months by visiting www.annualcreditreport.com or calling 1-877-322-8228.

You have a right to sue a credit repair organization that violates the Credit Repair Organizations Act. This law prohibits deceptive practices by credit repair organizations.

You have the right to cancel your contract with any credit repair organization for any reason within 3 business days from the date you signed it.

Credit bureaus are required by federal law to investigate most disputes you submit, usually within 30 days (unless your dispute is considered frivolous).

No one can legally remove accurate and timely negative information from a credit report.

CREDIT REPAIR ORGANIZATION DISCLOSURES

1. Total cost of services. The total amount you will pay for credit repair services under your service agreement is: {{total_service_fee}}.

2. Payment terms. {{payment_terms}}

3. Description of services. {{services_description}}

4. Estimated time to complete services. {{estimated_completion_time}}

5. Guarantees. {{guarantee_statement}}

6. Right to cancel. You may cancel this contract without penalty or obligation at any time before midnight of the 3rd business day after the date on which you signed the contract. See the attached notice of cancellation form for instructions.

7. State law rights. {{state_law_notice}}

CONSUMER ACKNOWLEDGMENT

I acknowledge that I have received and read this disclosure statement before signing any contract for credit repair services with {{organization_name}}.

Consumer printed name: {{client_name}}

Consumer signature: _________________________________   Date: _______________

Organization representative: __________________________   Date: _______________"""


def _croa_service_agreement_body() -> str:
    return """CREDIT REPAIR SERVICES AGREEMENT

This Credit Repair Services Agreement ("Agreement") is entered into as of {{effective_date}} ("Effective Date") by and between:

Service Provider: {{organization_name}}
Address: {{organization_address}}
Phone: {{organization_phone}} | Email: {{organization_email}}
("Company")

and

Consumer: {{client_name}}
Address: {{client_address}}
Email: {{client_email}} | Phone: {{client_phone}}
("Client").

RECITALS

Client desires to retain Company to provide credit repair and related consumer-reporting assistance services. Company agrees to perform such services in compliance with the Credit Repair Organizations Act (CROA), the Fair Credit Reporting Act (FCRA), applicable state credit services organization laws, and all other applicable federal and state laws.

1. SERVICES

Company will provide the following services ("Services"):
{{services_description}}

Company will not advise Client to make false statements to credit bureaus, creditors, or others, and will not assist Client in creating a new credit identity.

2. CLIENT RESPONSIBILITIES

Client agrees to:
(a) Provide truthful, complete, and timely information and documentation reasonably requested by Company;
(b) Review all dispute materials before submission and promptly notify Company of any inaccuracies;
(c) Maintain copies of all correspondence and documents related to credit reports and disputes;
(d) Not incur new derogatory credit during the engagement without informing Company.

3. FEES AND PAYMENT

Total fee for Services: {{total_service_fee}}
Payment schedule: {{payment_terms}}

CROA COMPLIANCE: Company will not charge or receive any money from Client for the performance of any service before such service is fully performed, except as permitted by applicable law and as expressly set forth in this Agreement.

4. TERM AND TERMINATION

This Agreement begins on the Effective Date and continues until terminated. Either party may terminate upon {{termination_notice_days}} days' written notice. Client may cancel without penalty within three (3) business days of signing pursuant to CROA and the Notice of Cancellation attached hereto.

Upon termination, Company will cease performing Services except as needed to close Client's file in an orderly manner. Fees for Services fully performed prior to termination remain due.

5. NO GUARANTEE OF RESULTS

{{guarantee_statement}}

Company does not guarantee any specific increase in credit score, deletion of any particular item, or any particular outcome with credit bureaus or creditors.

6. FCRA AUTHORIZATION

Client's authorization for Company to act on Client's behalf with consumer reporting agencies is set forth in the separate FCRA Dispute Authorization executed concurrently with this Agreement.

7. CONFIDENTIALITY AND DATA SECURITY

Company will use reasonable administrative, technical, and physical safeguards to protect Client's personal information. Company will not sell Client's personal information.

8. DISPUTE RESOLUTION

{{dispute_resolution_clause}}

9. GOVERNING LAW

This Agreement is governed by the laws of {{governing_state}}, without regard to conflict-of-law principles.

10. ENTIRE AGREEMENT

This Agreement, together with the CROA Disclosure Statement, Notice of Cancellation, and FCRA Authorization, constitutes the entire agreement between the parties.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

COMPANY: {{organization_name}}

By: _________________________________   Date: _______________
Name/Title: ___________________________

CLIENT:

{{client_name}}

Signature: _________________________________   Date: _______________"""


def _fcra_authorization_body() -> str:
    return """AUTHORIZATION TO OBTAIN AND DISPUTE CONSUMER REPORT INFORMATION

(Fair Credit Reporting Act — 15 U.S.C. § 1681 et seq.)

Date: {{effective_date}}

I, {{client_name}}, residing at {{client_address}}, hereby authorize {{organization_name}} ("Authorized Agent") to act on my behalf for purposes related to my consumer credit reports and disputes under the Fair Credit Reporting Act.

1. SCOPE OF AUTHORIZATION

I authorize Authorized Agent to:
(a) Obtain copies of my consumer reports from Experian, Equifax, TransUnion, and other consumer reporting agencies as needed to perform agreed credit repair services;
(b) Review and analyze information contained in my consumer reports;
(c) Prepare and submit disputes, requests for reinvestigation, and requests for verification of disputed information on my behalf;
(d) Communicate with consumer reporting agencies, data furnishers, and creditors regarding disputes and responses;
(e) Receive copies of dispute results, updated reports, and related correspondence on my behalf when permitted by law.

2. PERSONAL IDENTIFYING INFORMATION

I authorize Authorized Agent to use the following information in connection with the above activities:
Name: {{client_name}}
Date of birth: {{client_date_of_birth}}
Last four digits of SSN (if provided): {{client_ssn_last4}}
Current address: {{client_address}}
Prior addresses (if applicable): {{client_prior_addresses}}

3. DURATION

This authorization remains in effect until {{authorization_expiration}} or until I revoke it in writing, whichever occurs first.

4. REVOCATION

I may revoke this authorization at any time by sending written notice to {{organization_email}} or {{organization_address}}. Revocation will not affect actions taken in good faith before Authorized Agent receives notice.

5. ACKNOWLEDGMENTS

I understand that:
(a) Consumer reporting agencies are not required to remove accurate, current, and verifiable information;
(b) I have the right to dispute information directly with consumer reporting agencies without using a third party;
(c) Authorized Agent is not a law firm unless separately engaged as such, and this authorization does not create an attorney-client relationship unless a separate written agreement says otherwise.

6. SIGNATURE

I certify that the information I have provided is true and correct to the best of my knowledge.

Consumer printed name: {{client_name}}

Consumer signature: _________________________________   Date: _______________

If signed electronically, the electronic signature above constitutes my legal signature under the E-SIGN Act and applicable state law."""


DEFAULT_CONSENT_TEMPLATES: tuple[ConsentTemplateDefault, ...] = (
    ConsentTemplateDefault(
        key=ConsentDocumentTemplateKey.CROA_DISCLOSURE,
        title="CROA Disclosure Statement",
        body_text=_croa_disclosure_body(),
    ),
    ConsentTemplateDefault(
        key=ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT,
        title="Credit Repair Services Agreement",
        body_text=_croa_service_agreement_body(),
    ),
    ConsentTemplateDefault(
        key=ConsentDocumentTemplateKey.FCRA_AUTHORIZATION,
        title="FCRA Dispute Authorization",
        body_text=_fcra_authorization_body(),
    ),
)

DEFAULT_TEMPLATE_BY_KEY: dict[ConsentDocumentTemplateKey, ConsentTemplateDefault] = {
    item.key: item for item in DEFAULT_CONSENT_TEMPLATES
}
