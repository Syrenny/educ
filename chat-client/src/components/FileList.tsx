interface FileListProps {
	files: any[]
	onSelectFile: (fileId: string) => void
}

const FileList = ({ files, onSelectFile }: FileListProps) => {
	return (
		<div className='w-1/4 p-4'>
			<ul>
				{files.map(file => (
					<li
						key={file.file_id}
						onClick={() => onSelectFile(file.file_id)}
						className='cursor-pointer'
					>
						{file.filename}
					</li>
				))}
			</ul>
		</div>
	)
}

export default FileList
