const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface AiRenderResult {
  image_url: string
}

export class AiRenderError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message)
    this.name = 'AiRenderError'
  }
}

export async function generateAiRender(
  faceFile: File,
  glassesUrl: string,
): Promise<AiRenderResult> {
  const form = new FormData()
  form.append('face_image', faceFile)
  form.append('glasses_url', glassesUrl)

  const response = await fetch(`${API_BASE}/api/try-on/render-ai`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    let detail = `Server error (${response.status})`
    try {
      const json = await response.json()
      if (typeof json?.detail === 'string') detail = json.detail
    } catch {
      // use default detail
    }
    throw new AiRenderError(detail, response.status)
  }

  const data = (await response.json()) as AiRenderResult
  if (!data.image_url) {
    throw new AiRenderError('Server returned an empty image URL.')
  }
  return data
}
