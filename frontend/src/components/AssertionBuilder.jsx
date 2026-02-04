import { useState } from 'react'
import './AssertionBuilder.css'

const OPERATORS = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Not Contains' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
  { value: 'greater_than_or_equal', label: '≥' },
  { value: 'less_than_or_equal', label: '≤' },
  { value: 'exists', label: 'Exists' },
  { value: 'not_exists', label: 'Not Exists' },
  { value: 'is_type', label: 'Is Type' },
]

const TYPE_VALUES = ['string', 'number', 'boolean', 'array', 'object', 'null']

function AssertionBuilder({ assertions, onAddAssertion, onRemoveAssertion }) {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ field: '', operator: 'equals', expected: '' })

  const handleAddAssertion = () => {
    if (formData.field && formData.operator) {
      onAddAssertion({
        field: formData.field,
        operator: formData.operator,
        expected: formData.expected,
      })
      setFormData({ field: '', operator: 'equals', expected: '' })
      setShowForm(false)
    }
  }

  const isTypeOperator = formData.operator === 'is_type'
  const existsOperator = formData.operator === 'exists' || formData.operator === 'not_exists'

  return (
    <div className="assertion-builder">
      <div className="assertion-header">
        <h3>✓ Response Validation</h3>
        <button className="btn-add-assertion" onClick={() => setShowForm(!showForm)}>
          + Add Assertion
        </button>
      </div>

      {showForm && (
        <div className="assertion-form">
          <div className="form-row">
            <div className="form-col">
              <label>Field to Test</label>
              <input
                type="text"
                placeholder="e.g., status, response.data.id"
                value={formData.field}
                onChange={(e) => setFormData({ ...formData, field: e.target.value })}
              />
              <small>Use dot notation for nested fields or 'status'</small>
            </div>
          </div>

          <div className="form-row">
            <div className="form-col">
              <label>Operator</label>
              <select
                value={formData.operator}
                onChange={(e) => setFormData({ ...formData, operator: e.target.value })}
              >
                {OPERATORS.map((op) => (
                  <option key={op.value} value={op.value}>
                    {op.label}
                  </option>
                ))}
              </select>
            </div>

            {!existsOperator && (
              <div className="form-col">
                <label>Expected Value</label>
                {isTypeOperator ? (
                  <select
                    value={formData.expected}
                    onChange={(e) => setFormData({ ...formData, expected: e.target.value })}
                  >
                    <option value="">Select type...</option>
                    {TYPE_VALUES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="text"
                    placeholder="e.g., 200, 'success', 1000"
                    value={formData.expected}
                    onChange={(e) => setFormData({ ...formData, expected: e.target.value })}
                  />
                )}
              </div>
            )}
          </div>

          <div className="form-actions">
            <button className="btn-save" onClick={handleAddAssertion}>
              Add Assertion
            </button>
            <button className="btn-cancel" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="assertions-list">
        {assertions.length === 0 ? (
          <p className="empty-message">No assertions added yet</p>
        ) : (
          assertions.map((assertion, idx) => (
            <div key={idx} className="assertion-item">
              <div className="assertion-content">
                <span className="field">{assertion.field}</span>
                <span className="operator">{assertion.operator}</span>
                {assertion.expected && <span className="expected">{assertion.expected}</span>}
              </div>
              <button
                className="btn-remove"
                onClick={() => onRemoveAssertion(idx)}
                title="Remove assertion"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AssertionBuilder
