import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'

import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'

import React, { useEffect, useState } from 'react'
import { getURL } from '../../api/api'
import type { FileMeta } from '../../types'
import { PDFContextMenu } from './PdfContextMenu'

interface PDFViewerProps {
	meta: FileMeta
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ meta }) => {
	const [pdfUrl, setPdfUrl] = useState<string>('')
	const defaultLayoutPluginInstance = defaultLayoutPlugin()

	useEffect(() => {
		const fetchURL = async () => {
			const url = await getURL(meta.file_id)
			setPdfUrl(url)
		}

		fetchURL()
	}, [meta])

	return (
		<div className='h-full w-full '>
			{pdfUrl && (
				<Worker workerUrl='https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'>
					<PDFContextMenu />
					<Viewer
						theme={{ theme: 'auto' }}
						fileUrl={pdfUrl}
						plugins={[defaultLayoutPluginInstance]}
                        defaultScale={1.1}
					/>
				</Worker>
			)}
		</div>
	)
}
