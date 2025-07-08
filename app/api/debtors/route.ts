import { NextResponse } from "next/server"

// Mock database - in production, this would connect to your actual database
const debtors = [
  {
    id: "AC123456789",
    name: "Rajesh Kumar",
    phone: "+91 98765 43210",
    email: "rajesh.kumar@email.com",
    amount: 25000,
    originalAmount: 30000,
    dueDate: "2024-01-15",
    status: "overdue",
    language: "Hindi",
    lastContact: "2024-01-10",
    responseRate: 75,
    paymentHistory: [{ date: "2023-12-15", amount: 5000, type: "partial" }],
    notes: "Responsive to Hindi communication, prefers WhatsApp",
  },
  {
    id: "AC987654321",
    name: "Priya Sharma",
    phone: "+91 87654 32109",
    email: "priya.sharma@email.com",
    amount: 18500,
    originalAmount: 20000,
    dueDate: "2024-01-20",
    status: "active",
    language: "English",
    lastContact: "2024-01-12",
    responseRate: 90,
    paymentHistory: [{ date: "2023-11-20", amount: 1500, type: "partial" }],
    notes: "Professional, prefers email communication",
  },
]

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const status = searchParams.get("status")
  const language = searchParams.get("language")
  const search = searchParams.get("search")

  let filteredDebtors = debtors

  if (status && status !== "all") {
    filteredDebtors = filteredDebtors.filter((debtor) => debtor.status === status)
  }

  if (language && language !== "all") {
    filteredDebtors = filteredDebtors.filter((debtor) => debtor.language === language)
  }

  if (search) {
    filteredDebtors = filteredDebtors.filter(
      (debtor) =>
        debtor.name.toLowerCase().includes(search.toLowerCase()) ||
        debtor.id.toLowerCase().includes(search.toLowerCase()),
    )
  }

  return NextResponse.json(filteredDebtors)
}

export async function POST(request: Request) {
  const debtorData = await request.json()

  // In production, save to database
  const newDebtor = {
    id: `AC${Date.now()}`,
    ...debtorData,
    responseRate: 0,
    paymentHistory: [],
    lastContact: new Date().toISOString().split("T")[0],
  }

  return NextResponse.json(newDebtor, { status: 201 })
}
