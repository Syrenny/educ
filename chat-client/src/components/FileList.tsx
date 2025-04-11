import React from 'react'

interface FileListProps {
	files: { filename: string; file_id: string }[]
	onSelectFile: (fileId: string) => void
}

const FileList: React.FC<FileListProps> = ({ files, onSelectFile }) => {
	return (
		<div>
			{files.map(file => (
				<div
					key={file.file_id}
					onClick={() => onSelectFile(file.file_id)}
					style={{ cursor: 'pointer', marginBottom: '10px' }}
				>
					{file.filename}
				</div>
			))}
		</div>
	)
}

export default FileList
