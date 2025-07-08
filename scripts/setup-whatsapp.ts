import { WhatsAppService } from "../src/services/whatsappService"
import { WhatsAppTemplateService } from "../src/services/whatsappTemplateService"

async function setupWhatsApp() {
  console.log("🚀 Setting up WhatsApp Business Integration...")

  try {
    // 1. Verify Business Account
    console.log("1. Verifying WhatsApp Business Account...")
    const isVerified = await WhatsAppService.verifyBusinessAccount()

    if (!isVerified) {
      console.error("❌ WhatsApp Business Account verification failed")
      process.exit(1)
    }
    console.log("✅ WhatsApp Business Account verified")

    // 2. Setup Message Templates
    console.log("2. Setting up message templates...")
    await WhatsAppTemplateService.setupDefaultTemplates()
    console.log("✅ Message templates created")

    // 3. Get existing templates
    console.log("3. Fetching existing templates...")
    const templates = await WhatsAppTemplateService.getApprovedTemplates()
    console.log(`✅ Found ${templates.length} approved templates`)

    // 4. Test message (optional - uncomment to test)
    // console.log("4. Sending test message...")
    // await WhatsAppService.sendMessage("917439330282", "WhatsApp integration test successful! 🎉")
    // console.log("✅ Test message sent")

    console.log("\n🎉 WhatsApp Business integration setup completed!")
    console.log("\nNext steps:")
    console.log("1. Configure webhook URL in Meta Developer Console:")
    console.log("   URL: https://your-domain.com/api/whatsapp/webhook")
    console.log("   Verify Token: debt_collection_webhook_verify_2024")
    console.log("2. Subscribe to webhook events: messages, message_deliveries, message_reads")
    console.log("3. Test the integration with a real message")
  } catch (error) {
    console.error("❌ WhatsApp setup failed:", error)
    process.exit(1)
  }
}

// Run setup
setupWhatsApp()
