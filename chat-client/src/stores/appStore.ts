import { create } from 'zustand'
import type { FileMeta } from '../types'

type AppState = {
	files: FileMeta[]
	selectedFile: FileMeta | null
	setFiles: (files: FileMeta[]) => void
	selectFile: (file: FileMeta) => void
}

export const useAppStore = create<AppState>(set => ({
	files: [],
	selectedFile: null,
	setFiles: files => set({ files }),
	selectFile: file => set({ selectedFile: file }),
}))
