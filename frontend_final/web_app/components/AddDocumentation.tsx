import React, { useState } from 'react'

interface AddDocumentationProps {
  onNext: () => void;
}

const AddDocumentation: React.FC<AddDocumentationProps> = ({ onNext }) => {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here we would typically send the URL to the backend
    console.log('Submitted URL:', url)
    onNext()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="docUrl" className="block text-sm font-medium text-gray-700">
          Documentation URL
        </label>
        <input
          type="url"
          id="docUrl"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          placeholder="https://docs.example.com"
        />
      </div>
      <div className="flex justify-end">
        <button
          type="submit"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Next
        </button>
      </div>
    </form>
  )
}

export default AddDocumentation;