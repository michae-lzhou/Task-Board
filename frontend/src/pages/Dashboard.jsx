import { useEffect, useState } from 'react'
import axios from 'axios'
import './Dashboard.css'
import Members from './Members'  // Import the Members component
import Tasks from './Tasks'      // Import the Tasks component

function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  
  // Navigation state
  const [currentView, setCurrentView] = useState('dashboard') // 'dashboard', 'members', or 'tasks'
  const [selectedProjectId, setSelectedProjectId] = useState(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      // Using your FastAPI projects endpoint
      const response = await axios.get('http://localhost:8000/projects/')
      setProjects(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch projects')
      console.error('Error fetching projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteProject = (projectId) => {
    setProjects(projects.filter(p => p.id !== projectId))
  }

  const handleAddProject = () => {
    setShowAddModal(true)
    setNewProjectName('')
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    if (!newProjectName.trim()) return

    try {
      setIsCreating(true)
      // Create new project via API
      const response = await axios.post('http://localhost:8000/projects/', {
        name: newProjectName.trim()
      })
      
      // Add the new project to the list
      setProjects([...projects, response.data])
      
      // Close modal and reset form
      setShowAddModal(false)
      setNewProjectName('')
      
      console.log('Project created successfully:', response.data)
    } catch (err) {
      console.error('Error creating project:', err)
      alert('Failed to create project. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setNewProjectName('')
  }

  // Navigation functions
  const handleViewMembers = (projectId) => {
    setSelectedProjectId(projectId)
    setCurrentView('members')
  }

  const handleViewTasks = (projectId) => {
    setSelectedProjectId(projectId)
    setCurrentView('tasks')
  }

  const handleBackToDashboard = () => {
    setCurrentView('dashboard')
    setSelectedProjectId(null)
    fetchProjects()
  }

  // Render the appropriate view
  if (currentView === 'members' && selectedProjectId) {
    return (
      <Members 
        projectId={selectedProjectId} 
        onBack={handleBackToDashboard}
      />
    )
  }

  if (currentView === 'tasks' && selectedProjectId) {
    return (
      <Tasks 
        projectId={selectedProjectId} 
        onBack={handleBackToDashboard}
      />
    )
  }

  if (loading) {
    return (
      <>
        <header className="fixed-header">
          <div className="header-content">
            <h1>Project Dashboard</h1>
            <div className="project-count">{projects.length} Projects</div>
            <button className="add-project-btn" onClick={handleAddProject}>
              <span className="add-icon">+</span>
              Add Project
            </button>
          </div>
        </header>
        <div className="dashboard">
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading projects...</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        <header className="fixed-header">
          <div className="header-content">
            <h1>Project Dashboard</h1>
            <div className="project-count">{projects.length} Projects</div>
            <button className="add-project-btn" onClick={handleAddProject}>
              <span className="add-icon">+</span>
              Add Project
            </button>
          </div>
        </header>
        <div className="dashboard">
          <div className="error">
            <p>{error}</p>
            <button onClick={fetchProjects} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <header className="fixed-header">
        <div className="header-content">
          <h1>Project Dashboard</h1>
          <div className="project-count">{projects.length} Projects</div>
          <button className="add-project-btn" onClick={handleAddProject}>
            <span className="add-icon">+</span>
            Add Project
          </button>
        </div>
      </header>
      
      <div className="dashboard">
        <div className="projects-grid">
          {projects.map((project) => (
            <ProjectCard 
              key={project.id} 
              project={project} 
              onDeleteProject={handleDeleteProject}
              onViewMembers={handleViewMembers}
              onViewTasks={handleViewTasks}
            />
          ))}
        </div>

        {projects.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>No Projects Yet</h3>
            <p>Create your first project to get started</p>
            <button className="create-first-btn" onClick={handleAddProject}>
              <span className="add-icon">+</span>
              Create Your First Project
            </button>
          </div>
        )}
      </div>

      {/* Add Project Modal */}
      {showAddModal && (
        <>
          <div className="modal-overlay" onClick={handleCloseModal}></div>
          <div className="modal">
            <div className="modal-header">
              <h2>Create New Project</h2>
              <button className="close-btn" onClick={handleCloseModal}>×</button>
            </div>
            <form onSubmit={handleCreateProject} className="modal-content">
              <div className="form-group">
                <label htmlFor="projectName">Project Name</label>
                <input
                  type="text"
                  id="projectName"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Enter project name..."
                  autoFocus
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
                  disabled={!newProjectName.trim() || isCreating}
                >
                  {isCreating ? (
                    <>
                      <div className="btn-spinner"></div>
                      Creating...
                    </>
                  ) : (
                    <>
                      <span className="add-icon">+</span>
                      Create Project
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

function ProjectCard({ project, onDeleteProject, onViewMembers, onViewTasks }) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [taskCount, setTaskCount] = useState(null)
  const [loadingTasks, setLoadingTasks] = useState(false)

  useEffect(() => {
    fetchTaskCount()
  }, [project.id])

  const fetchTaskCount = async () => {
    try {
      setLoadingTasks(true)
      const response = await axios.get(`http://localhost:8000/projects/${project.id}/tasks`)
      setTaskCount(response.data.length)
    } catch (err) {
      console.error('Error fetching tasks:', err)
    } finally {
      setLoadingTasks(false)
    }
  }

  const handleDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/projects/${project.id}`)
      onDeleteProject(project.id)
      setShowDeleteConfirm(false)
    } catch (err) {
      console.error('Error deleting project:', err)
      alert('Failed to delete project')
    }
  }

  return (
    <div className="project-card">
      <div className="project-header">
        <h3 className="project-title">{project.name}</h3>
        <div className="project-id">#{project.id}</div>
      </div>

      <div className="project-stats">
        <div className="stat">
          <span className="stat-number">{project.members?.length || 0}</span>
          <span className="stat-label">Members</span>
        </div>
        <div className="stat">
          <span className="stat-number">
            {loadingTasks ? '•••' : (taskCount ?? '0')}
          </span>
          <span className="stat-label">Tasks</span>
        </div>
      </div>

      {project.members && project.members.length > 0 && (
        <div className="project-members">
          <div className="members-list">
            {project.members.slice(0, 4).map((member) => (
              <div key={member.id} className="member-avatar" title={member.name}>
                {member.name.charAt(0).toUpperCase()}
              </div>
            ))}
            {project.members.length > 4 && (
              <div className="member-avatar more">
                +{project.members.length - 4}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="project-actions">
        <button 
          className="btn primary"
          onClick={() => onViewTasks(project.id)}
        >
          Tasks
        </button>
        <button 
          className="btn secondary"
          onClick={() => onViewMembers(project.id)}
        >
          Members
        </button>
        <button 
          className="btn danger"
          onClick={() => setShowDeleteConfirm(true)}
        >
          Delete
        </button>
      </div>

      {showDeleteConfirm && (
        <div className="delete-confirm">
          <p>Delete "{project.name}"?</p>
          <div className="confirm-actions">
            <button className="btn btn-danger-solid" onClick={handleDelete}>
              Delete
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

export default Dashboard
