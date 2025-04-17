import React, { useEffect, useState } from 'react'
import { getFiles, uploadFile, isIndexed, deleteFile } from '../api/api'
import FileList from '../components/FileList'
import { PDFViewer } from '../components/PdfViewer'
import Chat from '../components/Chat'

import type { FileMeta } from '../types'


const Home = () => {
	const [files, setFiles] = useState<FileMeta[]>([])
	const [selectedFile, setSelectedFile] = useState<FileMeta | null>(null)
	const [uploading, setUploading] = useState<boolean>(false)

    const fetchFiles = async () => {
		const files = await getFiles()
		setFiles(files)
	}
    
	useEffect(() => {
		fetchFiles()
	}, [])

	const handleFileUpload = async (
		event: React.ChangeEvent<HTMLInputElement>
	) => {
		if (event.target.files?.length) {
			const files = Array.from(event.target.files)
			setUploading(true)
			try {
				const uploadedFile = await uploadFile(files)
			} catch (error) {
				console.error('Error uploading file:', error)
			} finally {
				setUploading(false)
                await fetchFiles()
			}
		}
        event.target.value = ''
	}

    const handleDeleteFile = async (fileId: string) => {
		try {
			const success = await deleteFile(fileId)
			if (success) {
				setFiles(prev => prev.filter(file => file.file_id !== fileId))
				if (selectedFile && selectedFile.file_id === fileId) setSelectedFile(null)
			}
		} catch (error) {
			console.error('Error deleting file:', error)
		}
	}

	return (
		<div className='grid grid-cols-[1fr_2fr_1fr]'>
			<div className='pl-3 pt-3'>
				<p className='text-2xl'>Files</p>
				{files.length === 0 ? (
					<p>No files available.</p>
				) : (
					<FileList
						files={files}
						onSelectFile={setSelectedFile}
						onDeleteFile={handleDeleteFile}
					/>
				)}
				<div>
					<input type='file' onChange={handleFileUpload} />
				</div>

				{uploading && <p>Uploading...</p>}
			</div>

			<div className='h-screen'>
				{selectedFile && <PDFViewer meta={selectedFile} />}
			</div>

			<div className='h-screen '>
				{selectedFile && <Chat file_meta={selectedFile} />}
			</div>
		</div>
	)
}

export default Home
