export interface Borrower {
  id: string
  accountNumber: string
  name: string
  phone: string
  email?: string
  address?: string
  preferredLanguage: string
  createdAt: Date
  updatedAt: Date
}

export interface DebtAccount {
  id: string
  borrowerId: string
  accountNumber: string
  originalAmount: number
  outstandingAmount: number
  dueDate: Date
  status: "active" | "overdue" | "settled" | "legal" | "written_off"
  interestRate?: number
  createdAt: Date
  updatedAt: Date
}

export interface Campaign {
  id: string
  name: string
  description?: string
  type: "payment_reminder" | "emi_offer" | "settlement" | "final_notice"
  status: "draft" | "active" | "paused" | "completed"
  targetLanguage?: string
  templateId?: string
  scheduledAt?: Date
  createdBy?: string
  createdAt: Date
  updatedAt: Date
}

export interface ChatSession {
  id: string
  borrowerId: string
  campaignId?: string
  sessionToken: string
  platform: "web" | "whatsapp" | "sms"
  language: string
  status: "active" | "closed" | "transferred"
  metadata: Record<string, any>
  startedAt: Date
  endedAt?: Date
  createdAt: Date
}

export interface ConversationMessage {
  id: string
  sessionId: string
  senderType: "user" | "bot" | "agent"
  messageType: "text" | "image" | "document" | "audio" | "video"
  content: string
  originalLanguage?: string
  translatedContent?: string
  metadata: Record<string, any>
  sentAt: Date
  deliveredAt?: Date
  readAt?: Date
}

export interface MessageTemplate {
  id: string
  name: string
  language: string
  type: string
  content: string
  variables: string[]
  isApproved: boolean
  whatsappTemplateId?: string
  createdAt: Date
  updatedAt: Date
}

export interface CampaignRecipient {
  id: string
  campaignId: string
  borrowerId: string
  debtAccountId: string
  status: "pending" | "sent" | "delivered" | "read" | "replied" | "failed"
  sentAt?: Date
  deliveredAt?: Date
  readAt?: Date
  repliedAt?: Date
  uniqueLink?: string
  metadata: Record<string, any>
  createdAt: Date
}

export interface PaymentTransaction {
  id: string
  debtAccountId: string
  sessionId?: string
  amount: number
  transactionType: "payment" | "settlement" | "adjustment"
  paymentMethod?: string
  transactionId?: string
  status: "pending" | "completed" | "failed" | "refunded"
  processedAt?: Date
  metadata: Record<string, any>
  createdAt: Date
}

export interface AnalyticsEvent {
  id: string
  eventType: string
  sessionId?: string
  borrowerId?: string
  campaignId?: string
  properties: Record<string, any>
  timestamp: Date
}

export interface LanguagePreference {
  id: string
  borrowerId: string
  languageCode: string
  confidenceScore: number
  detectedFrom: "manual" | "auto_detect" | "conversation"
  lastUsedAt: Date
  createdAt: Date
}

export interface AIResponse {
  content: string
  language: string
  intent: string
  entities: Record<string, any>
  confidence: number
  suggestedActions?: string[]
}

export interface TranslationRequest {
  text: string
  fromLanguage: string
  toLanguage: string
}

export interface TranslationResponse {
  translatedText: string
  confidence: number
  detectedLanguage?: string
}
