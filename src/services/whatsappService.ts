import axios from "axios"

export class WhatsAppService {
  private static readonly BASE_URL = "https://graph.facebook.com/v18.0"
  private static readonly PHONE_NUMBER_ID = "674138942450620"
  private static readonly ACCESS_TOKEN =
    "EAAIrYgZBTkUsBO4Fi5uTUP2FEhpLKor9wQo6TyplVqZCVBNo8gkzydLq7JDlWGENZAfcG4u6vKTzyJBhMhmSsV9WSubrW6gAsSxZAhsZB5hKzGk4ToWVIJFazEzlYAYLJlSC8sKxsAAXKAFf9JYPMGUhxNCZAO5BobVsrfTDLelvvkk7O5545Mg2AZBiVD8TsOz7ezZC6TZAC7TCiMisnmam4qu196DPut1CYW5ikiZC4wqrusWMsZD"
  private static readonly BUSINESS_ACCOUNT_ID = "1821321785109097"
  private static readonly APP_ID = "561175716819868"
  private static readonly WHATSAPP_NUMBER = "917439330282" // Your WhatsApp number

  static async sendMessage(to: string, message: string, templateId?: string): Promise<void> {
    try {
      const payload = templateId
        ? this.buildTemplateMessage(to, templateId, message)
        : this.buildTextMessage(to, message)

      const response = await axios.post(`${this.BASE_URL}/${this.PHONE_NUMBER_ID}/messages`, payload, {
        headers: {
          Authorization: `Bearer ${this.ACCESS_TOKEN}`,
          "Content-Type": "application/json",
        },
      })

      console.log("WhatsApp message sent:", response.data)
    } catch (error) {
      console.error("WhatsApp send error:", error)
      throw error
    }
  }

  private static buildTextMessage(to: string, message: string) {
    // Ensure phone number is in correct format (remove + and spaces)
    const cleanPhone = to.replace(/[\s+\-()]/g, "")

    return {
      messaging_product: "whatsapp",
      to: cleanPhone.startsWith("91") ? cleanPhone : `91${cleanPhone}`,
      type: "text",
      text: {
        body: message,
        preview_url: false,
      },
    }
  }

  private static buildTemplateMessage(to: string, templateId: string, message: string) {
    return {
      messaging_product: "whatsapp",
      to: to.replace(/\D/g, ""),
      type: "template",
      template: {
        name: templateId,
        language: {
          code: "en",
        },
        components: [
          {
            type: "body",
            parameters: [
              {
                type: "text",
                text: message,
              },
            ],
          },
        ],
      },
    }
  }

  static async handleWebhook(body: any): Promise<void> {
    try {
      if (body.entry && body.entry[0].changes && body.entry[0].changes[0].value.messages) {
        const message = body.entry[0].changes[0].value.messages[0]
        const from = message.from
        let messageBody = ""

        if (message.type === "text") {
          messageBody = message.text?.body || ""
          console.log(`Received WhatsApp message from ${from}: ${messageBody}`)
          await this.processIncomingMessage(from, messageBody)
        } else if (message.type === "interactive" && message.interactive.type === "button_reply") {
          const buttonText = message.interactive.button_reply.title
          console.log(`Received WhatsApp quick reply from ${from}: ${buttonText}`)
          await this.handleQuickReply(from, buttonText)
        }
      }

      // Handle status updates
      if (body.entry && body.entry[0].changes && body.entry[0].changes[0].value.statuses) {
        const status = body.entry[0].changes[0].value.statuses[0]
        await this.handleStatusUpdate(status)
      }
    } catch (error) {
      console.error("WhatsApp webhook processing error:", error)
    }
  }

  private static async processIncomingMessage(from: string, message: string): Promise<void> {
    // Find or create chat session
    const session = await this.findOrCreateSession(from, "whatsapp")

    // Save incoming message
    await this.saveMessage(session.id, "user", message)

    // Generate AI response
    const aiResponse = await this.generateResponse(session, message)

    // Send response
    await this.sendMessage(from, aiResponse.content)

    // Save bot response
    await this.saveMessage(session.id, "bot", aiResponse.content)
  }

  private static async findOrCreateSession(phone: string, platform: string): Promise<any> {
    // Implementation to find or create chat session
    // This would interact with your database
    return { id: "session-id", borrowerId: "borrower-id" }
  }

  private static async saveMessage(sessionId: string, senderType: string, content: string): Promise<void> {
    // Implementation to save message to database
  }

  private static async generateResponse(session: any, message: string): Promise<any> {
    // Implementation to generate AI response
    return { content: "AI generated response", language: "en" }
  }

  private static async handleStatusUpdate(status: any): Promise<void> {
    // Update message delivery status in database
    console.log("Message status update:", status)
  }

  static async verifyBusinessAccount(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.BASE_URL}/${this.BUSINESS_ACCOUNT_ID}`, {
        headers: {
          Authorization: `Bearer ${this.ACCESS_TOKEN}`,
        },
        params: {
          fields: "id,name,timezone_offset_min,message_template_namespace",
        },
      })

      console.log("WhatsApp Business Account verified:", response.data)
      return true
    } catch (error) {
      console.error("WhatsApp Business Account verification failed:", error)
      return false
    }
  }

  static async sendTemplateMessage(to: string, templateName: string, parameters: string[] = []): Promise<void> {
    try {
      const payload = {
        messaging_product: "whatsapp",
        to: to.replace(/\D/g, ""),
        type: "template",
        template: {
          name: templateName,
          language: {
            code: templateName.includes("hindi") ? "hi" : "en",
          },
          components: [
            {
              type: "body",
              parameters: parameters.map((param) => ({
                type: "text",
                text: param,
              })),
            },
          ],
        },
      }

      const response = await axios.post(`${this.BASE_URL}/${this.PHONE_NUMBER_ID}/messages`, payload, {
        headers: {
          Authorization: `Bearer ${this.ACCESS_TOKEN}`,
          "Content-Type": "application/json",
        },
      })

      console.log("WhatsApp template message sent:", response.data)
    } catch (error) {
      console.error("WhatsApp template send error:", error)
      throw error
    }
  }

  static async handleQuickReply(from: string, buttonText: string): Promise<void> {
    let response = ""

    switch (buttonText.toLowerCase()) {
      case "emi options":
      case "emi chahiye":
        response =
          "हमारे पास आपके लिए विभिन्न EMI विकल्प उपलब्ध हैं:\n\n1. 6 महीने - ₹4,500/महीना\n2. 12 महीने - ₹2,300/महीना\n3. 18 महीने - ₹1,600/महीना\n\nकौन सा विकल्प आपको पसंद है?"
        break
      case "more details":
        response = "EMI की अधिक जानकारी के लिए हमारे एजेंट से बात करें। कॉल बैक के लिए YES भेजें।"
        break
      default:
        response = "धन्यवाद! हमारा एजेंट जल्द ही आपसे संपर्क करेगा।"
    }

    await this.sendMessage(from, response)
  }
}
