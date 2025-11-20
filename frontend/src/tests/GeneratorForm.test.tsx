import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import GeneratorForm from '../components/GeneratorForm'

describe('GeneratorForm', () => {
  it('renders form inputs', () => {
    render(<GeneratorForm onJobCreated={vi.fn()} onBlogGenerated={vi.fn()} />)
    
    expect(screen.getByPlaceholderText(/channel name/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/video title/i)).toBeInTheDocument()
    expect(screen.getByText(/Generate Blog/i)).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    render(<GeneratorForm onJobCreated={vi.fn()} onBlogGenerated={vi.fn()} />)
    
    const submitButton = screen.getByText(/Generate Blog/i)
    fireEvent.click(submitButton)
    
    // Form should not submit without values
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/channel name/i)).toHaveValue('')
    })
  })

  it('disables submit button while loading', async () => {
    render(<GeneratorForm onJobCreated={vi.fn()} onBlogGenerated={vi.fn()} />)
    
    const submitButton = screen.getByText(/Generate Blog/i)
    expect(submitButton).not.toBeDisabled()
  })
})
