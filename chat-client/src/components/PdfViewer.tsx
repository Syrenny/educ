import React, { useEffect } from 'react'

interface PDFViewerProps {
	fileId: string
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ fileId }) => {
	useEffect(() => {
		// Логика для загрузки и рендеринга PDF
		const loadPDF = async () => {
			// Здесь можно использовать библиотеку pdf.js или создать собственное решение
			// Для начала выводим простой текст
			console.log('Loading PDF with fileId:', fileId)
		}

		loadPDF()
	}, [fileId])

	return (
		<div>
			{/* Вставь сюда компонент для отображения PDF */}
			<p>PDF Viewer for {fileId}</p>
		</div>
	)
}
