import React, { useEffect, useState } from 'react'
import { getURL } from '../api/api'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import type { FileMeta } from '../types'


interface PDFViewerProps {
	meta: FileMeta
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ meta }) => {
	const [pdfUrl, setPdfUrl] = useState<string>("")

	useEffect(() => {
        const fetchURL = async () => {
            const url = await getURL(meta.file_id)
            setPdfUrl(url)
        }

		fetchURL()
	}, [meta])

	const viewerUrl = `/pdfjs/web/viewer.html?file=${encodeURIComponent(pdfUrl)}`

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
