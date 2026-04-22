import { useRef, useState, type DragEvent, type ChangeEvent } from 'react'
import { cn } from '@/lib/cn'

const MAX_SIZE_BYTES = 10 * 1024 * 1024
const ACCEPT = ['image/jpeg', 'image/png']

interface Props {
  onFile: (file: File) => void
  disabled?: boolean
}

export function FaceUpload({ onFile, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [sizeError, setSizeError] = useState(false)

  function handleFile(file: File) {
    setSizeError(false)
    if (!ACCEPT.includes(file.type)) return
    if (file.size > MAX_SIZE_BYTES) { setSizeError(true); return }
    onFile(file)
  }

  function onInputChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
    e.target.value = ''
  }

  function onDrop(e: DragEvent) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-md">
      <div
        className={cn(
          'w-full border-2 border-dashed rounded-2xl p-10 flex flex-col items-center gap-4 transition-all cursor-pointer select-none',
          dragging
            ? 'border-gold-400 bg-gold-50 scale-[1.01]'
            : 'border-brand-200 bg-white hover:border-gold-300 hover:bg-gold-50/40',
          disabled && 'opacity-50 pointer-events-none',
        )}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        {/* Icon */}
        <div className={cn(
          'w-16 h-16 rounded-2xl flex items-center justify-center transition-colors',
          dragging ? 'bg-gold-400' : 'bg-brand-900',
        )}>
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
          </svg>
        </div>

        <div className="text-center">
          <p className="font-bold text-brand-900 text-lg">Upload your photo</p>
          <p className="text-sm text-brand-400 mt-1">
            Drag & drop or{' '}
            <span className="text-gold-500 font-semibold">browse files</span>
          </p>
          <p className="text-xs text-brand-300 mt-2">JPG or PNG · up to 10 MB</p>
        </div>
      </div>

      {sizeError && (
        <div className="w-full flex items-center gap-2 px-4 py-3 rounded-xl bg-red-50 border border-red-200">
          <svg className="w-4 h-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <p className="text-sm text-red-600 font-medium">File too large — please use a photo under 10 MB.</p>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT.join(',')}
        className="hidden"
        onChange={onInputChange}
      />
    </div>
  )
}
