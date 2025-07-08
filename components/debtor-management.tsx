"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, MessageSquare, Phone, Calendar, IndianRupee } from "lucide-react"

interface Debtor {
  id: string
  name: string
  phone: string
  amount: number
  dueDate: string
  status: "active" | "overdue" | "settled" | "legal"
  language: string
  lastContact: string
  responseRate: number
}

export default function DebtorManagement() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [languageFilter, setLanguageFilter] = useState("all")

  const debtors: Debtor[] = [
    {
      id: "AC123456789",
      name: "Rajesh Kumar",
      phone: "+91 98765 43210",
      amount: 25000,
      dueDate: "2024-01-15",
      status: "overdue",
      language: "Hindi",
      lastContact: "2024-01-10",
      responseRate: 75,
    },
    {
      id: "AC987654321",
      name: "Priya Sharma",
      phone: "+91 87654 32109",
      amount: 18500,
      dueDate: "2024-01-20",
      status: "active",
      language: "English",
      lastContact: "2024-01-12",
      responseRate: 90,
    },
    {
      id: "AC456789123",
      name: "Arjun Patel",
      phone: "+91 76543 21098",
      amount: 32000,
      dueDate: "2024-01-08",
      status: "legal",
      language: "Gujarati",
      lastContact: "2024-01-05",
      responseRate: 45,
    },
    {
      id: "AC321654987",
      name: "Meera Reddy",
      phone: "+91 65432 10987",
      amount: 15000,
      dueDate: "2024-01-25",
      status: "active",
      language: "Telugu",
      lastContact: "2024-01-13",
      responseRate: 85,
    },
    {
      id: "AC789123456",
      name: "Suresh Yadav",
      phone: "+91 54321 09876",
      amount: 42000,
      dueDate: "2024-01-12",
      status: "overdue",
      language: "Marathi",
      lastContact: "2024-01-08",
      responseRate: 60,
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "overdue":
        return "bg-red-100 text-red-800"
      case "settled":
        return "bg-blue-100 text-blue-800"
      case "legal":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const filteredDebtors = debtors.filter((debtor) => {
    const matchesSearch =
      debtor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      debtor.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || debtor.status === statusFilter
    const matchesLanguage = languageFilter === "all" || debtor.language === languageFilter

    return matchesSearch && matchesStatus && matchesLanguage
  })

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Debtor Management</CardTitle>
          <CardDescription>Manage and track all debt collection cases</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name or account number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
                <SelectItem value="settled">Settled</SelectItem>
                <SelectItem value="legal">Legal</SelectItem>
              </SelectContent>
            </Select>
            <Select value={languageFilter} onValueChange={setLanguageFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Languages</SelectItem>
                <SelectItem value="Hindi">Hindi</SelectItem>
                <SelectItem value="English">English</SelectItem>
                <SelectItem value="Marathi">Marathi</SelectItem>
                <SelectItem value="Tamil">Tamil</SelectItem>
                <SelectItem value="Telugu">Telugu</SelectItem>
                <SelectItem value="Gujarati">Gujarati</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Debtors Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Debtor Details</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Language</TableHead>
                <TableHead>Response Rate</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDebtors.map((debtor) => (
                <TableRow key={debtor.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{debtor.name}</div>
                      <div className="text-sm text-gray-500">{debtor.id}</div>
                      <div className="text-sm text-gray-500">{debtor.phone}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <IndianRupee className="h-4 w-4 mr-1" />
                      {debtor.amount.toLocaleString("en-IN")}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{new Date(debtor.dueDate).toLocaleDateString("en-IN")}</div>
                    <div className="text-xs text-gray-500">
                      Last contact: {new Date(debtor.lastContact).toLocaleDateString("en-IN")}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(debtor.status)}>
                      {debtor.status.charAt(0).toUpperCase() + debtor.status.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{debtor.language}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${debtor.responseRate}%` }}
                        ></div>
                      </div>
                      <span className="text-sm">{debtor.responseRate}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline">
                        <MessageSquare className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Phone className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Calendar className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-red-600">
              {filteredDebtors.filter((d) => d.status === "overdue").length}
            </div>
            <div className="text-sm text-gray-600">Overdue Cases</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {filteredDebtors.filter((d) => d.status === "active").length}
            </div>
            <div className="text-sm text-gray-600">Active Cases</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">
              ₹{filteredDebtors.reduce((sum, d) => sum + d.amount, 0).toLocaleString("en-IN")}
            </div>
            <div className="text-sm text-gray-600">Total Outstanding</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {Math.round(filteredDebtors.reduce((sum, d) => sum + d.responseRate, 0) / filteredDebtors.length)}%
            </div>
            <div className="text-sm text-gray-600">Avg Response Rate</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
