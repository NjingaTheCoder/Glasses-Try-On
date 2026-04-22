import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage'
import { storage } from './firebase'

export async function uploadGlassesPng(
  file: File,
  onProgress?: (pct: number) => void,
): Promise<string> {
  const path = `glasses/${Date.now()}_${file.name}`
  const storageRef = ref(storage, path)
  const task = uploadBytesResumable(storageRef, file, { contentType: 'image/png' })

  return new Promise((resolve, reject) => {
    task.on(
      'state_changed',
      (snap) => {
        const pct = (snap.bytesTransferred / snap.totalBytes) * 100
        onProgress?.(pct)
      },
      reject,
      async () => {
        const url = await getDownloadURL(task.snapshot.ref)
        resolve(url)
      },
    )
  })
}

export async function uploadFacePhoto(
  file: File,
  sessionId: string,
  onProgress?: (pct: number) => void,
): Promise<string> {
  const path = `faces/${sessionId}/${Date.now()}_${file.name}`
  const storageRef = ref(storage, path)
  const task = uploadBytesResumable(storageRef, file)

  return new Promise((resolve, reject) => {
    task.on(
      'state_changed',
      (snap) => {
        const pct = (snap.bytesTransferred / snap.totalBytes) * 100
        onProgress?.(pct)
      },
      reject,
      async () => {
        const url = await getDownloadURL(task.snapshot.ref)
        resolve(url)
      },
    )
  })
}
