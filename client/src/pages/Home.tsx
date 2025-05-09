import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { deleteFile, getFiles, uploadFile } from '../api/api'
import Chat from '../components/chat/ChatWindow'
import FileList from '../components/FileList'
import IconPaperClip from '../components/icons/IconPaperClip'
import { PDFViewer } from '../components/viewer/PdfViewer'

import { useAuth } from '../context/AuthContext'
import type { FileMeta } from '../types'

const Home = () => {
	const { file_id } = useParams()
	const { user, logout } = useAuth()
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
			<div className='pl-3 pt-3 w-full max-w-[230px] text-gray-700 dark:text-gray-300 select-none flex flex-col'>
				<div className='flex'>
					<h4 className='mb-1.5 mt-4 pl-0.5 text-2xl first:mt-0'>
						Файлы
					</h4>
					<label className='base-tool relative flex justify-center items-center text-gray-100 ml-auto text-3xl cursor-pointer mr-5'>
						<input
							disabled={uploading}
							className='absolute hidden size-0'
							aria-label='Upload file'
							type='file'
							onChange={handleFileUpload}
							accept='.pdf'
						/>
						<IconPaperClip classNames='text-xl justify-self-center text-gray-500 dark:text-gray-100' />
					</label>
				</div>

				{files.length === 0 && !uploading ? (
					<h4 className='text-center text-sm mr-2first:mt-0 mt-4'></h4>
				) : (
					<FileList files={files} onDeleteFile={handleDeleteFile} />
				)}

				{uploading && (
					<div className='flex justify-center items-center mb-1.5 mt-4 pl-0.5'>
						<h4 className='text-sm mr-2 first:mt-'>Загрузка</h4>
						<svg
							aria-hidden='true'
							className='w-3 h-3 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600'
							viewBox='0 0 100 101'
							fill='none'
							xmlns='http://www.w3.org/2000/svg'
						>
							<path
								d='M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z'
								fill='currentColor'
							/>
							<path
								d='M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z'
								fill='currentFill'
							/>
						</svg>
					</div>
				)}
				<form
					onSubmit={async event => {
						event.preventDefault()
						await logout()
						navigate('/login')
					}}
					className='mt-auto mb-8 group flex items-center gap-1.5 rounded-lg pl-2.5 pr-2 hover:bg-gray-100 dark:hover:bg-gray-700'
				>
					<span className='flex h-9 flex-none shrink items-center gap-1.5 truncate pr-2 text-gray-500 dark:text-gray-400'>
						{user?.email}
					</span>
					<button
						type='submit'
						className='ml-auto h-6 flex-none items-center gap-1.5 rounded-md border bg-white px-2 text-gray-700 shadow-sm group-hover:flex hover:shadow-none dark:border-gray-600 dark:bg-gray-600 dark:text-gray-400 dark:hover:text-gray-300 hidden'
					>
						Sign Out
					</button>
				</form>
			</div>

			<div className='h-screen flex-grow w-full'>
				{selectedFile && <PDFViewer meta={selectedFile} />}
			</div>

			<div className='w-full lg:max-w-[600px] md:max-w-[300px] h-screen '>
				{selectedFile && <Chat file_meta={selectedFile} />}
			</div>
		</div>
	)
}

export default Home
