import './ResponseViewer.css'

// Common HTTP header explanations
const HEADER_EXPLANATIONS = {
  'date': 'The date and time the response was generated',
  'content-type': 'The media type of the response body (e.g., JSON, HTML, plain text)',
  'content-length': 'The size of the response body in bytes',
  'content-encoding': 'The compression method used (e.g., gzip, deflate)',
  'transfer-encoding': 'How the response body is transmitted (e.g., chunked)',
  'connection': 'Whether the connection stays open or closes after the response',
  'server': 'Information about the server software',
  'cache-control': 'Directives for caching the response',
  'etag': 'A unique identifier for a specific version of the resource',
  'expires': 'When the response should no longer be cached',
  'last-modified': 'The date the resource was last changed',
  'location': 'The URL to redirect to (used in 3xx responses)',
  'set-cookie': 'Instructs the browser to store a cookie',
  'vary': 'Indicates which request headers affect caching',
  'access-control-allow-origin': 'Specifies which origins can access this resource',
  'authorization': 'Credentials for authenticating the request',
  'x-powered-by': 'Technology used to generate the response',
}

function ResponseViewer({ response, loading, assertions }) {
  const formatJson = (obj) => {
    return JSON.stringify(obj, null, 2)
  }

  const getStatusColor = (status) => {
    if (status >= 200 && status < 300) return 'status-success'
    if (status >= 300 && status < 400) return 'status-redirect'
    if (status >= 400 && status < 500) return 'status-client-error'
    return 'status-server-error'
  }

  const getHeaderExplanation = (headerName) => {
    const lowerName = headerName.toLowerCase()
    return HEADER_EXPLANATIONS[lowerName] || 'Custom header'
  }

  if (loading) {
    return (
      <div className="response-viewer">
        <div className="loading">
          <div className="spinner"></div>
          <p>Sending request...</p>
        </div>
      </div>
    )
  }

  if (!response) {
    return (
      <div className="response-viewer empty">
        <p>Response will appear here</p>
      </div>
    )
  }

  if (!response.success) {
    return (
      <div className="response-viewer error">
        <h3>Error</h3>
        <div className="error-message">{response.error}</div>
        {response.status_code && <p className="status-code">Status: {response.status_code}</p>}
      </div>
    )
  }

  return (
    <div className="response-viewer">
      <h2>Response</h2>

      <div className={`status-bar ${getStatusColor(response.status_code)}`}>
        <span className="status-code">Status: {response.status_code}</span>
      </div>

      {response.headers && Object.keys(response.headers).length > 0 && (
        <div className="headers-section">
          <h3>Headers</h3>
          <div className="headers-table">
            {Object.entries(response.headers).map(([key, value]) => (
              <div key={key} className="header-row header-with-tooltip">
                <div className="header-key-wrapper">
                  <div className="header-key">{key}</div>
                  <span className="header-tooltip-icon">?</span>
                  <span className="header-tooltip-text">{getHeaderExplanation(key)}</span>
                </div>
                <div className="header-value">{String(value).substring(0, 100)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {response.assertions && (
        <div className={`assertions-section ${response.assertions.passed ? 'passed' : 'failed'}`}>
          <h3>Assertions ({response.assertions.count})</h3>
          <div className={`assertion-result ${response.assertions.passed ? 'success' : 'error'}`}>
            {response.assertions.passed ? '✓ All assertions passed' : '✗ Some assertions failed'}
          </div>
          {response.assertions.errors && response.assertions.errors.length > 0 && (
            <div className="assertion-errors">
              {response.assertions.errors.map((error, idx) => (
                <div key={idx} className="assertion-error-item">
                  <span className="error-icon">⚠</span>
                  {error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {response.body && (
        <div className="body-section">
          <h3>Body</h3>
          <pre className="body-content">
            {typeof response.body === 'string'
              ? response.body
              : formatJson(response.body)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default ResponseViewer
