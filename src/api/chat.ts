import type { Request, Response } from "express"
import { supabase } from "../config/database"
import { AIService } from "../services/aiService"

export class ChatController {
  static async handleChatMessage(req: Request, res: Response): Promise<void> {
    try {
      const { sessionToken, message, language } = req.body

      // Get chat session
      const { data: session, error: sessionError } = await supabase
        .from("chat_sessions")
        .select(`
          *,
          borrowers(*),
          debt_accounts(*)
        `)
        .eq("session_token", sessionToken)
        .single()

      if (sessionError || !session) {
        res.status(404).json({
          success: false,
          error: "Chat session not found",
        })
        return
      }

      // Save user message
      await supabase.from("conversation_messages").insert([
        {
          session_id: session.id,
          sender_type: "user",
          content: message,
          original_language: language || "auto",
        },
      ])

      // Get conversation history
      const { data: history } = await supabase
        .from("conversation_messages")
        .select("content, sender_type")
        .eq("session_id", session.id)
        .order("sent_at", { ascending: true })
        .limit(20)

      const conversationHistory = history?.map((msg) => `${msg.sender_type}: ${msg.content}`) || []

      // Generate AI response
      const aiResponse = await AIService.generateResponse(
        message,
        session.borrowers,
        session.debt_accounts,
        conversationHistory,
      )

      // Save bot response
      await supabase.from("conversation_messages").insert([
        {
          session_id: session.id,
          sender_type: "bot",
          content: aiResponse.content,
          original_language: aiResponse.language,
          metadata: {
            intent: aiResponse.intent,
            entities: aiResponse.entities,
            confidence: aiResponse.confidence,
          },
        },
      ])

      // Log analytics event
      await supabase.from("analytics_events").insert([
        {
          event_type: "message_sent",
          session_id: session.id,
          borrower_id: session.borrower_id,
          properties: {
            intent: aiResponse.intent,
            language: aiResponse.language,
            platform: session.platform,
          },
        },
      ])

      res.json({
        success: true,
        data: {
          response: aiResponse.content,
          language: aiResponse.language,
          suggestedActions: aiResponse.suggestedActions,
        },
      })
    } catch (error) {
      console.error("Chat message error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to process chat message",
      })
    }
  }

  static async createChatSession(req: Request, res: Response): Promise<void> {
    try {
      const { uniqueLink } = req.params

      // Find campaign recipient by unique link
      const { data: recipient, error: recipientError } = await supabase
        .from("campaign_recipients")
        .select(`
          *,
          borrowers(*),
          debt_accounts(*),
          campaigns(*)
        `)
        .eq("unique_link", uniqueLink)
        .single()

      if (recipientError || !recipient) {
        res.status(404).json({
          success: false,
          error: "Invalid or expired link",
        })
        return
      }

      // Create chat session
      const sessionToken = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

      const { data: session, error: sessionError } = await supabase
        .from("chat_sessions")
        .insert([
          {
            borrower_id: recipient.borrower_id,
            campaign_id: recipient.campaign_id,
            session_token: sessionToken,
            platform: "web",
            language: recipient.borrowers.preferred_language || "en",
            metadata: {
              unique_link: uniqueLink,
              debt_account_id: recipient.debt_account_id,
            },
          },
        ])
        .select()
        .single()

      if (sessionError) throw sessionError

      // Update recipient status
      await supabase
        .from("campaign_recipients")
        .update({
          status: "read",
          read_at: new Date().toISOString(),
        })
        .eq("id", recipient.id)

      res.json({
        success: true,
        data: {
          sessionToken,
          borrower: recipient.borrowers,
          debtAccount: recipient.debt_accounts,
          campaign: recipient.campaigns,
        },
      })
    } catch (error) {
      console.error("Create chat session error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to create chat session",
      })
    }
  }

  static async getChatHistory(req: Request, res: Response): Promise<void> {
    try {
      const { sessionToken } = req.params
      const { limit = 50, offset = 0 } = req.query

      const { data: messages, error } = await supabase
        .from("conversation_messages")
        .select(`
          *,
          chat_sessions!inner(session_token)
        `)
        .eq("chat_sessions.session_token", sessionToken)
        .order("sent_at", { ascending: true })
        .range(Number(offset), Number(offset) + Number(limit) - 1)

      if (error) throw error

      res.json({
        success: true,
        data: messages,
      })
    } catch (error) {
      console.error("Get chat history error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to fetch chat history",
      })
    }
  }
}
