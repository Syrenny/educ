import React from 'react'
import type { FileMeta } from '../types'
import FileItem from './FileItem'

interface FileListProps {
	files: FileMeta[]
	onDeleteFile: (fileId: string) => void
}

const FileList: React.FC<FileListProps> = ({
	files,
	onDeleteFile,
}) => {
	return (
		<div className='scrollbar-custom flex touch-pan-y flex-col gap-1 overflow-y-auto rounded-r-xl from-gray-50 px-3 pb-3 pt-2 text-[.9rem] dark:from-gray-800/30 max-sm:bg-gradient-to-t md:bg-gradient-to-l'>
			<div className='flex flex-col gap-1'>
				{files.map((file, index) => (
					<FileItem 
                    key={index}
                    onDeleteFile={onDeleteFile}
                    file={file}
                    />
				))}
			</div>
		</div>
	)
}

export default FileList
