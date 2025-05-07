import React, { useState } from 'react'
import type { FileMeta } from '../types'
import { useParams } from 'react-router-dom'

interface FileItemProps {
    file: FileMeta
    onDeleteFile: (fileId: string) => void
}

const FileItem: React.FC<FileItemProps> = ({
    file,
    onDeleteFile,
}) => {
    const { file_id } = useParams()
    const [confirmDelete, setConfirmDelete] = useState(false)
    return (
		<a
			href={`/c/${file.file_id}`}
			className={`group flex h-10 flex-none items-center gap-1.5 rounded-lg pl-2.5 pr-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 sm:h-[2.35rem] 
            ${
				file.file_id === file_id
					? 'bg-gray-100 dark:bg-gray-700'
					: ''
			}`}
		>
			<div className='flex flex-1 items-center truncate'>
				{confirmDelete && (
					<span className='mr-1 font-semibold'> Delete </span>
				)}
				{file.filename}
			</div>
			{confirmDelete ? (
				<div>
					<button
						type='button'
						className='flex h-5 w-5 items-center justify-center rounded md:hidden md:group-hover:flex'
						title='Cancel delete action'
						onClick={e => {
							e.preventDefault()
							setConfirmDelete(false)
						}}
					>
						{/* <CarbonClose class='text-xs text-gray-400 hover:text-gray-500 dark:hover:text-gray-300' /> */}
						N
					</button>
					<button
						type='button'
						className='flex h-5 w-5 items-center justify-center rounded md:hidden md:group-hover:flex'
						title='Confirm delete action'
						onClick={e => {
							e.preventDefault()
							setConfirmDelete(false)
							onDeleteFile(file.file_id)
						}}
					>
						{/* <CarbonCheckmark class='text-xs text-gray-400 hover:text-gray-500 dark:hover:text-gray-300' /> */}
						Y
					</button>
				</div>
			) : (
				<div>
					<button
						type='button'
						className='flex h-5 w-5 items-center justify-center rounded md:hidden md:group-hover:flex'
						title='Delete conversation'
						onClick={event => {
							event.preventDefault()
							if (event.shiftKey) {
								onDeleteFile(file.file_id)
							} else {
								setConfirmDelete(true)
							}
						}}
					>
						{/* <CarbonTrashCan class='text-xs text-gray-400  hover:text-gray-500 dark:hover:text-gray-300' /> */}
                        D
					</button>
				</div>
			)}
		</a>
	)
}

export default FileItem
