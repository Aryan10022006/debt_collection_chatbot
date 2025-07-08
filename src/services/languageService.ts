import type { TranslationRequest, TranslationResponse } from "../types"

export class LanguageService {
  private static readonly SUPPORTED_LANGUAGES = {
    hi: "Hindi",
    mr: "Marathi",
    ta: "Tamil",
    te: "Telugu",
    en: "English",
    "en-IN": "Hinglish",
  }

  static async detectLanguage(text: string): Promise<string> {
    // Language detection logic
    const patterns = {
      hi: /[\u0900-\u097F]/,
      mr: /[\u0900-\u097F]/,
      ta: /[\u0B80-\u0BFF]/,
      te: /[\u0C00-\u0C7F]/,
      en: /^[a-zA-Z\s.,!?]+$/,
    }

    // Check for Devanagari script (Hindi/Marathi)
    if (patterns.hi.test(text)) {
      // More sophisticated detection between Hindi and Marathi
      const marathiWords = ["आहे", "होते", "करतो", "मराठी"]
      const hindiWords = ["है", "था", "करता", "हिंदी"]

      const marathiCount = marathiWords.filter((word) => text.includes(word)).length
      const hindiCount = hindiWords.filter((word) => text.includes(word)).length

      return marathiCount > hindiCount ? "mr" : "hi"
    }

    // Check for Tamil script
    if (patterns.ta.test(text)) return "ta"

    // Check for Telugu script
    if (patterns.te.test(text)) return "te"

    // Check for Hinglish (mix of English and Hindi words)
    const hinglishPatterns = [/\b(hai|hain|kar|kya|aap|main|hum)\b/i, /\b(paisa|rupee|payment|amount)\b/i]

    if (hinglishPatterns.some((pattern) => pattern.test(text))) {
      return "en-IN"
    }

    // Default to English
    return "en"
  }

  static async translateText(request: TranslationRequest): Promise<TranslationResponse> {
    const { text, fromLanguage, toLanguage } = request

    // If same language, return as is
    if (fromLanguage === toLanguage) {
      return {
        translatedText: text,
        confidence: 1.0,
        detectedLanguage: fromLanguage,
      }
    }

    try {
      // In production, integrate with Google Translate API or Azure Translator
      const translatedText = await this.performTranslation(text, fromLanguage, toLanguage)

      return {
        translatedText,
        confidence: 0.95,
        detectedLanguage: fromLanguage,
      }
    } catch (error) {
      console.error("Translation error:", error)
      return {
        translatedText: text,
        confidence: 0.0,
        detectedLanguage: fromLanguage,
      }
    }
  }

  private static async performTranslation(text: string, from: string, to: string): Promise<string> {
    // Mock translation - in production, use actual translation service
    const translations: Record<string, Record<string, string>> = {
      en: {
        hi: "आपका भुगतान देय है। कृपया जल्दी भुगतान करें।",
        mr: "तुमचे पेमेंट ड्यू आहे. कृपया लवकर पेमेंट करा.",
        ta: "உங்கள் கட்டணம் நிலுவையில் உள்ளது. தயவுசெய்து விரைவில் செலுத்துங்கள்.",
        te: "మీ చెల్లింపు బకాయి ఉంది. దయచేసి త్వరగా చెల్లించండి.",
        "en-IN": "Aapka payment due hai. Please jaldi payment kar dijiye.",
      },
    }

    return translations[from]?.[to] || text
  }

  static getLanguageName(code: string): string {
    return this.SUPPORTED_LANGUAGES[code as keyof typeof this.SUPPORTED_LANGUAGES] || "Unknown"
  }

  static getSupportedLanguages(): Record<string, string> {
    return this.SUPPORTED_LANGUAGES
  }
}
