import { useState } from 'react'
import './EnvironmentManager.css'

function EnvironmentManager({ environments, onAddEnvironment, onDeleteEnvironment, onSelectEnvironment, selectedEnvironment }) {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ name: '', variables: {} })
  const [currentVar, setCurrentVar] = useState({ key: '', value: '' })

  const handleAddVariable = () => {
    if (currentVar.key && currentVar.value) {
      setFormData({
        ...formData,
        variables: { ...formData.variables, [currentVar.key]: currentVar.value }
      })
      setCurrentVar({ key: '', value: '' })
    }
  }

  const handleRemoveVariable = (key) => {
    const newVars = { ...formData.variables }
    delete newVars[key]
    setFormData({ ...formData, variables: newVars })
  }

  const handleSaveEnvironment = () => {
    if (formData.name && Object.keys(formData.variables).length > 0) {
      onAddEnvironment(formData)
      setFormData({ name: '', variables: {} })
      setShowForm(false)
    }
  }

  return (
    <div className="environment-manager">
      <div className="env-header">
        <h3>🔐 Environments</h3>
        <button className="btn-add-env" onClick={() => setShowForm(!showForm)}>
          + New
        </button>
      </div>

      {showForm && (
        <div className="env-form">
          <input
            type="text"
            placeholder="Environment name (e.g., 'Production')"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />

          <div className="variables-section">
            <h4>Variables</h4>
            <div className="variable-input">
              <input
                type="text"
                placeholder="Key (e.g., API_KEY)"
                value={currentVar.key}
                onChange={(e) => setCurrentVar({ ...currentVar, key: e.target.value })}
              />
              <input
                type="text"
                placeholder="Value"
                value={currentVar.value}
                onChange={(e) => setCurrentVar({ ...currentVar, value: e.target.value })}
              />
              <button onClick={handleAddVariable}>Add</button>
            </div>

            {Object.entries(formData.variables).map(([key, value]) => (
              <div key={key} className="variable-item">
                <span className="var-key">{key}</span>
                <span className="var-value">***</span>
                <button onClick={() => handleRemoveVariable(key)}>✕</button>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button className="btn-save" onClick={handleSaveEnvironment}>Save Environment</button>
            <button className="btn-cancel" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="environments-list">
        {Object.entries(environments).map(([name, env]) => (
          <div
            key={name}
            className={`env-item ${selectedEnvironment === name ? 'selected' : ''}`}
            onClick={() => onSelectEnvironment(name)}
          >
            <div className="env-info">
              <span className="env-name">{name}</span>
              <span className="var-count">{Object.keys(env.variables).length} vars</span>
            </div>
            <button
              className="btn-delete"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteEnvironment(name)
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default EnvironmentManager
