import React, { useEffect, useState } from 'react'
import { getFiles } from '../api/api'
import FileList from '../components/FileList'
import Chat from '../components/Chat'

const Home = () => {
	const [files, setFiles] = useState<any[]>([])
	const [selectedFile, setSelectedFile] = useState<string | null>(null)

	useEffect(() => {
		const fetchFiles = async () => {
			const files = await getFiles()
			setFiles(files)
		}
		fetchFiles()
	}, [])

	return (
		<div className='flex'>
			<FileList files={files} onSelectFile={setSelectedFile} />
			<div className='flex-grow'>
				{/* {selectedFile && <PdfViewer fileId={selectedFile} />} */}
			</div>
			<div className='w-1/4'>
				{selectedFile && <Chat fileId={selectedFile} />}
			</div>
		</div>
	)
}

export default Home
