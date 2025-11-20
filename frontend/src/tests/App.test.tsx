import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders the app title', () => {
    render(<App />)
    expect(screen.getByText(/YouTube to Blog/i)).toBeInTheDocument()
  })

  it('renders the generator form initially', () => {
    render(<App />)
    expect(screen.getByPlaceholderText(/channel name/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/video title/i)).toBeInTheDocument()
  })
})
