// WhatsApp Business API Configuration
export const WHATSAPP_CONFIG = {
  BASE_URL: "https://graph.facebook.com/v18.0",
  PHONE_NUMBER_ID: "674138942450620",
  ACCESS_TOKEN:
    "EAAIrYgZBTkUsBO4Fi5uTUP2FEhpLKor9wQo6TyplVqZCVBNo8gkzydLq7JDlWGENZAfcG4u6vKTzyJBhMhmSsV9WSubrW6gAsSxZAhsZB5hKzGk4ToWVIJFazEzlYAYLJlSC8sKxsAAXKAFf9JYPMGUhxNCZAO5BobVsrfTDLelvvkk7O5545Mg2AZBiVD8TsOz7ezZC6TZAC7TCiMisnmam4qu196DPut1CYW5ikiZC4wqrusWMsZD",
  BUSINESS_ACCOUNT_ID: "1821321785109097",
  APP_ID: "561175716819868",
  WHATSAPP_NUMBER: "917439330282",
  VERIFY_TOKEN: "debt_collection_webhook_verify_2024",

  // Indian phone number validation
  PHONE_REGEX: /^(\+91|91|0)?[6-9]\d{9}$/,

  // Message templates for different languages
  TEMPLATES: {
    PAYMENT_REMINDER_HI: "payment_reminder_hindi",
    PAYMENT_REMINDER_EN: "payment_reminder_english",
    EMI_OFFER_HI: "emi_offer_hindi",
    EMI_OFFER_EN: "emi_offer_english",
    SETTLEMENT_OFFER: "settlement_offer",
    FINAL_NOTICE: "final_notice",
  },
}

export const validateIndianPhoneNumber = (phone: string): boolean => {
  return WHATSAPP_CONFIG.PHONE_REGEX.test(phone)
}

export const formatIndianPhoneNumber = (phone: string): string => {
  // Remove all non-digits
  const digits = phone.replace(/\D/g, "")

  // Handle different formats
  if (digits.startsWith("91") && digits.length === 12) {
    return digits // Already in correct format
  } else if (digits.startsWith("0") && digits.length === 11) {
    return `91${digits.substring(1)}` // Remove leading 0 and add 91
  } else if (digits.length === 10) {
    return `91${digits}` // Add country code
  }

  return digits // Return as is if format is unclear
}
