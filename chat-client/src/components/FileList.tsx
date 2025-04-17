import React from 'react'
import type { FileMeta } from '../types'

interface FileListProps {
	files: FileMeta[]
	onDeleteFile: (fileId: string) => void
	onSelectFile: (fileMeta: FileMeta) => void
}

const FileList: React.FC<FileListProps> = ({
	files,
	onSelectFile,
	onDeleteFile,
}) => {
	return (
		<div className='pl-2'>
			{files.map(file => (
				<div
					key={file.file_id}
					onClick={() => onSelectFile(file)}
					className='text-gray-500 hover:text-gray-700 transition-colors duration-150 p-1 rounded hover:bg-gray-100 mr-4 cursor-pointer'
				>
					<button
						onClick={e => {
							e.stopPropagation()
							onDeleteFile(file.file_id)
						}}
						className='text-red-500 hover:text-red-700 transition-colors duration-150 p-1 rounded hover:bg-red-100 mr-4 w-8'
					>
						X
					</button>
					{file.filename}
					{file.is_indexed === false && <span>(Индексация...)</span>}
				</div>
			))}
		</div>
	)
}

export default FileList
