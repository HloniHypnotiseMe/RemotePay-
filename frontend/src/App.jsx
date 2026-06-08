import { useState, useEffect } from 'react'
import toast, { Toaster } from 'react-hot-toast'

function App() {
  const [health, setHealth] = useState(null)
  const [assistantName, setAssistantName] = useState('')
  const [assistantConfigured, setAssistantConfigured] = useState(false)
  const [assistantId, setAssistantId] = useState(null)
  const [loading, setLoading] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Backend not running:', err))
  }, [])

  const configureAssistant = async () => {
    if (!assistantName.trim()) {
      toast.error('Please enter a name for your assistant')
      return
    }
    
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/assistant/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: assistantName,
          personality: 'friendly'
        })
      })
      const data = await res.json()
      setAssistantId(data.id)
      setAssistantConfigured(true)
      toast.success(`✅ ${assistantName} is now your AI assistant!`)
    } catch (err) {
      toast.error('Failed to configure assistant')
    } finally {
      setLoading(false)
    }
  }

  const createPayment = async () => {
    // First create a customer
    const customerRes = await fetch(`${API_URL}/api/v1/customers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'test@example.com', name: 'Test Customer' })
    })
    const customer = await customerRes.json()

    // Create payment
    const paymentRes = await fetch(`${API_URL}/api/v1/payments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: 1000,
        currency: 'ZAR',
        customer_id: customer.id,
        return_url: 'https://www.remote-pay.co.za/success',
        cancel_url: 'https://www.remote-pay.co.za/cancel',
        item_name: 'RemotePay Pro Plan'
      })
    })
    const payment = await paymentRes.json()

    // Create and submit form to PayFast
    const form = document.createElement('form')
    form.method = 'POST'
    form.action = payment.checkout_url
    form.target = '_blank'

    for (const [key, value] of Object.entries(payment.form_data)) {
      const input = document.createElement('input')
      input.type = 'hidden'
      input.name = key
      input.value = value
      form.appendChild(input)
    }

    document.body.appendChild(form)
    form.submit()
    document.body.removeChild(form)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-600">RemotePay</h1>
            {health && (
              <div className="text-sm text-gray-500">
                {health.payfast_mode === 'sandbox' ? '🔬 Sandbox' : '🚀 Live'} | v{health.version}
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Connection Status */}
        {health && (
          <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg mb-6">
            ✅ Backend Connected | PayFast: {health.payfast_mode}
          </div>
        )}

        {/* Named Assistant Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">🤖 Name Your Online Business Assistant</h2>
          {!assistantConfigured ? (
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="e.g., Sophia, ProfitBot, DealCloser"
                value={assistantName}
                onChange={(e) => setAssistantName(e.target.value)}
                className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={configureAssistant}
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Assistant'}
              </button>
            </div>
          ) : (
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <p className="text-primary-800">
                ✅ Your assistant <strong>{assistantName}</strong> is ready to help you close deals!
              </p>
            </div>
          )}
        </div>

        {/* Payment Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">💳 Test Payment</h2>
          <button
            onClick={createPayment}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
          >
            Pay R100 with PayFast
          </button>
          <p className="text-sm text-gray-500 mt-3">
            Test card: 4111 1111 1111 1111 | Any expiry, any CVV
          </p>
        </div>

        {/* Pricing Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">💰 Pricing Plans</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-bold">Free</h3>
              <p className="text-2xl font-bold mt-2">R0<span className="text-sm font-normal text-gray-500">/month</span></p>
              <p className="text-gray-600 mt-2">2.5% + R0.30 per transaction</p>
            </div>
            <div className="border-2 border-primary-500 rounded-lg p-4 bg-primary-50">
              <h3 className="text-lg font-bold text-primary-700">Pro 🔥</h3>
              <p className="text-2xl font-bold mt-2">R299<span className="text-sm font-normal text-gray-500">/month</span></p>
              <p className="text-gray-600 mt-2">0% transaction fee</p>
              <p className="text-sm text-primary-600 mt-2">✓ Named AI Assistant included</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
