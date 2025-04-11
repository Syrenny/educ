import React, { useEffect, useState } from 'react'
import { getFiles, uploadFile } from '../api/api'
import FileList from '../components/FileList'
import Chat from '../components/Chat'

interface File {
	filename: string
	file_id: string
}

const Home = () => {
	const [files, setFiles] = useState<File[]>([])
	const [selectedFile, setSelectedFile] = useState<string | null>(null)
	const [uploading, setUploading] = useState<boolean>(false)

	useEffect(() => {
		const fetchFiles = async () => {
			const files = await getFiles()
			setFiles(files)
		}
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
				setFiles(prevFiles => [...prevFiles, uploadedFile])
			} catch (error) {
				console.error('Error uploading file:', error)
			} finally {
				setUploading(false)
			}
		}
	}

	return (
		<div className='flex'>
			<div className='w-1/4'>
				<h2>Files</h2>
				{files.length === 0 ? (
					<p>No files available.</p>
				) : (
					<FileList files={files} onSelectFile={setSelectedFile} />
				)}
				<input type='file' onChange={handleFileUpload} />
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
