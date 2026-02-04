import './InfoPage.css'

function InfoPage() {
  const headers = {
    'Request Headers': [
      { name: 'Authorization', desc: 'Credentials for authenticating the request (e.g., Bearer token, Basic auth)' },
      { name: 'Content-Type', desc: 'The media type of the request body (e.g., application/json)' },
      { name: 'Content-Length', desc: 'The size of the request body in bytes' },
      { name: 'User-Agent', desc: 'Information about the client making the request' },
      { name: 'Accept', desc: 'The media types the client can accept (e.g., application/json)' },
      { name: 'Accept-Language', desc: 'Preferred languages for the response' },
      { name: 'Accept-Encoding', desc: 'Compression methods the client can handle' },
      { name: 'Cache-Control', desc: 'Directives for caching the request' },
      { name: 'Connection', desc: 'Whether to keep the connection open (keep-alive) or close it' },
    ],
    'Response Headers': [
      { name: 'Date', desc: 'The date and time the response was generated' },
      { name: 'Content-Type', desc: 'The media type of the response body (e.g., application/json, text/html)' },
      { name: 'Content-Length', desc: 'The size of the response body in bytes' },
      { name: 'Content-Encoding', desc: 'The compression method used (e.g., gzip, deflate)' },
      { name: 'Transfer-Encoding', desc: 'How the response body is transmitted (e.g., chunked)' },
      { name: 'Server', desc: 'Information about the server software' },
      { name: 'Cache-Control', desc: 'Directives for caching the response (max-age, no-cache, etc.)' },
      { name: 'ETag', desc: 'A unique identifier for a specific version of the resource' },
      { name: 'Last-Modified', desc: 'The date the resource was last changed' },
      { name: 'Location', desc: 'The URL to redirect to (used in 3xx responses)' },
      { name: 'Set-Cookie', desc: 'Instructs the browser to store a cookie' },
      { name: 'Vary', desc: 'Indicates which request headers affect caching' },
      { name: 'Access-Control-Allow-Origin', desc: 'Specifies which origins can access this resource' },
      { name: 'X-Powered-By', desc: 'Technology used to generate the response' },
    ],
  }

  const statusCodes = {
    '2xx Success': [
      { code: '200 OK', desc: 'Request succeeded. Response body contains the result.' },
      { code: '201 Created', desc: 'Request succeeded and a new resource was created.' },
      { code: '204 No Content', desc: 'Request succeeded but there is no content to return.' },
    ],
    '3xx Redirection': [
      { code: '301 Moved Permanently', desc: 'Resource moved to a new URL permanently.' },
      { code: '302 Found', desc: 'Resource temporarily at a different URL.' },
      { code: '304 Not Modified', desc: 'Resource not modified since the last request.' },
    ],
    '4xx Client Error': [
      { code: '400 Bad Request', desc: 'Request is invalid or malformed.' },
      { code: '401 Unauthorized', desc: 'Authentication is required or failed.' },
      { code: '403 Forbidden', desc: 'Server refuses to fulfill the request (permission denied).' },
      { code: '404 Not Found', desc: 'The requested resource was not found.' },
      { code: '429 Too Many Requests', desc: 'Rate limit exceeded. Too many requests in a short time.' },
    ],
    '5xx Server Error': [
      { code: '500 Internal Server Error', desc: 'Server encountered an error processing the request.' },
      { code: '502 Bad Gateway', desc: 'Server received invalid response from upstream server.' },
      { code: '503 Service Unavailable', desc: 'Server is temporarily unavailable (maintenance, etc.).' },
    ],
  }

  const httpMethods = [
    { method: 'GET', desc: 'Retrieve data from the server. Does not modify data.' },
    { method: 'POST', desc: 'Submit data to create a new resource on the server.' },
    { method: 'PUT', desc: 'Replace an entire resource on the server.' },
    { method: 'PATCH', desc: 'Partially update a resource on the server.' },
    { method: 'DELETE', desc: 'Delete a resource from the server.' },
    { method: 'HEAD', desc: 'Like GET, but only returns headers (no body).' },
  ]

  return (
    <div className="info-page">
      <div className="info-container">
        <h1>API Reference Guide</h1>
        <p className="intro">Learn about HTTP headers, status codes, methods, and how to use this API testing tool.</p>

        {/* HTTP Methods */}
        <section className="info-section">
          <h2>HTTP Methods</h2>
          <p className="section-desc">The method specifies what action to perform on the resource.</p>
          <div className="info-grid">
            {httpMethods.map((item, idx) => (
              <div key={idx} className="info-card">
                <h3>{item.method}</h3>
                <p>{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Status Codes */}
        <section className="info-section">
          <h2>HTTP Status Codes</h2>
          <p className="section-desc">The status code indicates the result of the request.</p>
          {Object.entries(statusCodes).map(([category, codes]) => (
            <div key={category} className="info-subsection">
              <h3>{category}</h3>
              <div className="info-grid">
                {codes.map((item, idx) => (
                  <div key={idx} className="info-card">
                    <h4>{item.code}</h4>
                    <p>{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>

        {/* Headers */}
        <section className="info-section">
          <h2>HTTP Headers</h2>
          <p className="section-desc">Headers provide metadata about the request or response.</p>
          {Object.entries(headers).map(([category, headerList]) => (
            <div key={category} className="info-subsection">
              <h3>{category}</h3>
              <div className="headers-list">
                {headerList.map((item, idx) => (
                  <div key={idx} className="header-item">
                    <h4>{item.name}</h4>
                    <p>{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>

        {/* Tips */}
        <section className="info-section tips">
          <h2>Tips for Testing APIs</h2>
          <ul>
            <li>Always verify the correct HTTP method for the operation you want to perform</li>
            <li>Check the API documentation for required headers (e.g., Authorization)</li>
            <li>Use JSON format for request bodies unless the API specifies otherwise</li>
            <li>Review response headers to understand caching, content type, and other metadata</li>
            <li>Save frequently used requests for quick access later</li>
            <li>Pay attention to status codes - they indicate success or the type of error</li>
            <li>Use query parameters for filtering or pagination</li>
            <li>Validate JSON in headers, body, and query params before sending</li>
          </ul>
        </section>
      </div>
    </div>
  )
}

export default InfoPage
