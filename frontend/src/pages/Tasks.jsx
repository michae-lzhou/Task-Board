/*******************************************************************************
 * Tasks.jsx
 * Purpose: Kanban-style task management interface with drag-and-drop 
 *          functionality. Displays tasks in columns (To-do, In Progress, Done)
 *          with real-time updates via WebSocket connections.
 ******************************************************************************/

import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import './Tasks.css'
import { useWebSocketTasks } from '../hooks/useWebSocket'
import ConnectionIndicator from '../components/ConnectionIndicator'

function Tasks({ projectId, onBack }) {
  const [tasks, setTasks] = useState([])
  const [project, setProject] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTask, setEditingTask] = useState(null)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskStatus, setNewTaskStatus] = useState('todo')
  const [newTaskAssigneeId, setNewTaskAssigneeId] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [draggedTask, setDraggedTask] = useState(null)
  const [dragOverColumn, setDragOverColumn] = useState(null)

  // WebSocket handler for real-time task updates
  const handleTasksChange = useCallback((action, taskData) => {
    // Only handle tasks for the current project
    if (taskData.project_id !== parseInt(projectId)) {
      return
    }

    switch (action) {
      case 'created':
        setTasks(prev => {
          const exists = prev.some(t => t.id === taskData.id)
          if (exists) return prev
          return [...prev, taskData]
        })
        break
      
      case 'updated':
        setTasks(prev => 
          prev.map(t => t.id === taskData.id ? 
            { ...t, ...taskData } : t)
        )
        break
      
      case 'deleted':
        setTasks(prev => 
          prev.filter(t => t.id !== taskData.id)
        )
        break
      
      default:
        console.log('Unknown task action:', action)
    }
  }, [projectId])

  useWebSocketTasks(handleTasksChange)

  useEffect(() => {
    if (projectId) {
      fetchProjectData()
    }
  }, [projectId])

  const fetchProjectData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [projectResponse, tasksResponse, membersResponse] = 
        await Promise.all([
          axios.get(`http://localhost:8000/projects/${projectId}`),
          axios.get(`http://localhost:8000/projects/${projectId}/tasks`),
          axios.get(`http://localhost:8000/projects/${projectId}/users`)
        ])
      
      setProject(projectResponse.data)
      setTasks(tasksResponse.data)
      setMembers(membersResponse.data)
    } catch (err) {
      setError('Failed to fetch project tasks')
      console.error('Error fetching project data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Drag and Drop Handlers
  const handleDragStart = (e, task) => {
    console.log('Drag start:', task.title)
    setDraggedTask(task)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', task.id.toString())
    
    e.target.style.opacity = '0.5'
    
    setTimeout(() => {
      e.target.classList.add('dragging')
    }, 0)
  }

  const handleDragEnd = (e) => {
    console.log('Drag end')
    e.target.style.opacity = '1'
    e.target.classList.remove('dragging')
    setDraggedTask(null)
    setDragOverColumn(null)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDragEnter = (e, status) => {
    e.preventDefault()
    console.log('Drag enter:', status)
    setDragOverColumn(status)
  }

  const handleDragLeave = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX
    const y = e.clientY
    
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      setDragOverColumn(null)
    }
  }

  const handleDrop = async (e, newStatus) => {
    e.preventDefault()
    console.log('Drop on:', newStatus)
    setDragOverColumn(null)
    
    if (!draggedTask) {
      console.log('No dragged task')
      return
    }
    
    if (draggedTask.status === newStatus) {
      console.log('Same status, no change needed')
      return
    }

    console.log(`Moving task ${draggedTask.id} from ${draggedTask.status} 
                to ${newStatus}`)

    // Optimistically update the UI
    const updatedTasks = tasks.map(task => 
      task.id === draggedTask.id 
        ? { ...task, status: newStatus }
        : task
    )
    setTasks(updatedTasks)

    try {
      const payload = {
        title: draggedTask.title,
        description: draggedTask.description || null,
        status: newStatus,
        project_id: parseInt(projectId),
        assigned_to: draggedTask.assigned_to || null
      }
      
      const response = await axios.put(
        `http://localhost:8000/tasks/${draggedTask.id}`, 
        payload
      )
      
      console.log(`Task ${draggedTask.id} successfully moved to ${newStatus}`)
      
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === draggedTask.id ? response.data : task
        )
      )
    } catch (err) {
      console.error('Error updating task status:', err)
      setTasks(tasks)
      alert('Failed to update task status. Please try again.')
    }
  }

  const handleAddTask = () => {
    setShowAddModal(true)
    resetTaskForm()
  }

  const handleEditTask = (task) => {
    setEditingTask(task)
    setNewTaskTitle(task.title)
    setNewTaskDescription(task.description || '')
    setNewTaskStatus(task.status)
    setNewTaskAssigneeId(task.assigned_to ? 
      task.assigned_to.toString() : '')
    setShowEditModal(true)
  }

  const resetTaskForm = () => {
    setNewTaskTitle('')
    setNewTaskDescription('')
    setNewTaskStatus('todo')
    setNewTaskAssigneeId('')
  }

  const handleCreateTask = async (e) => {
    e.preventDefault()
    if (!newTaskTitle.trim()) return

    try {
      setIsCreating(true)
      
      const payload = {
        title: newTaskTitle.trim(),
        description: newTaskDescription.trim() || null,
        status: newTaskStatus,
        project_id: parseInt(projectId),
        assigned_to: newTaskAssigneeId ? parseInt(newTaskAssigneeId) : null
      }
      
      console.log('Creating task with payload:', payload)
      
      const response = await axios.post('http://localhost:8000/tasks/', payload)
      
      setTasks(prev => {
        const exists = prev.some(t => t.id === response.data.id)
        if (exists) return prev
        return [...prev, response.data]
      })
      
      setShowAddModal(false)
      resetTaskForm()
      
      console.log('Task created successfully:', response.data)
    } catch (err) {
      console.error('Error creating task:', err)
      console.error('Error response:', err.response?.data)
      alert('Failed to create task. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  const handleUpdateTask = async (e) => {
    e.preventDefault()
    if (!newTaskTitle.trim() || !editingTask) return

    try {
      setIsUpdating(true)
      
      const payload = {
        title: newTaskTitle.trim(),
        description: newTaskDescription.trim() || null,
        status: newTaskStatus,
        project_id: parseInt(projectId),
        assigned_to: newTaskAssigneeId ? parseInt(newTaskAssigneeId) : null
      }
      
      console.log('Updating task with payload:', payload)
      
      const response = await axios.put(
        `http://localhost:8000/tasks/${editingTask.id}`, 
        payload
      )
      
      setTasks(tasks.map(task => 
        task.id === editingTask.id ? response.data : task
      ))
      
      setShowEditModal(false)
      setEditingTask(null)
      resetTaskForm()
      
      console.log('Task updated successfully:', response.data)
    } catch (err) {
      console.error('Error updating task:', err)
      console.error('Error response:', err.response?.data)
      alert('Failed to update task. Please try again.')
    } finally {
      setIsUpdating(false)
    }
  }

  const handleDeleteTask = async (taskId) => {
    try {
      await axios.delete(`http://localhost:8000/tasks/${taskId}`)
      setTasks(tasks.filter(task => task.id !== taskId))
    } catch (err) {
      console.error('Error deleting task:', err)
      alert('Failed to delete task')
    }
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setShowEditModal(false)
    setEditingTask(null)
    resetTaskForm()
  }

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status)
  }

  const getAssigneeName = (assignedTo) => {
    if (!assignedTo) return null
    const member = members.find(m => m.id === assignedTo)
    return member ? member.name : 'Unknown User'
  }

  const getInitials = (name) => {
    if (!name) return '?'
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

  // Common header component
  const renderHeader = () => (
    <header className="fixed-header">
      <div className="header-content tasks-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Dashboard
        </button>

        <div className="header-text">
          <h1>
            {project?.name ? `${project.name} Tasks` : 'Project Tasks'}
          </h1>
          <div className="project-info">
            {loading ? 'Loading...' : 
              `${tasks.length} Tasks${project ? 
                ` • Project #${project.id}` : ''}`
            }
          </div>
        </div>

        <div className="header-right">
          <ConnectionIndicator />
          <button className="add-task-btn" onClick={handleAddTask}>
            <span className="add-icon">+</span>
            Add Task
          </button>
        </div>
      </div>
    </header>
  )

  if (loading) {
    return (
      <>
        {renderHeader()}
        <div className="tasks-page">
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading tasks...</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        {renderHeader()}
        <div className="tasks-page">
          <div className="error">
            <p>{error}</p>
            <button onClick={fetchProjectData} className="retry-btn">
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
      
      <div className="tasks-page">
        <div className="kanban-board">
          <KanbanColumn 
            title="To-do" 
            status="todo" 
            tasks={getTasksByStatus('todo')}
            members={members}
            onEditTask={handleEditTask}
            onDeleteTask={handleDeleteTask}
            getAssigneeName={getAssigneeName}
            getInitials={getInitials}
            getRandomColor={getRandomColor}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            isDragOver={dragOverColumn === 'todo'}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          />
          <KanbanColumn 
            title="In Progress" 
            status="in-progress" 
            tasks={getTasksByStatus('in-progress')}
            members={members}
            onEditTask={handleEditTask}
            onDeleteTask={handleDeleteTask}
            getAssigneeName={getAssigneeName}
            getInitials={getInitials}
            getRandomColor={getRandomColor}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            isDragOver={dragOverColumn === 'in-progress'}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          />
          <KanbanColumn 
            title="Done" 
            status="done" 
            tasks={getTasksByStatus('done')}
            members={members}
            onEditTask={handleEditTask}
            onDeleteTask={handleDeleteTask}
            getAssigneeName={getAssigneeName}
            getInitials={getInitials}
            getRandomColor={getRandomColor}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            isDragOver={dragOverColumn === 'done'}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          />
        </div>

        {tasks.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>No Tasks Yet</h3>
            <p>Create your first task to get started with project management</p>
            <button className="create-first-btn" onClick={handleAddTask}>
              <span className="add-icon">+</span>
              Create Your First Task
            </button>
          </div>
        )}
      </div>

      {/* Add Task Modal */}
      {showAddModal && (
        <>
          <div className="modal-overlay" onClick={handleCloseModal}></div>
          <div className="modal">
            <div className="modal-header">
              <h2>Create New Task</h2>
              <button className="close-btn" onClick={handleCloseModal}>
                ×
              </button>
            </div>
            <form onSubmit={handleCreateTask} className="modal-content">
              <div className="form-group">
                <label htmlFor="taskTitle">Task Title</label>
                <input
                  type="text"
                  id="taskTitle"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="Enter task title..."
                  autoFocus
                  disabled={isCreating}
                />
              </div>
              <div className="form-group">
                <label htmlFor="taskDescription">Description (Optional)</label>
                <textarea
                  id="taskDescription"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  placeholder="Enter task description..."
                  disabled={isCreating}
                />
              </div>
              <div className="form-group">
                <label htmlFor="taskStatus">Status</label>
                <select
                  id="taskStatus"
                  value={newTaskStatus}
                  onChange={(e) => setNewTaskStatus(e.target.value)}
                  disabled={isCreating}
                >
                  <option value="todo">To-do</option>
                  <option value="in-progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="taskAssignee">Assignee (Optional)</label>
                <select
                  id="taskAssignee"
                  value={newTaskAssigneeId}
                  onChange={(e) => setNewTaskAssigneeId(e.target.value)}
                  disabled={isCreating}
                >
                  <option value="">Unassigned</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
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
                  disabled={!newTaskTitle.trim() || isCreating}
                >
                  {isCreating ? (
                    <>
                      <div className="btn-spinner"></div>
                      Creating...
                    </>
                  ) : (
                    <>
                      <span className="add-icon">+</span>
                      Create Task
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </>
      )}

      {/* Edit Task Modal */}
      {showEditModal && editingTask && (
        <>
          <div className="modal-overlay" onClick={handleCloseModal}></div>
          <div className="modal">
            <div className="modal-header">
              <h2>Edit Task</h2>
              <button className="close-btn" onClick={handleCloseModal}>
                ×
              </button>
            </div>
            <form onSubmit={handleUpdateTask} className="modal-content">
              <div className="form-group">
                <label htmlFor="editTaskTitle">Task Title</label>
                <input
                  type="text"
                  id="editTaskTitle"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="Enter task title..."
                  autoFocus
                  disabled={isUpdating}
                />
              </div>
              <div className="form-group">
                <label htmlFor="editTaskDescription">
                  Description (Optional)
                </label>
                <textarea
                  id="editTaskDescription"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  placeholder="Enter task description..."
                  disabled={isUpdating}
                />
              </div>
              <div className="form-group">
                <label htmlFor="editTaskStatus">Status</label>
                <select
                  id="editTaskStatus"
                  value={newTaskStatus}
                  onChange={(e) => setNewTaskStatus(e.target.value)}
                  disabled={isUpdating}
                >
                  <option value="todo">To-do</option>
                  <option value="in-progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="editTaskAssignee">Assignee (Optional)</label>
                <select
                  id="editTaskAssignee"
                  value={newTaskAssigneeId}
                  onChange={(e) => setNewTaskAssigneeId(e.target.value)}
                  disabled={isUpdating}
                >
                  <option value="">Unassigned</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn secondary" 
                  onClick={handleCloseModal}
                  disabled={isUpdating}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn primary"
                  disabled={!newTaskTitle.trim() || isUpdating}
                >
                  {isUpdating ? (
                    <>
                      <div className="btn-spinner"></div>
                      Updating...
                    </>
                  ) : (
                    'Update Task'
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

function KanbanColumn({ 
  title, 
  status, 
  tasks, 
  onEditTask, 
  onDeleteTask, 
  getAssigneeName, 
  getInitials, 
  getRandomColor,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop,
  isDragOver,
  onDragStart,
  onDragEnd
}) {
  return (
    <div 
      className={`kanban-column ${isDragOver ? 'drag-over' : ''}`}
      onDragOver={onDragOver}
      onDragEnter={(e) => onDragEnter(e, status)}
      onDragLeave={onDragLeave}
      onDrop={(e) => onDrop(e, status)}
    >
      <div className="column-header">
        <div className="column-title">
          <div className={`status-icon ${status}`}></div>
          {title}
        </div>
        <div className="task-count">{tasks.length}</div>
      </div>
      
      <div className="tasks-list">
        {tasks.length > 0 ? (
          tasks.map((task) => (
            <TaskCard 
              key={task.id} 
              task={task}
              status={status}
              onEdit={onEditTask}
              onDelete={onDeleteTask}
              getAssigneeName={getAssigneeName}
              getInitials={getInitials}
              getRandomColor={getRandomColor}
              onDragStart={onDragStart}
              onDragEnd={onDragEnd}
            />
          ))
        ) : (
          <div className="empty-column">
            <div className="empty-column-icon">
              {status === 'todo' && '📝'}
              {status === 'in-progress' && '⚡'}
              {status === 'done' && '✅'}
            </div>
            <p>No {title.toLowerCase()} tasks</p>
          </div>
        )}
      </div>
    </div>
  )
}

function TaskCard({ 
  task, 
  status, 
  onEdit, 
  onDelete, 
  getAssigneeName, 
  getInitials, 
  getRandomColor,
  onDragStart,
  onDragEnd
}) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleDeleteClick = async () => {
    await onDelete(task.id)
    setShowDeleteConfirm(false)
  }

  const handleDragStart = (e) => {
    if (showDeleteConfirm) {
      e.preventDefault()
      return
    }
    onDragStart(e, task)
  }

  const handleMouseDown = (e) => {
    if (e.target.closest('.task-actions') || 
        e.target.closest('.delete-confirm')) {
      return
    }
  }

  const assigneeName = getAssigneeName(task.assigned_to)

  return (
    <div 
      className={`task-card ${status}`}
      draggable={!showDeleteConfirm}
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      onMouseDown={handleMouseDown}
    >
      <div className="task-header">
        <h4 className="task-title">{task.title}</h4>
        <div className="task-id">#{task.id}</div>
      </div>

      {task.description && (
        <div className="task-description">
          {task.description}
        </div>
      )}

      <div className="task-footer">
        <div className="task-assignee">
          {assigneeName ? (
            <>
              <div 
                className="assignee-avatar" 
                style={{ background: getRandomColor(task.assigned_to) }}
              >
                {getInitials(assigneeName)}
              </div>
              <span>{assigneeName}</span>
            </>
          ) : (
            <span>Unassigned</span>
          )}
        </div>

        <div className="task-actions">
          <button 
            className="task-action-btn edit"
            onClick={(e) => {
              e.stopPropagation()
              onEdit(task)
            }}
            title="Edit task"
          >
            ✏️
          </button>
          <button 
            className="task-action-btn delete"
            onClick={(e) => {
              e.stopPropagation()
              setShowDeleteConfirm(true)
            }}
            title="Delete task"
          >
            🗑️
          </button>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="delete-confirm">
          <p>Delete "{task.title}"?</p>
          <div className="confirm-actions">
            <button 
              className="btn btn-danger-solid" 
              onClick={(e) => {
                e.stopPropagation()
                handleDeleteClick()
              }}
            >
              Delete
            </button>
            <button 
              className="btn secondary" 
              onClick={(e) => {
                e.stopPropagation()
                setShowDeleteConfirm(false)
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Tasks
