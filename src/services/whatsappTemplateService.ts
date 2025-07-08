import axios from "axios"
import { WHATSAPP_CONFIG } from "../config/whatsapp"

export class WhatsAppTemplateService {
  static async createMessageTemplate(templateData: {
    name: string
    language: string
    category: "MARKETING" | "UTILITY" | "AUTHENTICATION"
    components: any[]
  }): Promise<string> {
    try {
      const response = await axios.post(
        `${WHATSAPP_CONFIG.BASE_URL}/${WHATSAPP_CONFIG.BUSINESS_ACCOUNT_ID}/message_templates`,
        templateData,
        {
          headers: {
            Authorization: `Bearer ${WHATSAPP_CONFIG.ACCESS_TOKEN}`,
            "Content-Type": "application/json",
          },
        },
      )

      console.log("Template created:", response.data)
      return response.data.id
    } catch (error) {
      console.error("Template creation error:", error)
      throw error
    }
  }

  static async getApprovedTemplates(): Promise<any[]> {
    try {
      const response = await axios.get(
        `${WHATSAPP_CONFIG.BASE_URL}/${WHATSAPP_CONFIG.BUSINESS_ACCOUNT_ID}/message_templates`,
        {
          headers: {
            Authorization: `Bearer ${WHATSAPP_CONFIG.ACCESS_TOKEN}`,
          },
          params: {
            status: "APPROVED",
            limit: 100,
          },
        },
      )

      return response.data.data || []
    } catch (error) {
      console.error("Get templates error:", error)
      return []
    }
  }

  static async setupDefaultTemplates(): Promise<void> {
    const templates = [
      {
        name: "payment_reminder_hindi",
        language: "hi",
        category: "UTILITY" as const,
        components: [
          {
            type: "HEADER",
            format: "TEXT",
            text: "भुगतान अनुस्मारक",
          },
          {
            type: "BODY",
            text: "नमस्ते {{1}},\n\nआपका ₹{{2}} का भुगतान {{3}} को देय है। कृपया जल्दी भुगतान करें।\n\nभुगतान करने के लिए यहाँ क्लिक करें: {{4}}",
            example: {
              body_text: [["राजेश कुमार", "25,000", "15 जनवरी 2024", "https://pay.debtbot.ai/abc123"]],
            },
          },
          {
            type: "FOOTER",
            text: "DebtBot AI - RBI अनुपालित",
          },
          {
            type: "BUTTONS",
            buttons: [
              {
                type: "URL",
                text: "अभी भुगतान करें",
                url: "{{1}}",
                example: ["https://pay.debtbot.ai/abc123"],
              },
              {
                type: "QUICK_REPLY",
                text: "EMI विकल्प",
              },
            ],
          },
        ],
      },
      {
        name: "payment_reminder_english",
        language: "en",
        category: "UTILITY" as const,
        components: [
          {
            type: "HEADER",
            format: "TEXT",
            text: "Payment Reminder",
          },
          {
            type: "BODY",
            text: "Hello {{1}},\n\nYour payment of ₹{{2}} is due on {{3}}. Please make the payment immediately.\n\nClick here to pay: {{4}}",
            example: {
              body_text: [["Rajesh Kumar", "25,000", "January 15, 2024", "https://pay.debtbot.ai/abc123"]],
            },
          },
          {
            type: "FOOTER",
            text: "DebtBot AI - RBI Compliant",
          },
          {
            type: "BUTTONS",
            buttons: [
              {
                type: "URL",
                text: "Pay Now",
                url: "{{1}}",
                example: ["https://pay.debtbot.ai/abc123"],
              },
              {
                type: "QUICK_REPLY",
                text: "EMI Options",
              },
            ],
          },
        ],
      },
      {
        name: "emi_offer_hinglish",
        language: "en",
        category: "UTILITY" as const,
        components: [
          {
            type: "HEADER",
            format: "TEXT",
            text: "EMI Offer - आसान किस्त",
          },
          {
            type: "BODY",
            text: "Hi {{1}},\n\nAapke liye special EMI plan available hai!\n\n₹{{2}} ko {{3}} months mein pay kar sakte hain.\nMonthly EMI: ₹{{4}}\n\nInterested? Reply YES",
            example: {
              body_text: [["Priya", "25,000", "12", "2,300"]],
            },
          },
          {
            type: "BUTTONS",
            buttons: [
              {
                type: "QUICK_REPLY",
                text: "YES - EMI chahiye",
              },
              {
                type: "QUICK_REPLY",
                text: "More details",
              },
            ],
          },
        ],
      },
    ]

    for (const template of templates) {
      try {
        await this.createMessageTemplate(template)
        console.log(`Template ${template.name} created successfully`)
      } catch (error) {
        console.error(`Failed to create template ${template.name}:`, error)
      }
    }
  }
}
