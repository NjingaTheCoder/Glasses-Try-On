import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import apiClient from '../api/client'

export default function UploadCard() {
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)
  const [consent, setConsent] = useState(false)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!consent) {
      alert('Please agree to the consent terms')
      return
    }

    setUploading(true)

    try {
      // Step 1: Prepare upload
      const prepareResponse = await apiClient.prepareUpload({
        filename: file.name,
        consent_given: consent,
      })

      // Step 2: Upload file to signed URL
      await apiClient.uploadToSignedUrl(prepareResponse.upload_url, file)

      // Step 3: Complete upload
      await apiClient.completeUpload(prepareResponse.image_id, true)

      // Refresh images list
      queryClient.invalidateQueries({ queryKey: ['user-images'] })

      alert('Photo uploaded successfully! Processing...')
    } catch (err) {
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="card">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <label className="cursor-pointer">
          <span className="btn btn-primary">
            {uploading ? 'Uploading...' : 'Choose Photo'}
          </span>
          <input
            type="file"
            className="hidden"
            accept="image/jpeg,image/jpg,image/png"
            onChange={handleFileSelect}
            disabled={uploading || !consent}
          />
        </label>

        <p className="mt-2 text-sm text-gray-500">
          Upload a full-body photo (JPG, PNG)
        </p>
      </div>

      <div className="mt-4 flex items-start">
        <input
          type="checkbox"
          id="consent"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          className="mt-1 mr-2"
        />
        <label htmlFor="consent" className="text-sm text-gray-600 cursor-pointer">
          I consent to processing my photo for virtual try-on purposes. My image will be used
          solely for generating try-on results and will not be shared with third parties.
        </label>
      </div>
    </div>
  )
}
