import React, { useEffect, useState } from 'react'
import { deleteFile, getFiles, uploadFile } from '../api/api'
import FileList from '../components/FileList'
import { PDFViewer } from '../components/PdfViewer'
import Chat from '../components/chat/ChatWindow'
import { useParams, useNavigate } from 'react-router-dom'
import IconPaperClip from '../components/icons/IconPaperClip'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

import type { FileMeta, Shortcut } from '../types'

const Home = () => {
    const { file_id } = useParams()
	const navigate = useNavigate()

	const [files, setFiles] = useState<FileMeta[]>([])

	const selectedFile = files.find(file => file.file_id === file_id) || null

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
				if (selectedFile && selectedFile.file_id === fileId)
                    navigate(`/`)
			}
		} catch (error) {
			console.error('Error deleting file:', error)
		}
	}

	return (
		<div className='flex'>
			<ToastContainer position='top-right' autoClose={3000} />
			<div className='pl-3 pt-3 max-w-[250px] w-[250px]'>
				<div className='flex'>
					<h4 className='mb-1.5 mt-4 pl-0.5 text-3xl text-gray-400 first:mt-0 dark:text-gray-500'>
						Files
					</h4>
					<label className='base-tool relative flex justify-center items-center text-gray-100 ml-4 text-3xl cursor-pointer ml-auto mr-5'>
						<input
							disabled={uploading}
							className='absolute hidden size-0'
							aria-label='Upload file'
							type='file'
							onChange={handleFileUpload}
							accept='.pdf'
						/>
						<IconPaperClip classNames='text-2xl justify-self-center ' />
					</label>
				</div>

				{files.length === 0 ? (
					<p>No files available.</p>
				) : (
					<FileList files={files} onDeleteFile={handleDeleteFile} />
				)}

				{uploading && <p>Uploading...</p>}
			</div>

			<div className='h-screen flex-grow'>
				{selectedFile && <PDFViewer meta={selectedFile}/>}
			</div>

			<div className='h-screen w-[600px]'>
				{selectedFile && <Chat file_meta={selectedFile} />}
			</div>
		</div>
	)
}

export default Home
