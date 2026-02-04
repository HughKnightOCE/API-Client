import { useState, useEffect } from 'react'
import axios from 'axios'
import RequestBuilder from './components/RequestBuilder'
import ResponseViewer from './components/ResponseViewer'
import Sidebar from './components/Sidebar'
import EnvironmentManager from './components/EnvironmentManager'
import AssertionBuilder from './components/AssertionBuilder'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [savedRequests, setSavedRequests] = useState([])
  const [history, setHistory] = useState([])
  const [environments, setEnvironments] = useState({})
  const [selectedEnvironment, setSelectedEnvironment] = useState(null)
  const [assertions, setAssertions] = useState([])
  const [currentRequest, setCurrentRequest] = useState({
    method: 'GET',
    url: '',
    headers: '{}',
    body: '',
    params: '{}',
    environment: null,
  })

  // Load saved requests on mount
  useEffect(() => {
    loadSavedRequests()
    loadHistory()
    loadEnvironments()
  }, [])

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.style.background = '#1e1e1e'
      document.body.classList.add('dark-mode')
    } else {
      document.documentElement.style.background = '#f5f5f5'
      document.body.classList.remove('dark-mode')
    }
  }, [darkMode])

  const loadSavedRequests = async () => {
    try {
      const res = await axios.get('/api/requests')
      setSavedRequests(res.data.requests)
    } catch (error) {
      console.error('Failed to load requests:', error)
    }
  }

  const loadHistory = async () => {
    try {
      const res = await axios.get('/api/history')
      setHistory(res.data.history)
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const loadEnvironments = async () => {
    try {
      const res = await axios.get('/api/environments')
      setEnvironments(res.data.environments)
    } catch (error) {
      console.error('Failed to load environments:', error)
    }
  }

  const makeRequest = async (request) => {
    setLoading(true)
    try {
      const res = await axios.post('/api/request/enhanced', {
        method: request.method,
        url: request.url,
        headers: request.headers ? JSON.parse(request.headers) : {},
        body: request.body,
        params: request.params ? JSON.parse(request.params) : {},
        environment: selectedEnvironment,
        assertions: assertions,
      })
      setResponse(res.data)
      loadHistory()
    } catch (error) {
      setResponse({
        success: false,
        error: error.message,
        status_code: error.response?.status,
      })
    }
    setLoading(false)
  }

  const saveRequest = async (name) => {
    try {
      await axios.post('/api/save', {
        name,
        method: currentRequest.method,
        url: currentRequest.url,
        headers: currentRequest.headers ? JSON.parse(currentRequest.headers) : {},
        body: currentRequest.body,
        params: currentRequest.params ? JSON.parse(currentRequest.params) : {},
        environment: selectedEnvironment,
        assertions: assertions,
      })
      loadSavedRequests()
      alert(`Request saved as "${name}"`)
    } catch (error) {
      alert('Failed to save request')
    }
  }

  const deleteRequest = async (name) => {
    try {
      await axios.delete(`/api/requests/${name}`)
      loadSavedRequests()
    } catch (error) {
      alert('Failed to delete request')
    }
  }

  const loadRequest = (req) => {
    setCurrentRequest({
      method: req.method,
      url: req.url,
      headers: JSON.stringify(req.headers, null, 2),
      body: req.body || '',
      params: JSON.stringify(req.params, null, 2),
    })
    if (req.environment) {
      setSelectedEnvironment(req.environment)
    }
    if (req.assertions) {
      setAssertions(req.assertions)
    }
  }

  const handleAddEnvironment = async (name, variables) => {
    try {
      await axios.post('/api/environments', { name, variables })
      loadEnvironments()
    } catch (error) {
      console.error('Failed to add environment:', error)
    }
  }

  const handleDeleteEnvironment = async (name) => {
    try {
      await axios.delete(`/api/environments/${name}`)
      if (selectedEnvironment === name) {
        setSelectedEnvironment(null)
      }
      loadEnvironments()
    } catch (error) {
      console.error('Failed to delete environment:', error)
    }
  }

  const handleAddAssertion = (assertion) => {
    setAssertions([...assertions, assertion])
  }

  const handleRemoveAssertion = (index) => {
    setAssertions(assertions.filter((_, i) => i !== index))
  }

  return (
    <div className="app">
      <Sidebar
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        savedRequests={savedRequests}
        history={history}
        onLoadRequest={loadRequest}
        onDeleteRequest={deleteRequest}
      />

      <div className="main-content">
        <div className="builder-section">
          <div className="builder-tabs">
            <div className="environment-section">
              <EnvironmentManager
                environments={environments}
                selectedEnvironment={selectedEnvironment}
                onAddEnvironment={handleAddEnvironment}
                onDeleteEnvironment={handleDeleteEnvironment}
                onSelectEnvironment={setSelectedEnvironment}
              />
            </div>
            <RequestBuilder
              request={currentRequest}
              setRequest={setCurrentRequest}
              onMakeRequest={makeRequest}
              onSaveRequest={saveRequest}
              loading={loading}
              environments={environments}
              selectedEnvironment={selectedEnvironment}
              onSelectEnvironment={setSelectedEnvironment}
            />
            <div className="assertion-section">
              <AssertionBuilder
                assertions={assertions}
                onAddAssertion={handleAddAssertion}
                onRemoveAssertion={handleRemoveAssertion}
              />
            </div>
          </div>
        </div>

        <div className="response-section">
          <ResponseViewer response={response} loading={loading} assertions={assertions} />
        </div>
      </div>
    </div>
  )
}

export default App
