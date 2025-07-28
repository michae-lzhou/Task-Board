import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import './Members.css'
import { useWebSocketMembers } from '../hooks/useWebSocket'
import ConnectionIndicator from '../components/ConnectionIndicator'

function Members({ projectId, onBack }) {
  const [members, setMembers] = useState([])
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newMemberName, setNewMemberName] = useState('')
  const [newMemberEmail, setNewMemberEmail] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  // WebSocket handler for real-time member updates
  const handleMembersChange = useCallback((action, payload) => {
    console.log('WebSocket member event:', action, payload)
    if (!payload || parseInt(payload.project_id) !== parseInt(projectId)) return
    const user = payload.user
    if (!user || !user.id) return
    if (action === 'added') {
      setMembers(prev => prev.some(m => m.id === user.id) ? prev : [...prev, user])
    } else if (action === 'removed') {
      setMembers(prev => prev.filter(m => m.id !== user.id))
    }
  }, [projectId])

  useWebSocketMembers(handleMembersChange)

  useEffect(() => {
    if (projectId) {
      fetchProjectAndMembers()
    }
  }, [projectId])

  const fetchProjectAndMembers = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [projectResponse, membersResponse] = await Promise.all([
        axios.get(`http://localhost:8000/projects/${projectId}`),
        axios.get(`http://localhost:8000/projects/${projectId}/users`)
      ])
      
      setProject(projectResponse.data)
      setMembers(membersResponse.data)
    } catch (err) {
      setError('Failed to fetch project members')
      console.error('Error fetching project/users:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddMember = () => {
    setShowAddModal(true)
    setNewMemberName('')
    setNewMemberEmail('')
  }

  const handleCreateMember = async (e) => {
    e.preventDefault()
    if (!newMemberName.trim() || !newMemberEmail.trim()) return

    try {
      setIsCreating(true)
      const response = await
            axios.post(`http://localhost:8000/projects/${projectId}/add-member`, {
        name: newMemberName.trim(),
        email: newMemberEmail.trim()
      })
      
      console.log("User added as a member:", response.data);
      setMembers([...members, response.data])
      setShowAddModal(false)
      setNewMemberName('')
      setNewMemberEmail('')
    } catch (err) {
      console.error('Error adding member:', err)
      alert('Failed to add member. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setNewMemberName('')
    setNewMemberEmail('')
  }

  const handleDeleteMember = (memberId) => {
    setMembers(members.filter(m => m.id !== memberId))
  }

  // Common header component (used in all states)
  const renderHeader = () => (
    <header className="fixed-header">
      <div className="header-content members-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Dashboard
        </button>

        <div className="header-text">
          <h1>{project?.name ? `${project.name} Members` : 'Project Members'}</h1>
          <div className="project-info">
            {loading ? 'Loading...' : `${members.length} Members${project ? ` • Project #${project.id}` : ''}`}
          </div>
        </div>

        <button className="add-member-btn" onClick={handleAddMember}>
          <span className="add-icon">+</span>
          Add Member
        </button>
      </div>
    </header>
  )

  if (loading) {
    return (
      <>
        {renderHeader()}
        <div className="members-page">
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading members...</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        {renderHeader()}
        <div className="members-page">
          <div className="error">
            <p>{error}</p>
            <button onClick={fetchProjectAndMembers} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      {renderHeader()}
      
      <div className="members-page">
        <div className="members-grid">
          {members.map((member) => (
            <MemberCard 
              key={member.id} 
              member={member}
              projectId={projectId}
              onDeleteMember={handleDeleteMember}
            />
          ))}
        </div>

        {members.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h3>No Members Yet</h3>
            <p>Add your first team member to get started</p>
            <button className="create-first-btn" onClick={handleAddMember}>
              <span className="add-icon">+</span>
              Add Your First Member
            </button>
          </div>
        )}
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <>
          <div className="modal-overlay" onClick={handleCloseModal}></div>
          <div className="modal">
            <div className="modal-header">
              <h2>Add Team Member</h2>
              <button className="close-btn" onClick={handleCloseModal}>×</button>
            </div>
            <form onSubmit={handleCreateMember} className="modal-content">
              <div className="form-group">
                <label htmlFor="memberName">Full Name</label>
                <input
                  type="text"
                  id="memberName"
                  value={newMemberName}
                  onChange={(e) => setNewMemberName(e.target.value)}
                  placeholder="Enter member's full name..."
                  autoFocus
                  disabled={isCreating}
                />
              </div>
              <div className="form-group">
                <label htmlFor="memberEmail">Email Address</label>
                <input
                  type="email"
                  id="memberEmail"
                  value={newMemberEmail}
                  onChange={(e) => setNewMemberEmail(e.target.value)}
                  placeholder="Enter member's email..."
                  disabled={isCreating}
                />
              </div>
              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn secondary" 
                  onClick={handleCloseModal}
                  disabled={isCreating}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn primary"
                  disabled={!newMemberName.trim() || !newMemberEmail.trim() || isCreating}
                >
                  {isCreating ? (
                    <>
                      <div className="btn-spinner"></div>
                      Adding...
                    </>
                  ) : (
                    <>
                      <span className="add-icon">+</span>
                      Add Member
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </>
      )}
    </>
  )
}

function MemberCard({ member, projectId, onDeleteMember }) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleDelete = async () => {
    try {
      await axios.post(`http://localhost:8000/projects/${projectId}/remove-member`, {
        name: member.name,
        email: member.email,
      })
      onDeleteMember(member.id)
      setShowDeleteConfirm(false)
    } catch (err) {
      console.error('Error removing member:', err)
      alert('Failed to remove member')
    }
  }

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('')
  }

  const getRandomColor = (id) => {
    const colors = [
      'linear-gradient(135deg, #3b82f6, #2563eb)',
      'linear-gradient(135deg, #10b981, #059669)',
      'linear-gradient(135deg, #8b5cf6, #7c3aed)',
      'linear-gradient(135deg, #f59e0b, #d97706)',
      'linear-gradient(135deg, #ef4444, #dc2626)',
      'linear-gradient(135deg, #06b6d4, #0891b2)',
    ]
    return colors[id % colors.length]
  }

  return (
    <div className="member-card">
      <div className="member-header">
        <div className="member-avatar-large" style={{ background: getRandomColor(member.id) }}>
          {getInitials(member.name)}
        </div>
        <div className="member-info">
          <h3 className="member-name">{member.name}</h3>
          <p className="member-email">{member.email}</p>
        </div>
      </div>

      <div className="member-actions">
        <button 
          className="btn danger"
          onClick={() => setShowDeleteConfirm(true)}
        >
          Remove
        </button>
      </div>

      {showDeleteConfirm && (
        <div className="delete-confirm">
          <p>Remove "{member.name}" from project?</p>
          <div className="confirm-actions">
            <button className="btn btn-danger-solid" onClick={handleDelete}>
              Remove
            </button>
            <button className="btn secondary" onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Members
