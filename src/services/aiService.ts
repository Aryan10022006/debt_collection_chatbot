import { generateText } from "ai"
import { xai } from "@ai-sdk/xai"
import type { AIResponse, DebtAccount, Borrower } from "../types"
import { LanguageService } from "./languageService"

export class AIService {
  private static readonly SYSTEM_PROMPTS = {
    hi: `आप एक पेशेवर और सहानुभूतिपूर्ण ऋण वसूली AI सहायक हैं। 
    
महत्वपूर्ण दिशानिर्देश:
- हमेशा सम्मानजनक, पेशेवर और RBI दिशानिर्देशों का अनुपालन करें
- कभी भी आक्रामक, धमकी भरा या परेशान करने वाला न हों
- पारस्परिक रूप से लाभकारी समाधान खोजने पर ध्यान दें
- भुगतान योजना, EMI विकल्प और निपटान चर्चा की पेशकश करें
- भारतीय संदर्भ के लिए सांस्कृतिक रूप से संवेदनशील और उपयुक्त रहें`,

    en: `You are a professional, empathetic debt collection AI assistant for India.

IMPORTANT GUIDELINES:
- Always be respectful, professional, and compliant with RBI guidelines
- Never be aggressive, threatening, or harassing
- Focus on finding mutually beneficial solutions
- Offer payment plans, EMI options, and settlement discussions
- Be culturally sensitive and appropriate for Indian context`,

    "en-IN": `Aap ek professional aur empathetic debt collection AI assistant hain India ke liye.

IMPORTANT GUIDELINES:
- Hamesha respectful, professional aur RBI guidelines ke compliant rahiye
- Kabhi bhi aggressive, threatening ya harassing na baniye
- Mutually beneficial solutions dhundne par focus kariye
- Payment plans, EMI options aur settlement discussions offer kariye
- Indian context ke liye culturally sensitive aur appropriate rahiye`,
  }

  static async generateResponse(
    message: string,
    borrower: Borrower,
    debtAccount: DebtAccount,
    conversationHistory: string[] = [],
  ): Promise<AIResponse> {
    try {
      // Detect language
      const detectedLanguage = await LanguageService.detectLanguage(message)

      // Get appropriate system prompt
      const systemPrompt = this.getSystemPrompt(detectedLanguage, borrower, debtAccount)

      // Prepare conversation context
      const context = this.buildContext(conversationHistory, borrower, debtAccount)

      const { text } = await generateText({
        model: xai("grok-3"),
        system: systemPrompt,
        messages: [
          { role: "system", content: context },
          { role: "user", content: message },
        ],
        temperature: 0.7,
        maxTokens: 500,
      })

      // Extract intent and entities
      const intent = await this.extractIntent(message, detectedLanguage)
      const entities = await this.extractEntities(message, detectedLanguage)

      return {
        content: text,
        language: detectedLanguage,
        intent,
        entities,
        confidence: 0.9,
        suggestedActions: this.getSuggestedActions(intent, debtAccount),
      }
    } catch (error) {
      console.error("AI Service error:", error)
      return this.getFallbackResponse(message, borrower, debtAccount)
    }
  }

  private static getSystemPrompt(language: string, borrower: Borrower, debtAccount: DebtAccount): string {
    const basePrompt = this.SYSTEM_PROMPTS[language as keyof typeof this.SYSTEM_PROMPTS] || this.SYSTEM_PROMPTS["en"]

    return `${basePrompt}

BORROWER INFORMATION:
- Name: ${borrower.name}
- Account: ${debtAccount.accountNumber}
- Outstanding Amount: ₹${debtAccount.outstandingAmount.toLocaleString("en-IN")}
- Due Date: ${debtAccount.dueDate.toLocaleDateString("en-IN")}
- Status: ${debtAccount.status}

COMPLIANCE REQUIREMENTS:
- Never threaten legal action unless specifically authorized
- Always offer reasonable payment options
- Respect if customer requests to stop communication
- Maintain professional tone throughout
- Document all interactions properly

Your goal is to recover debt while maintaining customer relationships and following all regulatory guidelines.`
  }

  private static buildContext(history: string[], borrower: Borrower, debtAccount: DebtAccount): string {
    const recentHistory = history.slice(-10).join("\n")

    return `CONVERSATION CONTEXT:
Borrower: ${borrower.name}
Outstanding Amount: ₹${debtAccount.outstandingAmount.toLocaleString("en-IN")}
Account Status: ${debtAccount.status}
Preferred Language: ${borrower.preferredLanguage}

RECENT CONVERSATION:
${recentHistory}

Please respond appropriately based on the context and maintain consistency with previous interactions.`
  }

  private static async extractIntent(message: string, language: string): Promise<string> {
    const intents = {
      payment_inquiry: ["payment", "pay", "amount", "due", "भुगतान", "पैसा", "रकम"],
      payment_promise: ["will pay", "can pay", "tomorrow", "next week", "भुगतान करूंगा", "पैसे दूंगा"],
      dispute: ["wrong", "mistake", "not mine", "dispute", "गलत", "गलती"],
      hardship: ["problem", "difficulty", "job loss", "medical", "समस्या", "परेशानी"],
      settlement: ["settle", "discount", "reduce", "समझौता", "कम"],
      emi_request: ["installment", "emi", "monthly", "किस्त", "मासिक"],
    }

    const lowerMessage = message.toLowerCase()

    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some((keyword) => lowerMessage.includes(keyword.toLowerCase()))) {
        return intent
      }
    }

    return "general_inquiry"
  }

  private static async extractEntities(message: string, language: string): Promise<Record<string, any>> {
    const entities: Record<string, any> = {}

    // Extract amounts
    const amountRegex = /₹?(\d+(?:,\d+)*(?:\.\d{2})?)/g
    const amounts = message.match(amountRegex)
    if (amounts) {
      entities.amounts = amounts.map((amount) => Number.parseFloat(amount.replace(/[₹,]/g, "")))
    }

    // Extract dates
    const dateRegex = /(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|tomorrow|next week|अगले सप्ताह|कल/gi
    const dates = message.match(dateRegex)
    if (dates) {
      entities.dates = dates
    }

    // Extract phone numbers
    const phoneRegex = /(\+91|91)?[-\s]?[6-9]\d{9}/g
    const phones = message.match(phoneRegex)
    if (phones) {
      entities.phoneNumbers = phones
    }

    return entities
  }

  private static getSuggestedActions(intent: string, debtAccount: DebtAccount): string[] {
    const actions: Record<string, string[]> = {
      payment_inquiry: ["show_payment_options", "calculate_interest", "payment_history"],
      payment_promise: ["schedule_followup", "send_payment_link", "confirm_amount"],
      dispute: ["escalate_to_agent", "request_documents", "schedule_call"],
      hardship: ["offer_emi_plan", "discuss_settlement", "financial_counseling"],
      settlement: ["calculate_settlement", "get_approval", "generate_offer"],
      emi_request: ["calculate_emi", "show_emi_options", "setup_autopay"],
    }

    return actions[intent] || ["general_assistance", "escalate_to_agent"]
  }

  private static getFallbackResponse(message: string, borrower: Borrower, debtAccount: DebtAccount): AIResponse {
    const language = borrower.preferredLanguage || "en"

    const fallbackMessages = {
      hi: `नमस्ते ${borrower.name}! मैं आपकी सहायता करने के लिए यहाँ हूँ। आपका बकाया राशि ₹${debtAccount.outstandingAmount.toLocaleString("en-IN")} है। कृपया बताएं कि मैं आपकी कैसे मदद कर सकता हूँ?`,
      en: `Hello ${borrower.name}! I'm here to help you. Your outstanding amount is ₹${debtAccount.outstandingAmount.toLocaleString("en-IN")}. How can I assist you today?`,
      "en-IN": `Hello ${borrower.name}! Main aapki help karne ke liye yahan hun. Aapka outstanding amount ₹${debtAccount.outstandingAmount.toLocaleString("en-IN")} hai. Kya main aapki koi help kar sakta hun?`,
    }

    return {
      content: fallbackMessages[language as keyof typeof fallbackMessages] || fallbackMessages["en"],
      language,
      intent: "general_inquiry",
      entities: {},
      confidence: 0.5,
      suggestedActions: ["general_assistance", "payment_options"],
    }
  }
}
