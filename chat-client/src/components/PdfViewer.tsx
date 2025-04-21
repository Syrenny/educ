import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import React, { useEffect, useState } from 'react'
import { getURL } from '../api/api'
import { useAction } from '../context/ActionContext'
import type { FileMeta } from '../types'

interface PDFViewerProps {
	meta: FileMeta
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ meta }) => {
	const [pdfUrl, setPdfUrl] = useState<string>('')
	const { setAction, setSnippet } = useAction()

	useEffect(() => {
		const fetchURL = async () => {
			const url = await getURL(meta.file_id)
			setPdfUrl(url)
		}

		fetchURL()
	}, [meta])

	useEffect(() => {
		const handleMessage = (event: MessageEvent) => {
			if (event.origin !== window.location.origin) return

			const { type, action, text } = event.data || {}
			if (type === 'pdf-user-action') {
				setSnippet(text)
                setAction(action)
			}
		}

		window.addEventListener('message', handleMessage)
		return () => window.removeEventListener('message', handleMessage)
	}, [])

	const viewerUrl = `/pdfjs/web/viewer.html?file=${encodeURIComponent(
		pdfUrl
	)}`

	return (
		<iframe
			src={viewerUrl}
			width='100%'
			height='1000px'
			className='h-full w-full'
			title='PDF Viewer'
		/>
	)
}
