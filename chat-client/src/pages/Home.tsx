import React, { useEffect, useState } from 'react'
import { getFiles, uploadFile } from '../api/api'
import FileList from '../components/FileList'
import Chat from '../components/Chat'

import type { FileMeta } from '../types'


const Home = () => {
	const [files, setFiles] = useState<FileMeta[]>([])
	const [selectedFile, setSelectedFile] = useState<string | null>(null)
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

	return (
		<div className='flex'>
			<div className='w-1/4'>
				<h1>Files</h1>
				{files.length === 0 ? (
					<p>No files available.</p>
				) : (
					<FileList files={files} onSelectFile={setSelectedFile} />
				)}
				<div>
					<input type='file' onChange={handleFileUpload} />
				</div>

				{uploading && <p>Uploading...</p>}
			</div>

			<div className='flex-grow'>
				{/* {selectedFile && <PDFViewer fileId={selectedFile} />} */}
			</div>

			<div className='w-1/4'>
				{/* {selectedFile && <Chat fileId={selectedFile} />} */}
			</div>
		</div>
	)
}

export default Home
