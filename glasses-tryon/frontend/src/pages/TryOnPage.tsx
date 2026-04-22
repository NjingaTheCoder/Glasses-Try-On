import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Navbar } from '@/components/layout/Navbar'
import { FaceUpload } from '@/components/tryon/FaceUpload'
import { GlassesSidebar } from '@/components/tryon/GlassesSidebar'
import { GlassesStrip } from '@/components/tryon/GlassesStrip'
import { Button } from '@/components/ui/Button'
import { useTryOnStore } from '@/store/tryonStore'
import { useProduct } from '@/hooks/useProducts'
import { generateAiRender, AiRenderError } from '@/lib/aiRender'
import type { Product } from '@/types/product'

type RenderState = 'idle' | 'generating' | 'success' | 'error'

export default function TryOnPage() {
  const { productId } = useParams<{ productId?: string }>()
  const { product: preselectedProduct } = useProduct(productId)

  const {
    facePhoto,
    facePhotoUrl,
    selectedProduct,
    setFacePhoto,
    setSelectedProduct,
    reset,
  } = useTryOnStore()

  const [photoObjectUrl, setPhotoObjectUrl] = useState<string | null>(null)
  const [renderState, setRenderState] = useState<RenderState>('idle')
  const [aiImageUrl, setAiImageUrl] = useState<string | null>(null)
  const [aiError, setAiError] = useState<string | null>(null)

  useEffect(() => {
    if (preselectedProduct && !selectedProduct) setSelectedProduct(preselectedProduct)
  }, [preselectedProduct, selectedProduct, setSelectedProduct])

  function handleFile(file: File) {
    if (photoObjectUrl) URL.revokeObjectURL(photoObjectUrl)
    const url = URL.createObjectURL(file)
    setFacePhoto(file, url)
    setPhotoObjectUrl(url)
    resetRender()
  }

  function handleReset() {
    if (photoObjectUrl) URL.revokeObjectURL(photoObjectUrl)
    setPhotoObjectUrl(null)
    reset()
    resetRender()
  }

  function handleProductSelect(product: Product) {
    setSelectedProduct(product)
    resetRender()
  }

  function resetRender() {
    setRenderState('idle')
    setAiImageUrl(null)
    setAiError(null)
  }

  async function handleGenerate() {
    if (!facePhoto || !selectedProduct) return
    setRenderState('generating')
    setAiError(null)
    setAiImageUrl(null)
    try {
      const result = await generateAiRender(facePhoto, selectedProduct.image_url)
      setAiImageUrl(result.image_url)
      setRenderState('success')
    } catch (err) {
      setAiError(err instanceof AiRenderError ? err.message : 'Unexpected error. Please try again.')
      setRenderState('error')
    }
  }

  function handleDownload() {
    if (!aiImageUrl) return
    const a = document.createElement('a')
    a.href = aiImageUrl
    a.download = `humaine-tryon-${selectedProduct?.name ?? 'result'}.png`
    a.click()
  }

  const hasPhoto = !!facePhotoUrl
  const isGenerating = renderState === 'generating'
  const canGenerate = !!facePhoto && !!selectedProduct && !isGenerating

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#fafaf8' }}>
      <Navbar />

      {/* Steps indicator */}
      <div className="bg-white border-b border-brand-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-4">
          {[
            { n: 1, label: 'Upload Photo', done: hasPhoto },
            { n: 2, label: 'Choose Frame', done: hasPhoto && !!selectedProduct },
            { n: 3, label: 'Generate', done: renderState === 'success' },
          ].map((step, idx) => (
            <div key={step.n} className="flex items-center">
              <div className="flex items-center gap-2">
                <span className={[
                  'w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center transition-colors',
                  step.done
                    ? 'bg-gold-400 text-white'
                    : hasPhoto && idx === 1 && !selectedProduct
                    ? 'bg-brand-100 text-brand-600 ring-2 ring-brand-300'
                    : 'bg-brand-100 text-brand-400',
                ].join(' ')}>
                  {step.done ? (
                    <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : step.n}
                </span>
                <span className={[
                  'text-xs font-semibold hidden sm:inline',
                  step.done ? 'text-brand-700' : 'text-brand-300',
                ].join(' ')}>
                  {step.label}
                </span>
              </div>
              {idx < 2 && (
                <div className="w-8 sm:w-16 h-px bg-brand-100 mx-2" />
              )}
            </div>
          ))}
          <div className="flex items-center gap-4 ml-auto shrink-0">
            {hasPhoto && (
              <button onClick={handleReset} className="text-xs font-semibold text-brand-400 hover:text-brand-700 transition-colors">
                ↑ New photo
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Step 1: Upload ── */}
      {!hasPhoto && (
        <div className="flex-1 flex flex-col items-center justify-center py-16 px-4">
          <div className="text-center mb-8">
            <p className="text-brand-400 text-sm font-medium">Step 1 of 3</p>
            <h2 className="text-2xl font-bold text-brand-900 mt-1">Upload your portrait photo</h2>
            <p className="text-brand-400 text-sm mt-2 max-w-sm mx-auto">
              Use a front-facing, well-lit photo for the best results. Your photo stays private.
            </p>
          </div>
          <FaceUpload onFile={handleFile} />
        </div>
      )}

      {/* ── Step 2 + 3: Select frame + generate ── */}
      {hasPhoto && (
        <div className="flex flex-col lg:flex-row flex-1 overflow-hidden">

          {/* Desktop sidebar */}
          <div className="hidden lg:flex flex-col w-72 shrink-0 border-r border-brand-100 bg-white p-5 overflow-y-auto">
            <GlassesSidebar selected={selectedProduct} onSelect={handleProductSelect} />
          </div>

          {/* Main */}
          <div className="flex-1 flex flex-col items-center px-4 py-10 gap-8 overflow-auto">

            {/* Face + glasses preview */}
            <div className="flex items-stretch gap-4 flex-wrap justify-center w-full max-w-2xl">
              {/* Face card */}
              <div className="flex flex-col rounded-2xl overflow-hidden border border-brand-100 shadow-card bg-white min-w-[160px]">
                <div className="bg-gradient-to-br from-brand-50 to-brand-100 p-1">
                  <img
                    src={facePhotoUrl!}
                    alt="Your face"
                    className="h-44 w-44 object-cover rounded-xl"
                  />
                </div>
                <div className="px-3 py-2 text-center">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-brand-400">Your photo</p>
                </div>
              </div>

              {/* Plus sign */}
              {selectedProduct && (
                <div className="flex items-center self-center">
                  <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center">
                    <svg className="w-4 h-4 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                  </div>
                </div>
              )}

              {/* Glasses card */}
              {selectedProduct ? (
                <div className="flex flex-col rounded-2xl overflow-hidden border border-gold-200 shadow-card bg-white min-w-[160px]">
                  <div className="bg-gradient-to-br from-gold-50 to-gold-100/60 p-4 flex items-center justify-center h-44 w-44">
                    <img
                      src={selectedProduct.image_url}
                      alt={selectedProduct.name}
                      className="max-h-full max-w-full object-contain"
                    />
                  </div>
                  <div className="px-3 py-2 text-center border-t border-gold-100">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-gold-500">{selectedProduct.brand}</p>
                    <p className="text-xs font-semibold text-brand-800 truncate">{selectedProduct.name}</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-brand-200 bg-white min-w-[160px] h-[200px] w-44 gap-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center">
                    <svg className="w-5 h-5 text-brand-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                      <circle cx="7" cy="12" r="3" />
                      <circle cx="17" cy="12" r="3" />
                      <path d="M10 12h4M4 12H2M22 12h-2" />
                    </svg>
                  </div>
                  <p className="text-xs text-brand-400 font-medium text-center px-4">Select a frame from the sidebar</p>
                </div>
              )}
            </div>

            {/* Generate CTA */}
            {selectedProduct && renderState !== 'success' && (
              <div className="flex flex-col items-center gap-3">
                <Button
                  onClick={handleGenerate}
                  disabled={!canGenerate}
                  size="lg"
                  className="min-w-[220px]"
                >
                  {isGenerating ? (
                    <span className="flex items-center gap-2.5">
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Generating your render…
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                      </svg>
                      Generate Try-On
                    </span>
                  )}
                </Button>
                {!isGenerating && (
                  <p className="text-xs text-brand-400 text-center">
                    AI render takes 45–60 seconds · processed securely · photo not stored
                  </p>
                )}
              </div>
            )}

            {/* Generating */}
            {isGenerating && (
              <div className="flex flex-col items-center gap-4 py-4">
                <div className="relative w-14 h-14">
                  <div className="absolute inset-0 border-4 border-brand-100 rounded-full" />
                  <div className="absolute inset-0 border-4 border-gold-400 border-t-transparent rounded-full animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-3 h-3 rounded-full bg-gold-400 animate-pulse" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-sm font-semibold text-brand-800">Creating your realistic render</p>
                  <p className="text-xs text-brand-400 mt-0.5">Our AI is placing the frames on your photo…</p>
                </div>
              </div>
            )}

            {/* Error */}
            {renderState === 'error' && aiError && (
              <div className="w-full max-w-md bg-red-50 border border-red-200 rounded-2xl p-5">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-red-700">Render failed</p>
                    <p className="text-sm text-red-600 mt-0.5">{aiError}</p>
                    <button
                      onClick={handleGenerate}
                      className="mt-3 text-xs font-semibold text-red-500 underline underline-offset-2 hover:text-red-700"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Result */}
            {renderState === 'success' && aiImageUrl && (
              <div className="flex flex-col items-center gap-5 w-full max-w-2xl">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-gold-400 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-sm font-bold text-brand-900 uppercase tracking-wider">Your Try-On Result</p>
                </div>

                <div className="rounded-3xl overflow-hidden shadow-card-hover border border-brand-100 w-full">
                  <img
                    src={aiImageUrl}
                    alt="AI try-on result"
                    className="w-full object-contain"
                    style={{ maxHeight: '680px' }}
                  />
                </div>

                <div className="flex gap-3 flex-wrap justify-center">
                  <Button onClick={handleDownload} variant="primary">
                    <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    Download
                  </Button>
                  <Button onClick={resetRender} variant="secondary">
                    Try a different frame
                  </Button>
                  <Link to={`/product/${selectedProduct?.id}`}>
                    <Button variant="outline">View product</Button>
                  </Link>
                </div>

                <p className="text-xs text-brand-300 text-center">
                  AI-generated result · actual product may vary slightly · for reference only
                </p>
              </div>
            )}

          </div>

          {/* Mobile strip */}
          <div className="lg:hidden mt-auto sticky bottom-0 z-10">
            <GlassesStrip selected={selectedProduct} onSelect={handleProductSelect} />
          </div>

        </div>
      )}
    </div>
  )
}
