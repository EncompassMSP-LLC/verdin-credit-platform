import type { ConsentDocumentTemplateKey, ConsentType } from '@verdin/api-client';

export const CONSENT_TEMPLATE_LABELS: Record<ConsentDocumentTemplateKey, string> = {
  croa_disclosure: 'CROA disclosure statement',
  croa_service_agreement: 'Credit repair service agreement',
  fcra_authorization: 'FCRA dispute authorization',
};

export const CONSENT_TYPE_LABELS: Record<ConsentType, string> = {
  croa_services: 'CROA services agreement',
  fcra_dispute: 'FCRA dispute authorization',
  fdcpa_contact: 'FDCPA contact consent',
  marketing: 'Marketing consent',
  data_processing: 'Data processing consent',
};

export const TEMPLATE_TO_CONSENT_TYPE: Record<ConsentDocumentTemplateKey, ConsentType> = {
  croa_disclosure: 'croa_services',
  croa_service_agreement: 'croa_services',
  fcra_authorization: 'fcra_dispute',
};

export function consentTemplateLabels(keys: ConsentDocumentTemplateKey[]): string[] {
  return keys.map((key) => CONSENT_TEMPLATE_LABELS[key]);
}

export function consentTypeLabels(types: ConsentType[]): string[] {
  return types.map((type) => CONSENT_TYPE_LABELS[type]);
}
