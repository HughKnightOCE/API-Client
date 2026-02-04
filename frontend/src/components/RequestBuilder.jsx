import { useState } from 'react'
import './RequestBuilder.css'

function RequestBuilder({ request, setRequest, onMakeRequest, onSaveRequest, loading }) {
  const [saveName, setSaveName] = useState('')

  const handleMethodChange = (e) => {
    setRequest({ ...request, method: e.target.value })
  }

  const handleUrlChange = (e) => {
    setRequest({ ...request, url: e.target.value })
  }

  const handleHeadersChange = (e) => {
    setRequest({ ...request, headers: e.target.value })
  }

  const handleBodyChange = (e) => {
    setRequest({ ...request, body: e.target.value })
  }

  const handleParamsChange = (e) => {
    setRequest({ ...request, params: e.target.value })
  }

  const handleMakeRequest = () => {
    if (!request.url) {
      alert('Please enter a URL')
      return
    }
    onMakeRequest(request)
  }

  const handleSaveRequest = () => {
    if (!saveName) {
      alert('Please enter a name for the request')
      return
    }
    onSaveRequest(saveName)
    setSaveName('')
  }

  return (
    <div className="request-builder">
      <h2>Request Builder</h2>

      <div className="form-group">
        <label className="label-with-tooltip">
          Method
          <span className="tooltip-icon">?</span>
          <span className="tooltip-text">Select the HTTP request method (GET retrieves data, POST creates, PUT updates, etc.)</span>
        </label>
        <select value={request.method} onChange={handleMethodChange}>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="PATCH">PATCH</option>
          <option value="DELETE">DELETE</option>
          <option value="HEAD">HEAD</option>
        </select>
      </div>

      <div className="form-group">
        <label className="label-with-tooltip">
          URL
          <span className="tooltip-icon">?</span>
          <span className="tooltip-text">Enter the complete API endpoint URL (e.g., https://api.example.com/users/1)</span>
        </label>
        <input
          type="text"
          value={request.url}
          onChange={handleUrlChange}
          placeholder="https://api.example.com/endpoint"
        />
      </div>

      <div className="form-row">
        <div className="form-group flex-1">
          <label className="label-with-tooltip">
            Headers (JSON)
            <span className="tooltip-icon">?</span>
            <span className="tooltip-text">Optional HTTP headers. Example: {"{"}Authorization{":"} "Bearer token"{}"}</span>
          </label>
          <textarea
            value={request.headers}
            onChange={handleHeadersChange}
            placeholder='{"Authorization": "Bearer token"}'
            rows="4"
          />
        </div>

        <div className="form-group flex-1">
          <label className="label-with-tooltip">
            Query Params (JSON)
            <span className="tooltip-icon">?</span>
            <span className="tooltip-text">URL query parameters appended to the endpoint. Example: {"{"}page{":"} "1", "limit"{":"} "10"{}"}</span>
          </label>
          <textarea
            value={request.params}
            onChange={handleParamsChange}
            placeholder='{"page": "1", "limit": "10"}'
            rows="4"
          />
        </div>
      </div>

      <div className="form-group">
        <label className="label-with-tooltip">
          Body (JSON)
          <span className="tooltip-icon">?</span>
          <span className="tooltip-text">Request body data for POST, PUT, or PATCH requests. Only used with these methods.</span>
        </label>
        <textarea
          value={request.body}
          onChange={handleBodyChange}
          placeholder='{"key": "value"}'
          rows="6"
        />
      </div>

      <div className="button-group">
        <button
          className="btn btn-primary"
          onClick={handleMakeRequest}
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send Request'}
        </button>

        <div className="save-group">
          <input
            type="text"
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            placeholder="Request name"
            onKeyPress={(e) => e.key === 'Enter' && handleSaveRequest()}
          />
          <button className="btn btn-secondary" onClick={handleSaveRequest}>
            Save Request
          </button>
        </div>
      </div>
    </div>
  )
}

export default RequestBuilder
